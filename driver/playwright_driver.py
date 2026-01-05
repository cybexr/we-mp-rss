from asyncio import futures
import os
import platform
import sys
import json
import random
import uuid
import asyncio
from socket import timeout

# 设置环境变量
browsers_name = os.getenv("BROWSER_TYPE", "firefox")
browsers_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH", "")
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path

# 导入Playwright相关模块 - 使用async API
from playwright.async_api import async_playwright

# 导入反爬虫配置
from .anti_crawler_config import AntiCrawlerConfig


# 辅助函数：用于中止图片加载的路由处理器
async def _abort_images(route):
    await route.abort()

class PlaywrightController:
    def __init__(self):
        self.system = platform.system().lower()
        self.playwright = None
        self.driver = None
        self.browser = None
        self.context = None
        self.page = None
        self.isClose = True
    def _is_browser_installed(self, browser_name):
        """检查指定浏览器是否已安装"""
        try:
            
            # 遍历目录，查找包含浏览器名称的目录
            for item in os.listdir(browsers_path):
                item_path = os.path.join(browsers_path, item)
                if os.path.isdir(item_path) and browser_name.lower() in item.lower():
                    return True
            
            return False
        except (OSError, PermissionError):
            return False
    def is_async(self):
        # Always return True for async API
        return True

    def is_browser_started(self):
        """检测浏览器是否已启动，包含实际连接状态验证"""
        # 首先检查基本对象引用是否存在
        if (self.isClose or
            self.driver is None or
            self.browser is None or
            self.context is None or
            self.page is None):
            return False

        # 尝试验证浏览器实际连接状态
        try:
            # 检查浏览器是否连接（is_connected在Playwright中可用）
            if hasattr(self.browser, 'is_connected'):
                return self.browser.is_connected()
            # 如果没有is_connected方法，检查page是否可访问
            # 通过检查page的基本属性来验证状态
            elif hasattr(self.page, 'url'):
                # 如果能访问page.url，说明page对象仍然有效
                return True
            else:
                return False
        except Exception:
            # 任何异常都说明浏览器状态异常
            return False

    async def start_browser(self, headless=True, mobile_mode=False, dis_image=True, browser_name=browsers_name, language="zh-CN", anti_crawler=True):
        try:
            # 使用线程锁确保线程安全
            if  str(os.getenv("NOT_HEADLESS",False))=="True":
                headless = False
            else:
                headless = True

            if self.system != "windows":
                headless = True

            if self.driver is None:
                if sys.platform == "win32" :
                    # 设置事件循环策略为WindowsSelectorEventLoopPolicy
                    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                # 使用async_playwright
                self.playwright = await async_playwright().start()
                self.driver = self.playwright
        
            # 根据浏览器名称选择浏览器类型
            if browser_name.lower() == "firefox":
                browser_type = self.driver.firefox
            elif browser_name.lower() == "webkit":
                browser_type = self.driver.webkit
            else:
                browser_type = self.driver.chromium  # 默认使用chromium
            print(f"启动浏览器: {browser_name}, 无头模式: {headless}, 移动模式: {mobile_mode}, 反爬虫: {anti_crawler}")
            # 设置启动选项
            launch_options = {
                "headless": headless
            }

            # 在Windows上添加额外的启动选项
            if self.system == "windows":
                launch_options["handle_sigint"] = False
                launch_options["handle_sigterm"] = False
                launch_options["handle_sighup"] = False

            self.browser = await browser_type.launch(**launch_options)
            
            # 设置浏览器语言为中文
            context_options = {
                "locale": language
            }

            # 反爬虫配置 - 使用AntiCrawlerConfig
            if anti_crawler:
                context_options.update(AntiCrawlerConfig.get_anti_detection_config(mobile_mode))

            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()

            if mobile_mode:
                await self.page.set_viewport_size({"width": 375, "height": 812})
            # else:
            #     self.page.set_viewport_size({"width": 1920, "height": 1080})

            if dis_image:
                await self.context.route("**/*.{png,jpg,jpeg}", _abort_images)

            # 应用反爬虫脚本
            if anti_crawler:
                await self._apply_anti_crawler_scripts()

            self.isClose = False
            return self.page
        except Exception as e:
            error_msg = str(e)
            print(f"浏览器启动失败: {error_msg}")

            # Distinguish between async context errors and browser installation issues
            if 'Sync API' in error_msg or 'asyncio' in error_msg or 'async' in error_msg.lower():
                # Async context error - using sync API in async loop
                tips = "Async context error: You are using sync Playwright API inside an asyncio event loop. Solution: Convert all Playwright calls to async API (use playwright.async_api instead of playwright.sync_api, and add 'await' to all Playwright method calls)."
                print(tips)
                await self.cleanup()
                raise Exception(tips)
            elif 'executable' in error_msg.lower() or 'browser' in error_msg.lower() or 'not found' in error_msg.lower():
                # Browser not installed
                tips = "Docker环境;您可以设置环境变量INSTALL=True并重启Docker自动安装浏览器环境;如需要切换浏览器可以设置环境变量BROWSER_TYPE=firefox 支持(firefox,webkit,chromium),开发环境请手工安装"
                print(tips)
                await self.cleanup()
                raise Exception(tips)
            else:
                # Generic error with full traceback
                import traceback
                traceback.print_exc()
                tips = f"Browser launch failed: {error_msg}. Check logs above for full error details."
                print(tips)
                await self.cleanup()
                raise Exception(tips)
        
    def string_to_json(self, json_string):
        try:
            json_obj = json.loads(json_string)
            return json_obj
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return ""

    def parse_string_to_dict(self, kv_str: str):
        result = {}
        items = kv_str.strip().split(';')
        for item in items:
            try:
                key, value = item.strip().split('=')
                result[key.strip()] = value.strip()
            except Exception as e:
                pass
        return result

    async def add_cookies(self, cookies):
        if self.context is None:
            raise Exception("浏览器未启动，请先调用 start_browser()")
        await self.context.add_cookies(cookies)

    async def get_cookies(self):
        if self.context is None:
            raise Exception("浏览器未启动，请先调用 start_browser()")
        return await self.context.cookies()

    async def add_cookie(self, cookie):
        await self.add_cookies([cookie])

    async def _apply_anti_crawler_scripts(self):
        """应用反爬虫脚本"""
        try:
            from playwright_stealth.stealth import Stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(self.page)
        except ImportError:
            print("检测到playwright_stealth未安装，正在自动安装...")
            # Use async subprocess to avoid blocking the event loop
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", "playwright_stealth",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                print(f"安装playwright_stealth失败: {stderr.decode()}")
                raise
            from playwright_stealth.stealth import Stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(self.page)
        # 隐藏自动化特征
        await self.page.add_init_script("""
        // 隐藏webdriver属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // 隐藏chrome属性
        Object.defineProperty(window, 'chrome', {
            get: () => false,
        });
        
        // 修改plugins长度
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // 修改languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });
        
        // 隐藏自动化痕迹
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // 修改permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """)

        # 设置更真实的浏览器行为
        await self.page.evaluate("""
        // 随机延迟点击事件
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type === 'click') {
                const wrappedListener = function(...args) {
                    setTimeout(() => listener.apply(this, args), Math.random() * 100 + 50);
                };
                return originalAddEventListener.call(this, type, wrappedListener, options);
            }
            return originalAddEventListener.call(this, type, listener, options);
        };
        
        // 随机化鼠标移动
        document.addEventListener('mousemove', (e) => {
            if (Math.random() > 0.7) {
                e.stopImmediatePropagation();
            }
        }, true);
        """)

       

   

    # IMPORTANT: Always use async context manager for proper cleanup:
    # Example usage:
    #   controller = PlaywrightController()
    #   try:
    #       await controller.start_browser()
    #       await controller.open_url("https://example.com")
    #   finally:
    #       await controller.cleanup()
    #
    # DO NOT rely on __del__ for cleanup - async cleanup cannot be safely
    # called from __del__ and will cause RuntimeWarning or resource leaks.

    async def open_url(self, url, wait_until="domcontentloaded"):
        try:
            await self.page.goto(url, wait_until=wait_until)
        except Exception as e:
            raise Exception(f"打开URL失败: {str(e)}")

    async def Close(self):
        await self.cleanup()

    async def cleanup(self):
        """清理所有资源，优雅处理已关闭的对象"""
        # 分别处理每个资源，确保单个失败不影响其他资源清理
        # 1. 关闭page
        if hasattr(self, 'page') and self.page is not None:
            try:
                await self.page.close()
                self.page = None
            except Exception as e:
                print(f"关闭page时出错（可能已关闭）: {str(e)}")
                self.page = None

        # 2. 关闭context
        if hasattr(self, 'context') and self.context is not None:
            try:
                await self.context.close()
                self.context = None
            except Exception as e:
                print(f"关闭context时出错（可能已关闭）: {str(e)}")
                self.context = None

        # 3. 关闭browser
        if hasattr(self, 'browser') and self.browser is not None:
            try:
                await self.browser.close()
                self.browser = None
            except Exception as e:
                print(f"关闭browser时出错（可能已关闭）: {str(e)}")
                self.browser = None

        # 4. 停止playwright
        if hasattr(self, 'playwright') and self.playwright is not None:
            try:
                await self.playwright.stop()
                self.playwright = None
            except Exception as e:
                print(f"停止playwright时出错（可能已停止）: {str(e)}")
                self.playwright = None

        # 5. 清理driver引用
        if hasattr(self, 'driver'):
            self.driver = None

        # 6. 设置关闭标志
        self.isClose = True

    def dict_to_json(self, data_dict):
        try:
            return json.dumps(data_dict, ensure_ascii=False, indent=2)
        except (TypeError, ValueError) as e:
            print(f"字典转JSON失败: {e}")
            return ""

ControlDriver=PlaywrightController()
# 示例用法
if __name__ == "__main__":
    async def main():
        controller = PlaywrightController()
        try:
            await controller.start_browser(headless=False)
            await controller.open_url("https://mp.weixin.qq.com/")
            # Keep browser open for a few seconds to observe
            await asyncio.sleep(10)
        finally:
            await controller.cleanup()

    asyncio.run(main())