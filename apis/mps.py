from logging import info
from typing import Optional, List
from core.log import logger
from core.print import print_error
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from core.auth import get_current_user
from core.db import DB
from core.wx import search_Biz
from driver.wx import Wx
from .base import success_response, error_response
from datetime import datetime
from core.config import cfg
from core.res import save_avatar_locally
import io
import os
from jobs.article import UpdateArticle
router = APIRouter(prefix=f"/mps", tags=["公众号管理"])

# Database session dependency
def get_db():
    """FastAPI dependency for database session management"""
    db_session = DB.get_session()
    try:
        yield db_session
    finally:
        db_session.close()
# import core.db as db
# UPDB=db.Db("数据抓取")
# def UpdateArticle(art:dict):
#             return UPDB.add_article(art)


@router.get("/search/{kw}", summary="搜索公众号")
async def search_mp(
    kw: str = "",
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Run blocking search_Biz in thread pool executor to avoid blocking event loop
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,  # Use default thread pool executor
            lambda: search_Biz(kw, limit=limit, offset=offset)
        )
        data={
            'list':result.get('list') if result is not None else [],
            'page':{
                'limit':limit,
                'offset':offset
            },
            'total':result.get('total') if result is not None else 0
        }
        return success_response(data)
    except Exception as e:
        print(f"搜索公众号错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message=f"搜索公众号失败,请重新扫码授权！",
            )
        )

@router.get("", summary="获取公众号列表")
async def get_mps(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    kw: str = Query(""),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("created_at", description="Sort column: last_publish_time, article_count, created_at, mp_name"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取公众号列表，包含文章统计和最后发布时间。

    Returns:
        - last_publish_time: 最后一次文章发布时间 (ISO format 或 null)
        - article_count: 该公众号的文章总数 (integer, 0 if no articles)
    """
    def format_timestamp(timestamp):
        """格式化时间戳为ISO格式，处理0或None的情况"""
        if timestamp and timestamp > 0:
            return datetime.fromtimestamp(timestamp).isoformat()
        return None

    try:
        from core.models.feed import Feed
        from core.models.article import Article

        # Use async database session instead of sync session
        async with DB.async_session_factory() as session:
            # Build query with LEFT JOIN to Article table for counting and last publish time
            stmt = select(
                Feed,
                func.count(Article.id).label('article_count'),
                func.max(Article.publish_time).label('last_publish_time')
            ).outerjoin(
                Article, Article.mp_id == Feed.id
            ).group_by(
                Feed.id
            )

            if kw:
                stmt = stmt.where(Feed.mp_name.ilike(f"%{kw}%"))
            if category is not None:
                stmt = stmt.where(Feed.category == category)

            # Get total count (count distinct feeds, not article groups)
            count_stmt = select(func.count()).select_from(Feed)
            if kw:
                count_stmt = count_stmt.where(Feed.mp_name.ilike(f"%{kw}%"))
            if category is not None:
                count_stmt = count_stmt.where(Feed.category == category)

            total_result = await session.execute(count_stmt)
            total = total_result.scalar()

            # Apply sorting based on sort_by parameter
            sort_column_map = {
                'last_publish_time': func.max(Article.publish_time),
                'article_count': func.count(Article.id),
                'created_at': Feed.created_at,
                'mp_name': Feed.mp_name
            }

            # Default to created_at if invalid sort_by
            sort_column = sort_column_map.get(sort_by, Feed.created_at)

            # Apply sort order with null handling for last_publish_time
            if sort_order.lower() == 'asc':
                if sort_by == 'last_publish_time':
                    stmt = stmt.order_by(sort_column.asc().nullsfirst())
                else:
                    stmt = stmt.order_by(sort_column.asc())
            else:  # desc
                if sort_by == 'last_publish_time':
                    stmt = stmt.order_by(sort_column.desc().nullslast())
                else:
                    stmt = stmt.order_by(sort_column.desc())

            # Get paginated results
            stmt = stmt.limit(limit).offset(offset)
            result = await session.execute(stmt)
            rows = result.all()

            # Process results: each row is (Feed, article_count, last_publish_time)
            return success_response({
                "list": [{
                    "id": feed.id,
                    "mp_name": feed.mp_name,
                    "mp_cover": feed.mp_cover,
                    "mp_intro": feed.mp_intro,
                    "status": feed.status,
                    "cache_images": feed.cache_images,
                    "remarks": feed.remarks,
                    "category": feed.category,
                    "last_publish_time": format_timestamp(last_publish_time),
                    "article_count": article_count or 0,
                    "created_at": feed.created_at.isoformat()
                } for feed, article_count, last_publish_time in rows],
                "page": {
                    "limit": limit,
                    "offset": offset,
                    "total": total
                },
                "total": total
            })
    except Exception as e:
        print(f"获取公众号列表错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message="获取公众号列表失败"
            )
        )

@router.get("/categories", summary="获取公众号分类列表")
async def get_categories(
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            result = await session.execute(
                select(Feed.category)
                .where(Feed.category.isnot(None))
                .where(Feed.category != '')
                .distinct()
                .order_by(Feed.category.asc())
            )
            categories = result.scalars().all()

            return success_response({
                'categories': categories
            })
        except Exception as e:
            print(f"获取分类列表错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="获取分类列表失败"
                )
            )

@router.get("/update/{mp_id}", summary="更新公众号文章")
async def update_mps(
     mp_id: str,
     start_page: int = 0,
     end_page: int = 1,
    current_user: dict = Depends(get_current_user)
):
    """
    更新指定公众号的文章列表。

    此接口将文章更新任务提交到后台队列，立即返回任务ID用于状态查询。
    更新操作受频率限制保护，默认间隔30秒。

    Args:
        mp_id: 公众号ID
        start_page: 起始页码，默认0
        end_page: 结束页码，默认1（实际会获取 end_page 页的文章）

    Returns:
        包含以下字段的响应:
        - job_id: 后台任务ID，用于轮询任务状态
        - status: 任务状态 (queued/running/completed/failed)
        - mp_id: 公众号ID
        - message: 提示信息

    Raises:
        404: 公众号不存在
        400: 更新过于频繁
        500: 服务器内部错误
    """
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            from core.wx import WxGather
            from core.queue import TaskQueue

            result = await session.execute(
                select(Feed).where(Feed.id == mp_id)
            )
            mp = result.scalars().first()
            if not mp:
               return error_response(
                        code=40401,
                        message="请选择一个公众号"
                    )

            import time
            # Allow manual refresh every 30 seconds
            sync_interval=cfg.get("sync_interval",30)
            if mp.update_time is None:
                mp.update_time=int(time.time())-sync_interval
            time_span=int(time.time())-int(mp.update_time)

            if time_span<sync_interval:
               return error_response(
                        code=40402,
                        message="请不要频繁更新操作",
                        data={"time_span":time_span}
                    )

            # 更新公众号的最后更新时间（提交任务前更新，避免重复提交）
            mp.update_time = int(time.time())
            await session.commit()

            # Generate unique job_id for this refresh task
            job_id = f'refresh_{mp_id}_{int(time.time())}'

            # 提交文章更新任务到后台队列（非阻塞）
            TaskQueue.add_task(
                WxGather().Model().get_Articles,
                faker_id=mp.faker_id,
                Mps_id=mp.id,
                Mps_title=mp.mp_name,
                CallBack=UpdateArticle,
                start_page=start_page,
                MaxPage=end_page,
                job_id=job_id
            )

            # 立即返回任务ID，不等待任务完成
            return success_response({
                "job_id": job_id,
                "status": "queued",
                "mp_id": mp.id,
                "message": "文章更新任务已提交到后台队列，请使用job_id查询进度"
            })
        except Exception as e:
            print_error(f"更新公众号文章: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message=f"更新公众号文章{str(e)}"
                )
            )

@router.get("/jobs/{job_id}", summary="查询公众号文章更新任务状态")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    查询指定公众号文章更新任务的状态和进度。

    Args:
        job_id: 任务ID，由 update_mps 接口返回

    Returns:
        包含以下字段的响应:
        - job_id: 任务ID
        - status: 任务状态 (queued/running/completed/failed)
        - created_at: 任务创建时间
        - updated_at: 任务更新时间
        - task_name: 任务名称
        - progress: 进度百分比 (0-100)
        - error: 错误信息（仅失败时有值）

    Raises:
        404: 任务不存在
        500: 服务器内部错误
    """
    try:
        from core.queue import TaskQueue

        # 查询任务状态
        job_status = TaskQueue.get_status(job_id)

        if not job_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(
                    code=40401,
                    message=f"任务不存在: {job_id}"
                )
            )

        # 返回任务状态信息
        return success_response({
            "job_id": job_id,
            "status": job_status['status'],
            "created_at": job_status['created_at'],
            "updated_at": job_status['updated_at'],
            "task_name": job_status['task_name'],
            "progress": job_status['progress'],
            "error": job_status.get('error')
        })
    except HTTPException:
        raise
    except Exception as e:
        print_error(f"查询任务状态错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message=f"查询任务状态失败: {str(e)}"
            )
        )

@router.get("/{mp_id}", summary="获取公众号详情")
async def get_mp(
    mp_id: str,
    # current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            result = await session.execute(
                select(Feed).where(Feed.id == mp_id)
            )
            mp = result.scalars().first()
            if not mp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="公众号不存在"
                    )
                )
            return success_response({
                "id": mp.id,
                "mp_name": mp.mp_name,
                "mp_cover": mp.mp_cover,
                "mp_intro": mp.mp_intro,
                "status": mp.status,
                "cache_images": mp.cache_images,
                "remarks": mp.remarks,
                "category": mp.category,
                "created_at": mp.created_at.isoformat()
            })
        except Exception as e:
            print(f"获取公众号详情错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="获取公众号详情失败"
                )
            )
@router.post("/by_article", summary="通过文章链接获取公众号详情")
async def get_mp_by_article(
    url: str=Query(..., min_length=1),
    current_user: dict = Depends(get_current_user)
):
    try:
        # 使用BrowserManager进行浏览器复用和重试 (异步)
        from driver.browser_manager import BrowserManager

        async with BrowserManager(max_articles_per_browser=1, max_retries=3) as browser_mgr:
            info = await browser_mgr.fetch_article(url, mobile_mode=False)

        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(
                    code=40401,
                    message="公众号不存在"
                )
            )
        return success_response(info)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取公众号详情错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                code=40001,
                message="请输入正确的公众号文章链接"
            )
        )

@router.post("", summary="添加公众号")
async def add_mp(
    mp_name: str = Body(..., min_length=1, max_length=255),
    mp_cover: str = Body(None, max_length=255),
    mp_id: str = Body(None, max_length=255),
    avatar: str = Body(None, max_length=500),
    mp_intro: str = Body(None, max_length=255),
    cache_images: bool = Body(False),
    remarks: str = Body(''),
    category: str = Body(''),
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            import time
            now = datetime.now()

            import base64
            mpx_id = base64.b64decode(mp_id).decode("utf-8")
            local_avatar_path = f"{save_avatar_locally(avatar)}"

            # 检查公众号是否已存在
            result = await session.execute(
                select(Feed).where(Feed.faker_id == mp_id)
            )
            existing_feed = result.scalars().first()

            if existing_feed:
                # 更新现有记录
                existing_feed.mp_name = mp_name
                existing_feed.mp_cover = local_avatar_path
                existing_feed.mp_intro = mp_intro
                existing_feed.cache_images = cache_images
                existing_feed.remarks = remarks
                existing_feed.category = category
                existing_feed.updated_at = now
            else:
                # 创建新的Feed记录
                new_feed = Feed(
                    id=f"MP_WXS_{mpx_id}",
                    mp_name=mp_name,
                    mp_cover= local_avatar_path,
                    mp_intro=mp_intro,
                    status=1,  # 默认启用状态
                    created_at=now,
                    updated_at=now,
                    faker_id=mp_id,
                    update_time=0,
                    sync_time=0,
                    cache_images=cache_images,
                    remarks=remarks,
                    category=category,
                )
                session.add(new_feed)

            await session.commit()

            feed = existing_feed if existing_feed else new_feed
             #在这里实现第一次添加获取公众号文章
            if not existing_feed:
                from core.queue import TaskQueue
                from core.wx import WxGather
                Max_page=int(cfg.get("max_page","2"))
                TaskQueue.add_task( WxGather().Model().get_Articles,faker_id=feed.faker_id,Mps_id=feed.id,CallBack=UpdateArticle,MaxPage=Max_page,Mps_title=mp_name)

            return success_response({
                "id": feed.id,
                "mp_name": feed.mp_name,
                "mp_cover": feed.mp_cover,
                "mp_intro": feed.mp_intro,
                "status": feed.status,
                "faker_id":mp_id,
                "created_at": feed.created_at.isoformat()
            })
        except Exception as e:
            await session.rollback()
            print(f"添加公众号错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="添加公众号失败"
                )
            )

@router.put("/batch-category", summary="批量更新公众号分类")
async def batch_update_category(
    mp_ids: List[str] = Body(..., min_items=1, max_items=100),
    category: str = Body(..., min_length=1, max_length=255),
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed

            logger.info(f"批量更新分类 - mp_ids: {mp_ids}, category: {category}")

            # 直接通过 id 查询
            result = await session.execute(
                select(Feed).where(Feed.id.in_(mp_ids))
            )
            mps = result.scalars().all()

            if not mps:
                logger.warning(f"公众号不存在，未找到以下ID: {mp_ids[:3]}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message=f"公众号不存在，未找到以下ID: {mp_ids[:3]}{'...' if len(mp_ids) > 3 else ''}"
                    )
                )

            logger.info(f"查询到 {len(mps)} 条记录，IDs: {[mp.id for mp in mps]}")

            updated_count = 0
            for mp in mps:
                mp.category = category
                mp.updated_at = datetime.now()
                updated_count += 1

            await session.commit()

            logger.info(f"成功更新 {updated_count} 个公众号的分类为: {category}")

            return success_response({
                "updated_count": updated_count
            })
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"批量更新分类错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="批量更新分类失败"
                )
            )


@router.post("/batch-refresh", summary="批量刷新公众号文章")
async def batch_refresh_mps(
    mp_ids: List[str] = Body(..., min_items=1, max_items=50, description="公众号ID列表"),
    start_page: int = Body(0, ge=0, description="起始页码"),
    end_page: int = Body(1, ge=1, description="结束页码"),
    current_user: dict = Depends(get_current_user)
):
    """
    批量刷新多个公众号的文章。

    对选中的多个公众号提交文章更新任务到后台队列。
    应用频率限制，超出限制的公众号会被跳过。

    Args:
        mp_ids: 公众号ID列表（1-50个）
        start_page: 起始页码
        end_page: 结束页码

    Returns:
        包含以下字段的响应:
        - submitted_count: 已提交任务数
        - rate_limited_count: 因频率限制跳过的数量
        - job_ids: 已提交的任务ID列表
        - rate_limited_mps: 被跳过的公众号ID列表
    """
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            from core.wx import WxGather
            from core.queue import TaskQueue
            from datetime import datetime, timedelta

            # Get sync interval from config (default 30 seconds)
            sync_interval = cfg.get("sync_interval", 30)

            # Query all requested MPs
            result = await session.execute(
                select(Feed).where(Feed.id.in_(mp_ids))
            )
            mps = result.scalars().all()

            if not mps:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="未找到任何公众号"
                    )
                )

            submitted_job_ids = []
            rate_limited_mp_ids = []
            now = datetime.now()

            for mp in mps:
                # Check rate limiting
                if mp.update_time:
                    # Convert Unix timestamp to datetime for proper subtraction
                    from datetime import datetime as dt
                    update_time_dt = dt.fromtimestamp(mp.update_time) if isinstance(mp.update_time, (int, float)) else mp.update_time
                    time_since_update = (now - update_time_dt).total_seconds()
                    if time_since_update < sync_interval:
                        logger.info(f"公众号 {mp.mp_name} 更新过于频繁，跳过（距上次更新 {time_since_update:.0f}秒）")
                        rate_limited_mp_ids.append(mp.id)
                        continue

                # Generate unique job_id for this refresh task
                job_id = f'refresh_{mp.id}_{int(now.timestamp())}'

                # Submit task to queue with correct arguments
                TaskQueue.add_task(
                    WxGather().Model().get_Articles,
                    faker_id=mp.faker_id,
                    Mps_id=mp.id,
                    Mps_title=mp.mp_name,
                    CallBack=UpdateArticle,
                    start_page=start_page,
                    MaxPage=end_page,
                    job_id=job_id
                )

                # Update mp update_time
                mp.update_time = int(now.timestamp())
                submitted_job_ids.append(job_id)
                logger.info(f"已提交批量刷新任务 {job_id} for 公众号 {mp.mp_name}")

            await session.commit()

            logger.info(f"批量刷新完成: 提交 {len(submitted_job_ids)} 个任务, 跳过 {len(rate_limited_mp_ids)} 个")

            return success_response({
                "submitted_count": len(submitted_job_ids),
                "rate_limited_count": len(rate_limited_mp_ids),
                "job_ids": submitted_job_ids,
                "rate_limited_mps": rate_limited_mp_ids
            })

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"批量刷新错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="批量刷新失败"
                )
            )


@router.put("/{mp_id}", summary="更新公众号信息")
async def update_mp(
    mp_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed

            result = await session.execute(
                select(Feed).where(Feed.id == mp_id)
            )
            mp = result.scalars().first()
            if not mp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="公众号不存在"
                    )
                )

            request_json = await request.json()

            if 'cache_images' in request_json:
                cache_images_value = request_json['cache_images']
                if isinstance(cache_images_value, bool):
                    mp.cache_images = cache_images_value
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_response(
                            code=40001,
                            message="cache_images字段必须是布尔类型"
                        )
                    )

            if 'remarks' in request_json:
                remarks_value = request_json['remarks']
                if isinstance(remarks_value, str) and len(remarks_value) <= 255:
                    mp.remarks = remarks_value
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_response(
                            code=40002,
                            message="remarks字段必须是字符串且长度不超过255"
                        )
                    )

            if 'category' in request_json:
                category_value = request_json['category']
                if isinstance(category_value, str) and len(category_value) <= 255:
                    mp.category = category_value
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_response(
                            code=40003,
                            message="category字段必须是字符串且长度不超过255"
                        )
                    )

            mp.updated_at = datetime.now()
            await session.commit()

            return success_response({
                "id": mp.id,
                "mp_name": mp.mp_name,
                "mp_cover": mp.mp_cover,
                "mp_intro": mp.mp_intro,
                "status": mp.status,
                "cache_images": mp.cache_images,
                "remarks": mp.remarks,
                "category": mp.category,
                "created_at": mp.created_at.isoformat(),
                "updated_at": mp.updated_at.isoformat()
            })
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            print(f"更新公众号信息错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="更新公众号信息失败"
                )
            )

@router.delete("/{mp_id}", summary="删除订阅号")
async def delete_mp(
    mp_id: str,
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            result = await session.execute(
                select(Feed).where(Feed.id == mp_id)
            )
            mp = result.scalars().first()
            if not mp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="订阅号不存在"
                    )
                )

            await session.delete(mp)
            await session.commit()
            return success_response({
                "message": "订阅号删除成功",
                "id": mp_id
            })
        except Exception as e:
            await session.rollback()
            print(f"删除订阅号错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message="删除订阅号失败"
                )
            )