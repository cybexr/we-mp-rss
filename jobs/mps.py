from datetime import datetime
from core.models.article import Article
from .article import UpdateArticle,Update_Over
import core.db as db
from core.wx import WxGather
from core.log import logger
from core.task import GlobalScheduler
from core.models.feed import Feed
from core.config import cfg,DEBUG
from core.print import print_info,print_success,print_error
from driver.wx import WX_API
from driver.success import Success
from driver.browser_manager import BrowserManager
import asyncio
import random
wx_db=db.Db(tag="任务调度")

async def fetch_all_article():
    print("开始更新")
    wx=WxGather().Model()
    try:
        # 获取公众号列表
        mps=db.DB.get_all_mps()
        for item in mps:
            try:
                await wx.get_Articles(item.faker_id,CallBack=UpdateArticle,Mps_id=item.id,Mps_title=item.mp_name, MaxPage=1)
            except Exception as e:
                print(e)
        print(wx.articles)
    except Exception as e:
        print(e)
    finally:
        logger.info(f"所有公众号更新完成,共更新{wx.all_count()}条数据")


def test(info:str):
    print("任务测试成功",info)

"""
Article List Collection Jobs - Dual-Queue Architecture

This module handles scheduled article list collection from WeChat Official Accounts (MPs).
Uses GlobalQueueManager.list_queue for article list fetching tasks.

Architecture:
    - list_queue: Article list collection (paused when QR code expires)
    - content_queue: Article content extraction (independent, see fetch_no_article.py)

Queue Pause Behavior:
    - When WeChat QR code expires: list_queue pauses automatically via driver/success.setStatus(False)
    - Article list tasks remain queued but won't execute until QR login success
    - Content extraction queue continues independently

Usage:
    from jobs.mps import start_job, add_job
    start_job()  # Start scheduled collection via APScheduler
    await add_job(feeds, task)  # Manual collection trigger
"""

from core.models.message_task import MessageTask
from core.queue import GlobalQueueManager
from .webhook import web_hook

async def do_job(mp=None,task:MessageTask=None):
        # TaskQueue.add_task(test,info=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # print("执行任务", task.mps_id)
        print("执行任务")
        all_count=0
        wx=WxGather().Model()

        # Read messagetask_mp_delay config for pagination delay (default 2s, clamped 1-10s)
        delay_base = cfg.get('messagetask_mp_delay', 2)
        delay_base = max(1, min(10, float(delay_base)))
        # Calculate interval with 30% random variation for pagination delay
        page_interval = int(delay_base * random.uniform(0.7, 1.3))
        print(f"Pagination delay for [{mp.mp_name}]: {page_interval}s (base: {delay_base}s)")

        try:
            await wx.get_Articles(mp.faker_id,CallBack=UpdateArticle,Mps_id=mp.id,Mps_title=mp.mp_name, MaxPage=1,Over_CallBack=Update_Over,interval=page_interval)
        except Exception as e:
            print_error(e)
            # raise
        finally:
            count=wx.all_count()
            all_count+=count
            from jobs.webhook import MessageWebHook 
            tms=MessageWebHook(task=task,feed=mp,articles=wx.articles)
            web_hook(tms)
            print_success(f"任务({task.id})[{mp.mp_name}]执行成功,{count}成功条数")

from core.queue import GlobalQueueManager
async def add_job(feeds:list[Feed]=None,task:MessageTask=None,isTest=False):
    if isTest:
        GlobalQueueManager.list_queue.clear_queue()

    # Read and validate messagetask_mp_delay config (default 2s, range 1-10s)
    delay_base = cfg.get('messagetask_mp_delay', 2)
    delay_base = max(1, min(10, float(delay_base)))  # Clamp to 1-10s range

    for feed in feeds:
        GlobalQueueManager.list_queue.add_task(do_job,feed,task)
        if isTest:
            print(f"测试任务，{feed.mp_name}，加入队列成功")
            reload_job()
            break
        # Add delay with 30% random variation between each MP processing
        actual_delay = delay_base * random.uniform(0.7, 1.3)
        print(f'等待 {actual_delay:.2f}秒后处理下一个公众号...')
        await asyncio.sleep(actual_delay)
        print(f"{feed.mp_name}，加入队列成功")
    print_success(GlobalQueueManager.list_queue.get_queue_info())
    pass
import json
def get_feeds(task:MessageTask=None):
     mps = json.loads(task.mps_id)
     ids=",".join([item["id"]for item in mps])
     mps=wx_db.get_mps_list(ids)
     if len(mps)==0:
        mps=wx_db.get_all_mps()
     return mps

def reload_job():
    print_success("重载任务")
    GlobalScheduler.clear_all_jobs()
    GlobalQueueManager.list_queue.clear_queue()
    start_job()

async def run(job_id:str=None,isTest=False):
    from .taskmsg import get_message_task
    tasks=get_message_task(job_id)
    if not tasks:
        print("没有任务")
        return None
    for task in tasks:
            #添加测试任务
            from core.print import print_warning
            print_warning(f"{task.name} 添加到队列运行")
            await add_job(get_feeds(task),task,isTest=isTest)
            pass
    return tasks
def start_job(job_id:str=None):
    from .taskmsg import get_message_task
    tasks=get_message_task(job_id)
    if not tasks:
        print("没有任务")
        return
    tag="定时采集"
    for task in tasks:
        cron_exp=task.cron_exp
        if not cron_exp:
            print_error(f"任务[{task.id}]没有设置cron表达式")
            continue
      
        job_id=GlobalScheduler.add_cron_job(add_job,cron_expr=cron_exp,args=[get_feeds(task),task],job_id=str(task.id),tag="定时采集")
        print(f"已添加任务: {job_id}")
    GlobalScheduler.start()
    print("启动任务")
def start_all_task():
      #开启自动同步未同步 文章任务
    from jobs.fetch_no_article import start_sync_content
    start_sync_content()
    start_job()
if __name__ == '__main__':
    # do_job()
    # start_all_task()
    pass