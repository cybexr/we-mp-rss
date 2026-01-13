# `driver` Module

## Overview

The `driver` module provides a comprehensive suite of tools and functionalities for advanced web automation, with a particular focus on interacting with the WeChat Public Platform (`mp.weixin.qq.com`). It integrates Playwright for browser control and includes sophisticated anti-detection and human-like behavior simulation mechanisms to ensure robust and stealthy operation.

This module is designed to handle tasks such as:
- Automated login to WeChat Public Platform (via QR code or token).
- Managing browser sessions and cookies.
- Fetching and parsing WeChat articles.
- Switching between multiple WeChat accounts.
- Applying advanced anti-crawler techniques to evade bot detection.
- Intercepting and processing network traffic for specific data extraction (e.g., article read counts).
- Securely storing sensitive session data.

## Key Functionalities

*   **Browser Automation:** Utilizes Playwright to control browser instances, enabling navigation, DOM interaction, and screenshot capabilities.
*   **Anti-Detection & Behavior Simulation:** Incorporates JavaScript-based scripts (`anti_crawler_advanced.js`, `anti_crawler_base.js`, `anti_crawler_behavior.js`) to mimic human browsing patterns and bypass various anti-bot detection methods (e.g., WebDriver detection, headless browser checks, fingerprinting).
*   **WeChat Public Platform Interaction:**
    *   **Login Management:** Supports QR code login with real-time status monitoring and token-based login for persistent sessions.
    *   **Session Management:** Handles cookies, tokens, and session expiry.
    *   **Article Fetching:** Fetches full article content, extracts metadata (title, author, publish time), images, and cleans HTML.
    *   **Account Management:** Allows switching between different linked WeChat public accounts.
*   **Data Storage:** Provides an encrypted `KeyStore` for secure persistence of sensitive data like session cookies.
*   **Network Interception:** Includes a `mitmproxy` add-on (`extdata/like.py`) for custom HTTP traffic interception and analysis, demonstrating capabilities like extracting article read counts.
*   **Retry Mechanisms & Delays:** Implements robust retry logic with exponential backoff and human-like random delays to improve resilience against network issues and server-side rate limiting.

## Basic Usage

The core functionalities are exposed through various classes and functions, primarily designed to be integrated into larger automation workflows.

### Example: QR Code Login to WeChat Public Platform

```python
import asyncio
from driver.wx import WX_API

async def main():
    async def login_callback(session_data, account_info):
        print("Login successful!")
        print(f"Token: {session_data.get('token')}")
        print(f"Account Info: {account_info}")

    async def notice_callback(message):
        print(f"Notice: {message}")

    print("Initiating WeChat QR code login...")
    result = WX_API.GetCode(CallBack=login_callback, Notice=notice_callback)
    print(f"QR Code info: {result}")

    # The login process runs in the background.
    # You might want to add a loop here to keep the main program alive
    # until login is confirmed or times out.
    while not await WX_API.HasLogin():
        print("Waiting for login...")
        await asyncio.sleep(5)
    print("Logged in successfully!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example: Fetching an Article

```python
import asyncio
from driver.playwright_driver import PlaywrightController
from driver.wxarticle import WXArticleFetcher

async def main():
    controller = PlaywrightController()
    try:
        await controller.start_browser(headless=True)
        fetcher = WXArticleFetcher(page=controller.page)

        article_url = "https://mp.weixin.qq.com/s/your-wechat-article-id"
        print(f"Fetching article: {article_url}")
        article_data = await fetcher.get_article_content(article_url)

        if article_data and article_data.get("content") != "DELETED":
            print(f"Title: {article_data.get('title')}")
            print(f"Author: {article_data.get('author')}")
            print(f"Content snippet: {article_data.get('content')[:200]}...")
        else:
            print(f"Failed to fetch article or it was deleted/unavailable.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await controller.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

For detailed API specifications, refer to the `API.md` document.
