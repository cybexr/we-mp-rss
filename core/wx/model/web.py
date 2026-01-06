import json
import requests
import time
import random
import asyncio
import aiohttp
import yaml
import re
from bs4 import BeautifulSoup
from core.wx.base import WxGather
from core.print import print_error, print_info, print_warning
from core.log import logger
from core.config import cfg

# 继承 BaseGather 类
class MpsWeb(WxGather):
    """Web模式采集 - 使用BrowserManager进行浏览器复用和重试"""

    def __init__(self):
        super().__init__()
        self.browser_manager = None

    def _get_browser_manager(self):
        """获取或创建BrowserManager实例"""
        if self.browser_manager is None:
            from driver.browser_manager import BrowserManager
            # 配置：使用 gather.content_browser_restart_req 配置，每N个文章重启一次浏览器，最多重试3次，延迟2-5秒
            browser_restart_req = cfg.get('gather.content_browser_restart_req', 100)
            browser_restart_req = max(1, min(1000, int(browser_restart_req)))
            self.browser_manager = BrowserManager(
                max_articles_per_browser=browser_restart_req,
                max_retries=3,
                min_delay=2.0,
                max_delay=5.0
            )
        return self.browser_manager

    # 重写 content_extract 方法 - 异步版本
    async def content_extract(self,  url):
        """提取文章内容，使用BrowserManager进行浏览器复用和重试"""
        try:
            from driver.wxarticle import WXArticleFetcher

            browser_manager = self._get_browser_manager()
            print_info(f"Extracting content from: {url}")

            # 使用BrowserManager获取文章内容 (异步)
            result = await browser_manager.fetch_article(url, mobile_mode=False)

            if result and result.get("content"):
                text = result.get("content", "")
                text = self.remove_common_html_elements(text)
                return text
            else:
                print_warning(f"No content extracted from: {url}")
                return ""

        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            print_error(f"Error extracting content: {e}")
        return ""

    async def cleanup(self):
        """清理浏览器资源"""
        if self.browser_manager:
            await self.browser_manager.cleanup()
            self.browser_manager = None

    # IMPORTANT: Always use async context manager for proper cleanup:
    # Example usage:
    #   mps_web = MpsWeb()
    #   try:
    #       await mps_web.get_Articles(...)
    #   finally:
    #       await mps_web.cleanup()
    #
    # DO NOT rely on __del__ for cleanup - async cleanup cannot be safely
    # called from __del__ and will cause RuntimeWarning or resource leaks.
    # 重写 get_Articles 方法 - 异步版本
    async def get_Articles(self, faker_id:str=None,Mps_id:str=None,Mps_title="",CallBack=None,start_page:int=0,MaxPage:int=1,interval=10,Gather_Content=False,Item_Over_CallBack=None,Over_CallBack=None):
        super().Start(mp_id=Mps_id)
        if self.Gather_Content:
            Gather_Content=True
        print(f"Web浏览器模式,是否采集[{Mps_title}]内容：{Gather_Content}\n")
        # 请求参数
        url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
        count=5
        params = {
        "sub": "list",
        "sub_action": "list_ex",
        "begin":start_page,
        "count": count,
        "fakeid": faker_id,
        "token": self.token,
        "lang": "zh_CN",
        "f": "json",
        "ajax": 1
    }
        # 连接超时
        session=self.session
        # 起始页数
        i = start_page
        consecutive_empty_page = 0
        should_stop = False  # Flag to stop pagination
        while True:
            if i >= MaxPage:
                break
            begin = i * count
            params["begin"] = str(begin)
            print(f"第{i+1}页开始爬取\n")
            # 随机暂停几秒，避免过快的请求导致过快的被查到
            await asyncio.sleep(random.randint(0,interval))
            try:
                headers = self.fix_header(url)
                # Use aiohttp for async HTTP request
                async with aiohttp.ClientSession(cookies=session.cookies, connector=aiohttp.TCPConnector(ssl=False)) as aio_session:
                    async with aio_session.get(url, headers=headers, params=params) as resp:
                        msg = await resp.json()
                        self._cookies = resp.cookies
                # 流量控制了, 退出
                if msg['base_resp']['ret'] == 200013:
                    super().Error("frequencey control, stop at {}".format(str(begin)))
                    break
                
                if msg['base_resp']['ret'] == 200003:
                    super().Error("Invalid Session, stop at {}".format(str(begin)),code="Invalid Session")
                    break
                if msg['base_resp']['ret'] != 0:
                    super().Error("错误原因:{}:代码:{}".format(msg['base_resp']['err_msg'],msg['base_resp']['ret']),code=msg['base_resp']['err_msg'])
                    break    
                # 如果返回的内容中为空则结束
                if 'publish_page' not in msg:
                    super().Error("all ariticle parsed")
                    break
                if msg['base_resp']['ret'] != 0:
                    super().Error("错误原因:{}:代码:{}".format(msg['base_resp']['err_msg'],msg['base_resp']['ret']))
                    break  
                if "publish_page" in msg:
                    msg["publish_page"]=json.loads(msg['publish_page'])
                    publish_list = msg["publish_page"].get('publish_list', [])

                    # Check if page is empty
                    if len(publish_list) == 0:
                        consecutive_empty_page += 1
                        print(f"第{i+1}页无文章，连续空页计数: {consecutive_empty_page}/3")
                        if consecutive_empty_page >= 3:
                            print("连续3页无文章，提前停止翻页")
                            should_stop = True
                            break  # Break the for loop (empty pages, so nothing to iterate anyway)
                    else:
                        consecutive_empty_page = 0

                    for item in publish_list:
                        if "publish_info" in item:
                            publish_info= json.loads(item['publish_info'])
                       
                            if "appmsgex" in publish_info:
                                # info = '"{}","{}","{}","{}"'.format(str(item["aid"]), item['title'], item['link'], str(item['create_time']))
                                for item in publish_info["appmsgex"]:
                                    if Gather_Content:
                                        if not super().HasGathered(item["aid"]):
                                            item["content"] = await self.content_extract(item['link'])
                                            super().Wait(3,10,tips=f"{item['title']} 采集完成")
                                    else:
                                        item["content"] = ""
                                    item["id"] = item["aid"]
                                    item["mp_id"] = Mps_id
                                    if CallBack is not None:
                                        super().FillBack(CallBack=CallBack,data=item,Ext_Data={"mp_title":Mps_title,"mp_id":Mps_id})
                    print(f"第{i+1}页爬取成功\n")

                    # Check if we should stop pagination after processing this page
                    if should_stop:
                        break

                # 翻页
                i += 1
            except (aiohttp.ClientTimeout, asyncio.TimeoutError):
                print("Request timed out")
                break
            except aiohttp.ClientError as e:
                print(f"Request error: {e}")
                break
            finally:
                super().Item_Over(item={"mps_id":Mps_id,"mps_title":Mps_title},CallBack=Item_Over_CallBack)
        super().Over(CallBack=Over_CallBack)
        pass