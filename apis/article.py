from fastapi import APIRouter, Depends, HTTPException, status as fast_status, Query
from core.auth import get_current_user
from core.db import DB
from core.models.base import DATA_STATUS
from core.models.article import Article,ArticleBase
from sqlalchemy import and_, or_, desc, select
from .base import success_response, error_response
from core.config import cfg
from apis.base import format_search_kw
from core.print import print_warning, print_info, print_error, print_success
from core.cache import clear_cache_pattern
from tools.fix import fix_article
router = APIRouter(prefix=f"/articles", tags=["文章管理"])


    
@router.delete("/clean", summary="清理无效文章(MP_ID不存在于Feeds表中的文章)")
async def clean_orphan_articles(
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.feed import Feed
            from core.models.article import Article

            # 找出Articles表中mp_id不在Feeds表中的记录
            subquery = select(Feed.id)
            deleted_count = await session.execute(
                select(Article).where(~Article.mp_id.in_(subquery))
            )
            articles_to_delete = deleted_count.scalars().all()

            for article in articles_to_delete:
                await session.delete(article)

            await session.commit()

            # 清除相关缓存
            clear_cache_pattern("articles_list")
            clear_cache_pattern("home_page")
            clear_cache_pattern("tag_detail")

            return success_response({
                "message": "清理无效文章成功",
                "deleted_count": len(articles_to_delete)
            })
        except Exception as e:
            await session.rollback()
            print(f"清理无效文章错误: {str(e)}")
            raise HTTPException(
                status_code=fast_status.HTTP_201_CREATED,
                detail=error_response(
                    code=50001,
                    message="清理无效文章失败"
                )
            )

@router.put("/{article_id}/read", summary="改变文章阅读状态")
async def toggle_article_read_status(
    article_id: str,
    is_read: bool = Query(..., description="阅读状态: true为已读, false为未读"),
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.article import Article

            # 检查文章是否存在
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalars().first()
            if not article:
                raise HTTPException(
                    status_code=fast_status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="文章不存在"
                    )
                )

            # 更新阅读状态
            article.is_read = 1 if is_read else 0
            await session.commit()

            # 清除相关缓存
            clear_cache_pattern("articles_list")
            clear_cache_pattern("article_detail")
            clear_cache_pattern("tag_detail")

            return success_response({
                "message": f"文章已标记为{'已读' if is_read else '未读'}",
                "is_read": is_read
            })
        except HTTPException as e:
            raise e
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"更新文章阅读状态失败: {str(e)}"
                )
            )
    
@router.delete("/clean_duplicate_articles", summary="清理重复文章")
async def clean_duplicate(
    current_user: dict = Depends(get_current_user)
):
    try:
        from tools.clean import clean_duplicate_articles
        (msg, deleted_count) =clean_duplicate_articles()
        return success_response({
            "message": msg,
            "deleted_count": deleted_count
        })
    except Exception as e:
        print(f"清理重复文章: {str(e)}")
        raise HTTPException(
            status_code=fast_status.HTTP_201_CREATED,
            detail=error_response(
                code=50001,
                message="清理重复文章"
            )
        )


@router.api_route("", summary="获取文章列表",methods= ["GET", "POST"], operation_id="get_articles_list")
async def get_articles(
    offset: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(None),
    mp_id: str = Query(None),
    has_content:bool=Query(False),
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:

            # 构建查询条件
            if has_content:
                query = select(Article)
            else:
                query = select(ArticleBase)

            if status:
                query = query.where(Article.status == status)
            else:
                query = query.where(Article.status != DATA_STATUS.DELETED)
            if mp_id:
                query = query.where(Article.mp_id == mp_id)
            if search:
                search_conditions = format_search_kw(search)
                query = query.where(search_conditions)

            # 获取总数
            from sqlalchemy import func
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # 分页查询（按发布时间降序）
            query = query.order_by(Article.publish_time.desc()).offset(offset).limit(limit)
            result = await session.execute(query)
            articles = result.scalars().all()

            # 查询公众号名称
            from core.models.feed import Feed
            mp_ids = list(set([article.mp_id for article in articles if article.mp_id]))
            mp_names = {}
            if mp_ids:
                feed_result = await session.execute(
                    select(Feed).where(Feed.id.in_(mp_ids))
                )
                feeds = feed_result.scalars().all()
                mp_names = {feed.id: feed.mp_name for feed in feeds}

            # 合并公众号名称到文章列表
            article_list = []
            for article in articles:
                article_dict = {c.name: getattr(article, c.name) for c in article.__table__.columns}
                article_dict["mp_name"] = mp_names.get(article.mp_id, "未知公众号")
                article_list.append(article_dict)

            from .base import success_response
            return success_response({
                "list": article_list,
                "total": total
            })
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"获取文章列表失败: {str(e)}"
                )
            )

@router.get("/{article_id}", summary="获取文章详情")
async def get_article_detail(
    article_id: str,
    content: bool = False,
    # current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            result = await session.execute(
                select(Article).where(Article.id == article_id).where(Article.status != DATA_STATUS.DELETED)
            )
            article = result.scalars().first()
            if not article:
                from .base import error_response
                raise HTTPException(
                    status_code=fast_status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="文章不存在"
                    )
                )
            return success_response(fix_article(article))
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"获取文章详情失败: {str(e)}"
                )
            )   

@router.delete("/{article_id}", summary="删除文章")
async def delete_article(
    article_id: str,
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            from core.models.article import Article

            # 检查文章是否存在
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalars().first()
            if not article:
                raise HTTPException(
                    status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                    detail=error_response(
                        code=40401,
                        message="文章不存在"
                    )
                )
            # 逻辑删除文章（更新状态为deleted）
            article.status = DATA_STATUS.DELETED
            if cfg.get("article.true_delete", False):
                await session.delete(article)
            await session.commit()

            return success_response(None, message="文章已标记为删除")
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"删除文章失败: {str(e)}"
                )
            )

@router.get("/{article_id}/next", summary="获取下一篇文章")
async def get_next_article(
    article_id: str,
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            # 获取当前文章的发布时间
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            current_article = result.scalars().first()
            if not current_article:
                raise HTTPException(
                    status_code=fast_status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="当前文章不存在"
                    )
                )

            # 查询发布时间更晚的第一篇文章
            next_result = await session.execute(
                select(Article)
                .where(Article.publish_time > current_article.publish_time)
                .where(Article.status != DATA_STATUS.DELETED)
                .where(Article.mp_id == current_article.mp_id)
                .order_by(Article.publish_time.asc())
                .limit(1)
            )
            next_article = next_result.scalars().first()

            if not next_article:
                raise HTTPException(
                    status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                    detail=error_response(
                        code=40402,
                        message="没有下一篇文章"
                    )
                )
            return success_response(fix_article(next_article))
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"获取下一篇文章失败: {str(e)}"
                )
            )

@router.get("/{article_id}/prev", summary="获取上一篇文章")
async def get_prev_article(
    article_id: str,
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            # 获取当前文章的发布时间
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            current_article = result.scalars().first()
            if not current_article:
                raise HTTPException(
                    status_code=fast_status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="当前文章不存在"
                    )
                )

            # 查询发布时间更早的第一篇文章
            prev_result = await session.execute(
                select(Article)
                .where(Article.publish_time < current_article.publish_time)
                .where(Article.status != DATA_STATUS.DELETED)
                .where(Article.mp_id == current_article.mp_id)
                .order_by(Article.publish_time.desc())
                .limit(1)
            )
            prev_article = prev_result.scalars().first()

            if not prev_article:
                raise HTTPException(
                    status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                    detail=error_response(
                        code=40403,
                        message="没有上一篇文章"
                    )
                )
            return success_response(fix_article(prev_article))
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"获取上一篇文章失败: {str(e)}"
                )
            )

@router.post("/{article_id}/reextract", summary="重新提取文章内容")
async def reextract_article(
    article_id: str,
    current_user: dict = Depends(get_current_user)
):
    async with DB.async_session_factory() as session:
        try:
            # 查询文章
            result = await session.execute(
                select(Article).where(Article.id == article_id)
            )
            article = result.scalars().first()
            if not article:
                raise HTTPException(
                    status_code=fast_status.HTTP_404_NOT_FOUND,
                    detail=error_response(
                        code=40401,
                        message="文章不存在"
                    )
                )

            # 构建URL
            if article.url:
                url = article.url
            else:
                url = f"https://mp.weixin.qq.com/s/{article.id}"

            print_info(f"正在重新提取文章内容: {article.title}, URL: {url}")

            # 根据配置选择提取方法
            content = None
            if cfg.get("gather.content_mode", "web") == "web":
                # 使用 Web 浏览器方式提取 - 使用BrowserManager (异步)
                from driver.browser_manager import BrowserManager
                try:
                    async with BrowserManager(max_articles_per_browser=1, max_retries=3) as browser_mgr:
                        article_data = await browser_mgr.fetch_article(url, mobile_mode=False)
                        content = article_data.get("content", "")
                except Exception as e:
                    print_error(f"Web方式提取内容失败: {str(e)}")
            else:
                # 使用 WxGather 方式提取 (异步)
                from core.wx.base import WxGather
                try:
                    ga = WxGather().Model()
                    try:
                        # 使用 await 调用异步方法
                        content = await ga.content_extract(url)
                    finally:
                        # Explicit cleanup to prevent resource leaks
                        await ga.cleanup()
                except Exception as e:
                    print_error(f"WxGather方式提取内容失败: {str(e)}")

            # 更新文章内容
            if content:
                article.content = content
                if content == "DELETED":
                    print_error(f"文章 {article.title} 内容已被发布者删除")
                    article.status = DATA_STATUS.DELETED
                await session.commit()

                # 清除相关缓存
                clear_cache_pattern("articles_list")
                clear_cache_pattern("article_detail")
                clear_cache_pattern("tag_detail")

                print_success(f"成功重新提取文章 {article.title} 的内容")
                return success_response(fix_article(article), message="重新提取文章内容成功")
            else:
                print_error(f"重新提取文章 {article.title} 内容失败")
                raise HTTPException(
                    status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                    detail=error_response(
                        code=50001,
                        message="重新提取文章内容失败"
                    )
                )

        except HTTPException as e:
            raise e
        except Exception as e:
            await session.rollback()
            print_error(f"重新提取文章内容时发生错误: {str(e)}")
            raise HTTPException(
                status_code=fast_status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_response(
                    code=50001,
                    message=f"重新提取文章内容失败: {str(e)}"
                )
            )