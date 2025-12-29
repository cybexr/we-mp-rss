from logging import info
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session
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
from driver.wxarticle import WXArticleFetcher
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
    session = DB.get_session()
    try:
        result = search_Biz(kw,limit=limit,offset=offset)
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
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    try:
        from core.models.feed import Feed
        query = session.query(Feed)
        if kw:
            query = query.filter(Feed.mp_name.ilike(f"%{kw}%"))
        if category:
            query = query.filter(Feed.category == category)
        total = query.count()
        mps = query.order_by(Feed.created_at.desc()).limit(limit).offset(offset).all()
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
    session = DB.get_session()
    try:
        from core.models.feed import Feed
        categories = session.query(Feed.category)\
            .filter(Feed.category.isnot(None))\
            .filter(Feed.category != '')\
            .distinct()\
            .order_by(Feed.category.asc())\
            .all()

        category_list = [c[0] for c in categories]
        return success_response({
            'categories': category_list
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
    finally:
        session.close()

@router.get("/update/{mp_id}", summary="更新公众号文章")
async def update_mps(
     mp_id: str,
     background_tasks: BackgroundTasks,
     start_page: int = 0,
     end_page: int = 1,
    current_user: dict = Depends(get_current_user)
):
    session = DB.get_session()
    try:
        from core.models.feed import Feed
        mp = session.query(Feed).filter(Feed.id == mp_id).first()
        if not mp:
           return error_response(
                    code=40401,
                    message="请选择一个公众号"
                )
        import time
        sync_interval=cfg.get("sync_interval",60)
        if mp.update_time is None:
            mp.update_time=int(time.time())-sync_interval
        time_span=int(time.time())-int(mp.update_time)
        if time_span<sync_interval:
           return error_response(
                    code=40402,
                    message="请不要频繁更新操作",
                    data={"time_span":time_span}
                )
        result=[]
        def UpArt(mp):
            from core.wx import WxGather
            wx=WxGather().Model()
            wx.get_Articles(mp.faker_id,Mps_id=mp.id,Mps_title=mp.mp_name,CallBack=UpdateArticle,start_page=start_page,MaxPage=end_page)
            result=wx.articles
        background_tasks.add_task(UpArt, mp)
        return success_response({
            "time_span":time_span,
            "list":result,
            "total":len(result),
            "mps":mp
        })
    except Exception as e:
        print(f"更新公众号文章: {str(e)}",e)
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
    session = DB.get_session()
    try:
        from core.models.feed import Feed
        mp = session.query(Feed).filter(Feed.id == mp_id).first()
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
        info =await WXArticleFetcher().async_get_article_content(url)

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
    session = DB.get_session()
    try:
        from core.models.feed import Feed
        import time
        now = datetime.now()
        
        import base64
        mpx_id = base64.b64decode(mp_id).decode("utf-8")
        local_avatar_path = f"{save_avatar_locally(avatar)}"
        
        # 检查公众号是否已存在
        existing_feed = session.query(Feed).filter(Feed.faker_id == mp_id).first()
        
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
           
        session.commit()
        
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
        session.rollback()
        print(f"添加公众号错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message="添加公众号失败"
            )
        )




@router.put("/{mp_id}", summary="更新公众号信息")
async def update_mp(
    mp_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    session = DB.get_session()
    try:
        from core.models.feed import Feed

        mp = session.query(Feed).filter(Feed.id == mp_id).first()
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
        session.commit()

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
        session.rollback()
        print(f"更新公众号信息错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message="更新公众号信息失败"
            )
        )
    finally:
        session.close()

@router.delete("/{mp_id}", summary="删除订阅号")
async def delete_mp(
    mp_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = DB.get_session()
    try:
        from core.models.feed import Feed
        mp = session.query(Feed).filter(Feed.id == mp_id).first()
        if not mp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(
                    code=40401,
                    message="订阅号不存在"
                )
            )

        session.delete(mp)
        session.commit()
        return success_response({
            "message": "订阅号删除成功",
            "id": mp_id
        })
    except Exception as e:
        session.rollback()
        print(f"删除订阅号错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message="删除订阅号失败"
            )
        )

@router.put("/batch-category", summary="批量更新公众号分类")
async def batch_update_category(
    mp_ids: List[str] = Body(..., min_items=1, max_items=100),
    category: str = Body(..., min_length=1, max_length=255),
    current_user: dict = Depends(get_current_user)
):
    session = DB.get_session()
    try:
        from core.models.feed import Feed

        mps = session.query(Feed).filter(Feed.id.in_(mp_ids)).all()

        if not mps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(
                    code=40401,
                    message="未找到任何公众号"
                )
            )

        updated_count = 0
        for mp in mps:
            mp.category = category
            mp.updated_at = datetime.now()
            updated_count += 1

        session.commit()

        return success_response({
            "updated_count": updated_count
        })
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"批量更新分类错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                code=50001,
                message="批量更新分类失败"
            )
        )
    finally:
        session.close()

