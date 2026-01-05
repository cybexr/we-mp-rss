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
    current_user: dict = Depends(get_current_user)
):
    try:
        from core.models.feed import Feed
        # Use async database session instead of sync session
        async with DB.async_session_factory() as session:
            # Build query using SQLAlchemy 2.0 select() syntax
            stmt = select(Feed)
            if kw:
                stmt = stmt.where(Feed.mp_name.ilike(f"%{kw}%"))
            if category is not None:
                stmt = stmt.where(Feed.category == category)

            # Get total count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar()

            # Get paginated results
            stmt = stmt.order_by(Feed.created_at.desc()).limit(limit).offset(offset)
            result = await session.execute(stmt)
            mps = result.scalars().all()

            return success_response({
                "list": [{
                    "id": mp.id,
                    "mp_name": mp.mp_name,
                    "mp_cover": mp.mp_cover,
                    "mp_intro": mp.mp_intro,
                    "status": mp.status,
                    "cache_images": mp.cache_images,
                    "remarks": mp.remarks,
                    "category": mp.category,
                    "created_at": mp.created_at.isoformat()
                } for mp in mps],
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

    此接口会直接同步等待文章更新完成，并返回实际获取到的文章列表。
    更新操作受频率限制保护，默认间隔30秒。

    Args:
        mp_id: 公众号ID
        start_page: 起始页码，默认0
        end_page: 结束页码，默认1（实际会获取 end_page 页的文章）

    Returns:
        包含以下字段的响应:
        - time_span: 距离上次更新的时间间隔（秒）
        - list: 本次更新获取到的文章列表
        - total: 获取到的文章总数
        - mp_id: 公众号ID

    Raises:
        404: 公众号不存在
        400: 更新过于频繁
        500: 服务器内部错误
    """
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            from core.wx import WxGather

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

            # 直接执行文章更新任务（同步等待完成）
            wx=WxGather().Model()
            try:
                await wx.get_Articles(
                    mp.faker_id,
                    Mps_id=mp.id,
                    Mps_title=mp.mp_name,
                    CallBack=UpdateArticle,
                    start_page=start_page,
                    MaxPage=end_page
                )

                # 更新公众号的最后更新时间
                mp.update_time = int(time.time())
                await session.commit()

                # 返回实际获取到的文章列表
                return success_response({
                    "time_span": time_span,
                    "list": wx.articles,
                    "total": len(wx.articles),
                    "mp_id": mp.id
                })
            finally:
                # Explicit cleanup to prevent resource leaks
                await wx.cleanup()
        except Exception as e:
            print_error(f"更新公众号文章: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    code=50001,
                    message=f"更新公众号文章{str(e)}"
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