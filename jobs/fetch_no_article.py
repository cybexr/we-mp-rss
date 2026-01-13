from core.models.article import Article,DATA_STATUS
import core.db as db
from core.wx.base import WxGather
from core.print import print_success,print_error,print_warning, JobLogger
import random
import asyncio
DB=db.Db(tag="内容修正")

async def fetch_articles_without_content():
    """
    查询content为空的文章，调用微信内容提取方法获取内容并更新数据库
    """
    from driver.browser_manager import BrowserManager
    from sqlalchemy import select, or_

    # 查询content为空的文章 - 使用异步session
    async with DB.async_session_factory() as session:
        try:
            # 使用 gather.content_max_articles_per_batch 配置，默认10，范围1-1000
            max_articles_per_batch = cfg.get('gather.content_max_articles_per_batch', 10)
            max_articles_per_batch = max(1, min(1000, int(max_articles_per_batch)))

            stmt = select(Article).where(or_(Article.content.is_(None), Article.content == "")).order_by(Article.publish_time.desc()).limit(max_articles_per_batch)
            result = await session.execute(stmt)
            articles = result.scalars().all()
            if not articles:
                print_warning("暂无需要获取内容的文章")
                return

            # 使用async context manager初始化BrowserManager
            # 使用新的 gather.content_req_delay 配置，并在其基础上±30%随机浮动
            base_delay = float(cfg.get("gather.content_req_delay", 2))
            min_delay = base_delay * 0.7  # -30%
            max_delay = base_delay * 1.3  # +30%

            # 使用 gather.content_browser_restart_req 配置，默认100，范围1-1000
            browser_restart_req = cfg.get('gather.content_browser_restart_req', 100)
            browser_restart_req = max(1, min(1000, int(browser_restart_req)))

            async with BrowserManager(
                max_articles_per_browser=browser_restart_req,
                max_retries=3,
                min_delay=min_delay,
                max_delay=max_delay
            ) as browser_manager:

                # Use JobLogger for sync content job context
                with JobLogger(JobLogger.SYNC_CONTENT, mp_name="") as job_logger:
                    for article in articles:
                        # 构建URL
                        if article.url:
                            url = article.url
                        else:
                            url = f"https://mp.weixin.qq.com/s/{article.id}"

                        # Create child context with article title
                        article_title = article.title[:30] if article.title else article.id
                        article_logger = job_logger.child_context(article_title)
                        article_logger.print_info(f"正在处理文章, URL: {url}")

                        # 获取内容
                        if cfg.get("gather.content_mode","web"):
                            article_data = await browser_manager.fetch_article(url, mobile_mode=False)
                            content = article_data.get("content")
                        else:
                            # 仅在非web模式下初始化WxGather
                            if 'ga' not in locals():
                                ga = WxGather().Model()
                            content = await ga.content_extract(url)
                        if content:
                            # 更新内容
                            article.content = content
                            if  content=="DELETED":
                                article_logger.print_error("内容已被发布者删除")
                                article.status = DATA_STATUS.DELETED
                            await session.commit()
                            article_logger.print_success("成功更新文章内容")
                        else:
                            article_logger.print_error("获取文章内容失败")
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            await session.rollback()
"""
Article Content Extraction Jobs - Dual-Queue Architecture

This module handles article content extraction using browser automation.
Uses GlobalQueueManager.content_queue for content extraction tasks.

Architecture:
    - content_queue: Article content extraction (independent from list_queue)
    - list_queue: Article list collection (see mps.py)

Queue Independence:
    - content_queue runs independently, NOT affected by WeChat QR expiry
    - Continues processing even when list_queue is paused
    - Ensures content extraction progresses regardless of authentication state

Usage:
    from jobs.fetch_no_article import start_sync_content
    start_sync_content()  # Start scheduled content extraction
"""

from core.task import GlobalScheduler
from core.queue import GlobalQueueManager
from core.config import cfg
from core.print import print_success,print_warning

def start_sync_content():
    """
    根据配置自动启动文章内容同步任务

    功能：
    - 检查是否启用了自动同步功能
    - 根据配置的间隔时间设置定时任务
    - 清除现有任务队列和调度器中的所有作业
    - 添加新的定时同步任务并启动调度器

    Args:
        无显式参数，从配置中读取以下设置：
        - gather.content_auto_check: 是否启用自动同步功能
        - gather.content_auto_interval: 同步间隔时间（分钟）

    Returns:
        None

    Raises:
        无显式异常抛出，但内部可能打印警告或成功信息
    """
    if not cfg.get("gather.content_auto_check",False):
        print_warning("自动检查并同步文章内容功能未启用")
        return
    interval=int(cfg.get("gather.content_auto_interval",10)) # 每隔多少分钟

    # Convert to hours if interval > 59 minutes (Cron minute field only accepts 0-59)
    if interval > 59:
        hours = interval // 60
        if hours > 23:
            print_warning(f"间隔时间{interval}分钟超过24小时,已调整为24小时")
            hours = 23
            cron_exp = "0 */23 * * *"  # Every 23 hours
        else:
            cron_exp = f"0 */{hours} * * *"  # Every N hours at minute 0
        print_success(f"间隔{interval}分钟已转换为{hours}小时")
    else:
        cron_exp = f"*/{interval} * * * *"  # Every N minutes

    GlobalQueueManager.content_queue.clear_queue()
    GlobalScheduler.clear_all_jobs()
    job_id=GlobalScheduler.add_cron_job(fetch_articles_without_content,cron_expr=cron_exp)
    print_success(f"已添自动同步文章内容任务: {job_id}, cron表达式: {cron_exp}")
    GlobalScheduler.start()

if __name__ == "__main__":
    asyncio.run(fetch_articles_without_content())