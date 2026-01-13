# API Documentation for `driver` Module

This document details the public Application Programming Interfaces (APIs) exposed by the `driver` module, encompassing both JavaScript and Python components.

## JavaScript APIs

### `anti_crawler_advanced.js`

This script provides advanced anti-detection and human-like behavior simulation capabilities for web automation.

#### Classes

##### `AntiDetectionBypass`

Handles various techniques to bypass common anti-bot detection mechanisms, including Selenium, WebDriver, PhantomJS, and headless browser checks. It also implements browser fingerprint randomization, network spoofing, and timing attack prevention.

**Constructor**

```javascript
new AntiDetectionBypass()
```

Initializes the `AntiDetectionBypass` module, setting up all the detection bypass mechanisms.

**Methods**

*   **`init()`**
    ```javascript
    antiDetectionBypass.init()
    ```
    Initializes all bypass mechanisms by calling a series of internal methods. This is automatically called by the constructor.

*   **`bypassSeleniumDetection()`**
    ```javascript
    antiDetectionBypass.bypassSeleniumDetection()
    ```
    Hides Selenium-specific properties and spoofs `document.documentElement.hasAttribute` to evade detection.

*   **`bypassWebDriverDetection()`**
    ```javascript
    antiDetectionBypass.bypassWebDriverDetection()
    ```
    Masks `navigator.webdriver` and other `window.navigator` properties to prevent WebDriver detection.

*   **`bypassPhantomDetection()`**
    ```javascript
    antiDetectionBypass.bypassPhantomDetection()
    ```
    Conceals `window.callPhantom`, `window._phantom`, and `window.phantom` properties to bypass PhantomJS detection.

*   **`bypassHeadlessDetection()`**
    ```javascript
    antiDetectionBypass.bypassHeadlessDetection()
    ```
    Spoofs `navigator.headless` and `window.chrome` objects to circumvent headless browser detection.

*   **`browserFingerprintRandomization()`**
    ```javascript
    antiDetectionBypass.browserFingerprintRandomization()
    ```
    Introduces randomization to browser fingerprints, specifically for User-Agent strings and canvas rendering.

*   **`networkSpoofing()`**
    ```javascript
    antiDetectionBypass.networkSpoofing()
    ```
    Modifies `window.fetch` and `XMLHttpRequest` to add random delays and headers, mimicking human-like network behavior.

*   **`timingAttackPrevention()`**
    ```javascript
    antiDetectionBypass.timingAttackPrevention()
    ```
    Adds small, random delays to `performance.now()` and `Date.now()` to prevent timing-based detection attacks.

##### `AdvancedBehaviorSimulator`

Simulates advanced human-like browsing behavior to make automated interactions less detectable. This includes reading patterns, interaction habits, human errors, and break patterns.

**Constructor**

```javascript
new AdvancedBehaviorSimulator()
```

Initializes the `AdvancedBehaviorSimulator` module, setting up listeners and intervals for simulating various user behaviors.

**Methods**

*   **`init()`**
    ```javascript
    advancedBehaviorSimulator.init()
    ```
    Initializes all behavior simulation mechanisms. This is automatically called by the constructor.

*   **`simulateReadingBehavior()`**
    ```javascript
    advancedBehaviorSimulator.simulateReadingBehavior()
    ```
    Simulates natural scrolling and reading patterns, including progressive scrolling down a page.

*   **`simulateInteractionPatterns()`**
    ```javascript
    advancedBehaviorSimulator.simulateInteractionPatterns()
    ```
    Mimics typical user interaction patterns such as form filling (with potential errors and corrections) and hesitant link hovering before clicking.

*   **`simulateHumanErrors()`**
    ```javascript
    advancedBehaviorSimulator.simulateHumanErrors()
    ```
    Introduces common human errors like misclicks on nearby elements and exaggerated scrolling.

*   **`simulateBreakPatterns()`**
    ```javascript
    advancedBehaviorSimulator.simulateBreakPatterns()
    ```
    Simulates periods of user inactivity or "breaks," including simulating window visibility changes and subsequent return with potential new scroll positions.

##### `RealTimeDetectionBypass`

Monitors for real-time anti-bot detection attempts and dynamically adjusts behavior to counter them.

**Constructor**

```javascript
new RealTimeDetectionBypass()
```

Initializes the `RealTimeDetectionBypass` module, setting up mechanisms to monitor detection attempts and adjust responses dynamically.

**Methods**

*   **`init()`**
    ```javascript
    realTimeDetectionBypass.init()
    ```
    Initializes the real-time detection monitoring and response mechanisms. This is automatically called by the constructor.

*   **`monitorDetectionAttempts()`**
    ```javascript
    realTimeDetectionBypass.monitorDetectionAttempts()
    ```
    Overrides `window.getComputedStyle` to monitor how frequently detection scripts are probing for browser properties. It can return misleading information if too many attempts are detected.

*   **`dynamicResponseAdjustment()`**
    ```javascript
    realTimeDetectionBypass.dynamicResponseAdjustment()
    ```
    Periodically checks the frequency of detection attempts and, if high, can temporarily pause (and later resume) the `AdvancedBehaviorSimulator` to reduce activity and avoid further detection.

#### Global Exports

The following instances of the classes are made globally available on the `window` object for easy access:

*   `window.antiDetectionBypass`: An instance of `AntiDetectionBypass`.
*   `window.advancedBehaviorSimulator`: An instance of `AdvancedBehaviorSimulator`.
*   `window.realTimeDetectionBypass`: An instance of `RealTimeDetectionBypass`.

### `anti_crawler_base.js`

This script applies foundational anti-detection techniques by directly modifying global JavaScript objects and prototypes. It does not expose a traditional API but alters the browser environment to circumvent common bot detection mechanisms such as `navigator.webdriver`, `navigator.mimeTypes`, various hardware/screen properties, canvas and WebGL fingerprints, Chrome extension APIs (`chrome.runtime`, `chrome.permissions`), `performance.memory`, language/timezone settings, automation-related properties, and network connection details.

### `anti_crawler_behavior.js`

This script focuses on simulating human-like user behavior to make automated interactions less detectable.

#### Classes

##### `BehaviorSimulator`

Manages various aspects of simulated human user behavior within the browser.

**Constructor**

```javascript
new BehaviorSimulator()
```

Initializes the `BehaviorSimulator` module, setting up listeners and intervals for simulating various user behaviors.

**Methods**

*   **`init()`**
    ```javascript
    behaviorSimulator.init()
    ```
    Initializes all behavior simulation mechanisms.

*   **`simulateMouseActivity()`**
    ```javascript
    behaviorSimulator.simulateMouseActivity()
    ```
    Simulates mouse movements and clicks, including random pauses and irregular trajectories.

*   **`simulateScrolling()`**
    ```javascript
    behaviorSimulator.simulateScrolling()
    ```
    Simulates natural scrolling behavior, including irregular scrolling and occasional "bounce-back" near the page bottom.

*   **`startAutoScroll()`**
    ```javascript
    behaviorSimulator.startAutoScroll()
    ```
    Starts a periodic auto-scrolling process when the page is inactive.

*   **`simulateKeyboardActivity()`**
    ```javascript
    behaviorSimulator.simulateKeyboardActivity()
    ```
    Simulates keyboard events, including random delays and key presses.

*   **`simulateFocusBehavior()`**
    ```javascript
    behaviorSimulator.simulateFocusBehavior()
    ```
    Simulates user focus changes, including temporary distractions and tab switching.

*   **`simulateHumanDelays()`**
    ```javascript
    behaviorSimulator.simulateHumanDelays()
    ```
    Introduces random delays into common DOM querying methods like `document.querySelector` to mimic human reaction times.

*   **`simulatePageInteraction()`**
    ```javascript
    behaviorSimulator.simulatePageInteraction()
    ```
    Simulates various page interactions such as mouse hovering over elements and text selection.

*   **`pause()`**
    ```javascript
    behaviorSimulator.pause()
    ```
    Pauses all active behavior simulations.

*   **`resume()`**
    ```javascript
    behaviorSimulator.resume()
    ```
    Resumes all paused behavior simulations.

#### Global Exports

*   `window.behaviorSimulator`: An instance of `BehaviorSimulator`.

---

## Python APIs

### `auth.py`

This module provides functionality for managing authorization processes, including a scheduled task for token refresh.

#### Functions

*   **`auth()`**
    ```python
    auth()
    ```
    Executes the authorization process, typically involving a `WX_InterFace` (from `base.py`) to switch accounts. It uses a file lock to ensure only one process runs at a time.

### `base.py`

This module acts as a dynamic importer for `WX_API` and `WX_InterFace` classes, selecting between implementations in `driver.wx` and `driver.wx_api` based on the `server.auth_web` configuration setting. It does not expose any public functions or classes directly but influences the availability of other API components.

### `browser_manager.py`

This module provides a `BrowserManager` class for robust, human-like browser automation, focusing on article fetching with browser reuse, retry mechanisms, and delays.

#### Classes

##### `BrowserManager`

Manages the lifecycle of browser instances for web scraping tasks, including reuse, retries, and human-like delays.

**Constructor**

```python
BrowserManager(
    max_articles_per_browser: int = 7,
    max_retries: int = 3,
    min_delay: float = 2.0,
    max_delay: float = 5.0
)
```

Initializes the browser manager with configurable parameters for browser reuse, retry attempts, and delays.

**Methods**

*   **`fetch_article(self, url: str, mobile_mode: bool = False) -> Dict`**
    ```python
    await browser_manager.fetch_article(url, mobile_mode=False)
    ```
    Fetches a single article from the given URL, applying browser reuse and retry logic.

*   **`batch_fetch_articles(self, urls: list, mobile_mode: bool = False, progress_callback: Optional[Callable] = None) -> list`**
    ```python
    await browser_manager.batch_fetch_articles(urls, mobile_mode=False, progress_callback=None)
    ```
    Fetches a list of articles in a batch, incorporating browser reuse and retry logic. An optional `progress_callback` can be provided.

*   **`cleanup(self)`**
    ```python
    await browser_manager.cleanup()
    ```
    Cleans up all resources associated with the browser manager, including closing browser instances.

*   **`__aenter__(self)`**
    ```python
    async with BrowserManager(...) as manager:
        # ...
    ```
    Enables the use of `BrowserManager` as an asynchronous context manager.

*   **`__aexit__(self, exc_type, exc_val, exc_tb)`**
    ```python
    async with BrowserManager(...) as manager:
        # ...
    ```
    Ensures that `cleanup()` is called automatically when exiting the asynchronous context.

### `cookies.py`

This module provides utility functions for handling browser cookies, specifically for extracting expiry information.

#### Functions

*   **`expire(cookies: any) -> Optional[Dict]`**
    ```python
    expire(cookies)
    ```
    Analyzes a list or dictionary of cookies to find the `slave_sid` cookie's expiration time and calculates the remaining seconds until expiry.

### `playwright_driver.py`

This module provides a `PlaywrightController` class to manage Playwright browser instances, offering functionalities for starting browsers, handling cookies, navigating URLs, and applying anti-crawler scripts.

#### Classes

##### `PlaywrightController`

Manages Playwright browser instances, contexts, and pages.

**Constructor**

```python
PlaywrightController()
```

Initializes the Playwright controller, setting up system and Playwright related attributes.

**Methods**

*   **`start_browser(self, headless=True, mobile_mode=False, dis_image=True, browser_name="chromium", language="zh-CN", anti_crawler=True) -> Page`**
    ```python
    await controller.start_browser(headless=True, mobile_mode=False)
    ```
    Starts a new browser instance with configurable options such as headless mode, mobile emulation, image disabling, browser type, language, and anti-crawler measures. Returns a Playwright `Page` object.

*   **`is_browser_started(self) -> bool`**
    ```python
    controller.is_browser_started()
    ```
    Checks if the browser is currently started and connected.

*   **`string_to_json(self, json_string) -> Union[Dict, str]`**
    ```python
    controller.string_to_json(json_string)
    ```
    Converts a JSON string into a Python dictionary. Returns an empty string on parsing error.

*   **`parse_string_to_dict(self, kv_str: str) -> Dict`**
    ```python
    controller.parse_string_to_dict("key1=value1; key2=value2")
    ```
    Parses a key-value string (e.g., from cookies) into a dictionary.

*   **`add_cookies(self, cookies)`**
    ```python
    await controller.add_cookies(cookies_list)
    ```
    Adds a list of cookie dictionaries to the current browser context.

*   **`get_cookies(self) -> List[Dict]`**
    ```python
    await controller.get_cookies()
    ```
    Retrieves all cookies from the current browser context.

*   **`add_cookie(self, cookie)`**
    ```python
    await controller.add_cookie(single_cookie_dict)
    ```
    Adds a single cookie dictionary to the current browser context.

*   **`open_url(self, url, wait_until="domcontentloaded")`**
    ```python
    await controller.open_url("https://example.com")
    ```
    Navigates the browser page to the specified URL, waiting until a certain state (default: "domcontentloaded").

*   **`Close(self)`**
    ```python
    await controller.Close()
    ```
    Alias for `cleanup()`. Closes all browser resources.

*   **`cleanup(self)`**
    ```python
    await controller.cleanup()
    ```
    Cleans up all Playwright browser resources (page, context, browser, Playwright instance).

*   **`dict_to_json(self, data_dict) -> str`**
    ```python
    controller.dict_to_json({"key": "value"})
    ```
    Converts a Python dictionary to a JSON string.

*   **`is_async(self) -> bool`**
    ```python
    controller.is_async()
    ```
    Indicates that this controller uses the async Playwright API (always returns `True`).

*   **`_is_browser_installed(self, browser_name)`**
    ```python
    controller._is_browser_installed("chromium")
    ```
    Checks if a specific browser type (e.g., "chromium", "firefox") is installed in the Playwright environment.

#### Global Instances

*   **`ControlDriver`**: A global instance of `PlaywrightController`.

### `store.py`

This module provides a `KeyStore` class for secure, encrypted storage and retrieval of sensitive data, typically used for cookies or tokens.

#### Classes

##### `KeyStore`

Manages the encryption and decryption of data stored in a file.

**Constructor**

```python
KeyStore()
```

Initializes the `KeyStore` with a file crypto instance, using a predefined key.

**Methods**

*   **`save(self, text)`**
    ```python
    keystore.save(data_to_save)
    ```
    Encrypts and saves the provided text (or JSON serializable object) to the configured key file.

*   **`load(self)`**
    ```python
    keystore.load()
    ```
    Decrypts and loads data from the configured key file, returning it as a Python object (e.g., list of cookies).

#### Global Instances

*   **`Store`**: A global instance of `KeyStore`.

### `success.py`

This module manages the login status and information for WeChat, providing thread-safe access and a mechanism for sending success notifications.

#### Functions

*   **`setStatus(status: bool)`**
    ```python
    await setStatus(True)
    ```
    Asynchronously sets the global WeChat login status.

*   **`getStatus() -> bool`**
    ```python
    await getStatus()
    ```
    Asynchronously retrieves the global WeChat login status.

*   **`getLoginInfo() -> Any`**
    ```python
    await getLoginInfo()
    ```
    Asynchronously retrieves the stored WeChat login information.

*   **`setLoginInfo(info: Any)`**
    ```python
    await setLoginInfo(login_data)
    ```
    Asynchronously sets the global WeChat login information.

*   **`Success(data: dict, ext_data: dict = {})`**
    ```python
    await Success(login_data, account_info)
    ```
    Processes successful login data, updates the login status and information, and sends a system notice.

*   **`Success_Msg(data: dict, ext_data: dict = {})`**
    ```python
    Success_Msg(data, ext_data)
    ```
    Formats and sends a system notification for successful authorization.

### `token.py`

This module provides utility functions for managing WeChat authentication tokens and associated cookies.

#### Functions

*   **`set_token(data: any, ext_data: any = None)`**
    ```python
    set_token(token_data, account_info)
    ```
    Stores the WeChat login token, cookie string, fingerprint, and expiry information into the configuration. Optionally stores extended data.

*   **`get(key: str, default: str = "") -> str`**
    ```python
    get("token")
    ```
    Retrieves a specific configuration value (e.g., "token", "cookie") from the WeChat configuration.

### `wx_api.py`

This module provides the `WeChatAPI` class for programmatic interaction with the WeChat Public Platform, primarily for handling QR code-based login and session management. It also exposes several global helper functions.

#### Classes

##### `WeChatAPI`

Handles WeChat Public Platform login via QR code, manages session cookies, and provides utilities for token-based login and account information retrieval.

**Constructor**

```python
WeChatAPI()
```

Initializes the WeChatAPI client with base URLs, session headers, and state management variables.

**Methods**

*   **`get_qr_code(self, callback: Optional[Callable] = None, notice: Optional[Callable] = None) -> Dict[str, Any]`**
    ```python
    wechat_api.get_qr_code(login_success_callback, notice_callback)
    ```
    Initiates the QR code login process, fetches the QR code image, and starts monitoring its scan status. Returns QR code information.

*   **`login_with_token(self, token: str = "", cookies: Any = None) -> bool`**
    ```python
    wechat_api.login_with_token(my_token, my_cookies)
    ```
    Attempts to log in to the WeChat Public Platform using a provided token and cookies.

*   **`logout(self)`**
    ```python
    wechat_api.logout()
    ```
    Logs out the current session, clears cookies, and removes temporary files.

*   **`is_login_valid(self) -> bool`**
    ```python
    wechat_api.is_login_valid()
    ```
    Checks if the current login session is still valid by attempting to access the home page.

*   **`get_session_info(self) -> Dict[str, Any]`**
    ```python
    wechat_api.get_session_info()
    ```
    Retrieves the current session's login status, token, cookies, and calculated expiry.

*   **`switch_account(self, username:str="")`**
    ```python
    wechat_api.switch_account("gh_abcdef123456")
    ```
    (Internal use advised) Attempts to switch to a different WeChat public account.

*   **`Token(self, callback:Optional[Callable] = None)`**
    ```python
    wechat_api.Token(my_callback)
    ```
    (Alias for `login_with_token`) Attempts to log in using a token.

*   **`QRcode(self)`**
    ```python
    wechat_api.QRcode()
    ```
    Returns information about the current QR code state, including its path and existence.

*   **`GetCode(self, CallBack=None, Notice=None)`**
    ```python
    wechat_api.GetCode(my_callback, my_notice_callback)
    ```
    Starts the QR code generation and login monitoring process in a separate thread.

*   **`GetHasCode(self)`**
    ```python
    wechat_api.GetHasCode()
    ```
    Checks if the QR code image file exists.

*   **`check_lock(self)`**
    ```python
    wechat_api.check_lock()
    ```
    Checks if a login process lock file exists.

*   **`set_lock(self)`**
    ```python
    wechat_api.set_lock()
    ```
    Creates a lock file to indicate a login process is active.

*   **`release_lock(self)`**
    ```python
    wechat_api.release_lock()
    ```
    Removes the login process lock file.

*   **`HasLogin(self)`**
    ```python
    wechat_api.HasLogin()
    ```
    Checks if the user is currently logged in and if a QR code is not present.

*   **`Close(self)`**
    ```python
    wechat_api.Close()
    ```
    Performs a no-op, as resource cleanup is handled by other methods.

#### Global Instances

*   **`WeChat_api`**: A global instance of `WeChatAPI`.

#### Global Functions

*   **`get_qr_code(callback: Optional[Callable] = None, notice: Optional[Callable] = None) -> Dict[str, Any]`**
    ```python
    get_qr_code(login_success_callback, notice_callback)
    ```
    Wrapper for `WeChat_api.get_qr_code()`.

*   **`login_with_token(token: str = "", cookies: Optional[Dict[str, str]] = None, login_callback: Optional[Callable] = None) -> bool`**
    ```python
    login_with_token(my_token, my_cookies)
    ```
    Wrapper for `WeChat_api.login_with_token()`.

*   **`get_session_info() -> Dict[str, Any]`**
    ```python
    get_session_info()
    ```
    Wrapper for `WeChat_api.get_session_info()`.

*   **`logout()`**
    ```python
    logout()
    ```
    Wrapper for `WeChat_api.logout()`.

### `wx.py`

This module provides the `Wx` class for high-level WeChat Public Platform automation, including QR code and token-based login, session management, article data extraction, and account switching, leveraging Playwright.

#### Classes

##### `Wx`

High-level manager for WeChat Public Platform interactions, integrating Playwright for browser automation and handling login, session, and content extraction.

**Constructor**

```python
Wx()
```

Initializes the `Wx` instance, setting up Playwright controller, and cleaning up previous lock files and QR codes.

**Methods**

*   **`GetHasCode(self)`**
    ```python
    wx_instance.GetHasCode()
    ```
    Checks if the QR code image file exists.

*   **`extract_token_from_requests(self)`**
    ```python
    wx_instance.extract_token_from_requests()
    ```
    Attempts to extract the WeChat login token from the current browser page's URL, localStorage, sessionStorage, or cookies.

*   **`switch_account(self, username: str = "") -> bool`**
    ```python
    await wx_instance.switch_account("目标公众号ID或名称")
    ```
    Asynchronously switches to a different WeChat public account, requiring an active login session.

*   **`GetCode(self, CallBack=None, Notice=None)`**
    ```python
    wx_instance.GetCode(my_callback, my_notice)
    ```
    Starts the QR code login process by launching a browser and monitoring the QR code scan, running as a background asynchronous task.

*   **`QRcode(self)`**
    ```python
    wx_instance.QRcode()
    ```
    Returns information about the current QR code state, including its path and existence.

*   **`refresh_task(self) -> None`**
    ```python
    await wx_instance.refresh_task()
    ```
    Asynchronously refreshes the browser session and validates the login status. Raises an exception if the login has expired.

*   **`HasLogin(self) -> bool`**
    ```python
    await wx_instance.HasLogin()
    ```
    Asynchronously checks the current login status in a thread-safe manner.

*   **`schedule_refresh(self) -> None`**
    ```python
    await wx_instance.schedule_refresh()
    ```
    Sets up a periodic asynchronous task to refresh the login session, keeping it active.

*   **`Token(self, callback: Any = None, isClose: bool = True) -> Optional[Dict]`**
    ```python
    await wx_instance.Token(my_callback, isClose=True)
    ```
    Asynchronously attempts token-based authentication using stored credentials, validates the session, and updates cookies.

*   **`wxLogin(self, CallBack: Any = None, NeedExit: bool = True) -> Optional[Dict]`**
    ```python
    await wx_instance.wxLogin(my_callback, NeedExit=True)
    ```
    Asynchronously orchestrates the complete QR code login flow, including browser launch, QR code display, scan monitoring, and session data extraction.

*   **`format_token(self, cookies: List[Dict], token: str = "") -> Dict`**
    ```python
    wx_instance.format_token(browser_cookies, "extracted_token")
    ```
    Formats a list of browser cookies and an optional token into a standardized session dictionary, including calculated expiry.

*   **`Call_Success(self, has_extdata: bool = True) -> Optional[Dict]`**
    ```python
    await wx_instance.Call_Success()
    ```
    Asynchronously handles the post-login success logic, extracting session data and executing registered callbacks.

*   **`_extract_wechat_data(self) -> Dict[str, str]`**
    ```python
    await wx_instance._extract_wechat_data()
    ```
    Asynchronously scrapes WeChat public account metadata (name, logo, read counts, etc.) from the dashboard.

*   **`cleanup_resources(self) -> bool`**
    ```python
    await wx_instance.cleanup_resources()
    ```
    Asynchronously cleans up temporary files (QR code) and resets login state flags.

*   **`__aenter__(self) -> "Wx"`**
    ```python
    async with Wx() as wx:
        # ...
    ```
    Enables the use of `Wx` as an asynchronous context manager.

*   **`__aexit__(self, exc_type, exc_val, exc_tb) -> None`**
    ```python
    async with Wx() as wx:
        # ...
    ```
    Ensures `cleanup_resources()` and `controller.cleanup()` are called upon exiting the asynchronous context.

*   **`Close(self) -> bool`**
    ```python
    await wx_instance.Close()
    ```
    Asynchronously closes the underlying Playwright browser controller.

*   **`Clean(self) -> None`**
    ```python
    wx_instance.Clean()
    ```
    Synchronously removes the QR code image file.

*   **`expire_all_cookies(self) -> bool`**
    ```python
    wx_instance.expire_all_cookies()
    ```
    Synchronously clears all cookies from the browser context.

*   **`check_lock(self) -> bool`**
    ```python
    await wx_instance.check_lock()
    ```
    Asynchronously checks if a login process lock is active.

*   **`set_lock(self) -> None`**
    ```python
    wx_instance.set_lock()
    ```
    Synchronously creates a lock file.

*   **`release_lock(self) -> bool`**
    ```python
    wx_instance.release_lock()
    ```
    Synchronously removes the lock file.

#### Global Instances

*   **`WX_API`**: A global instance of `Wx`.

#### Global Functions

*   **`GetCode(CallBack: any = None, NeedExit=True)`**
    ```python
    GetCode(my_callback, NeedExit=True)
    ```
    Wrapper for `WX_API.GetCode()`.

### `wxarticle.py`

This module provides the `WXArticleFetcher` class for fetching, parsing, and cleaning WeChat public account articles using Playwright.

#### Classes

##### `WXArticleFetcher`

Fetches and processes WeChat public account articles, including content extraction, image handling, and metadata parsing.

**Constructor**

```python
WXArticleFetcher(page=None, wait_timeout: int = 10000)
```

Initializes the article fetcher with a Playwright `Page` object and an optional wait timeout.

**Methods**

*   **`convert_publish_time_to_timestamp(self, publish_time_str: str) -> int`**
    ```python
    fetcher.convert_publish_time_to_timestamp("2024年03月24日 17:14")
    ```
    Converts various formats of publish time strings into a Unix timestamp.

*   **`extract_biz_from_source(self, url: str, page=None) -> str`**
    ```python
    await fetcher.extract_biz_from_source("https://mp.weixin.qq.com/s/...", page)
    ```
    Asynchronously extracts the `__biz` parameter from an article URL or the page source.

*   **`extract_id_from_url(self, url: str) -> str`**
    ```python
    fetcher.extract_id_from_url("https://mp.weixin.qq.com/s/YTHUfxzWCjSRnfElEkL2Xg")
    ```
    Extracts the unique ID from a WeChat article URL.

*   **`FixArticle(self, urls: list = [], mp_id: str = "") -> bool`**
    ```python
    await fetcher.FixArticle(article_urls, "公众号ID")
    ```
    Asynchronously processes a batch of article URLs to fetch their content and update them in a backend system.

*   **`get_article_content(self, url: str) -> Dict`**
    ```python
    await fetcher.get_article_content("https://mp.weixin.qq.com/s/...")
    ```
    Asynchronously fetches the detailed content of a single WeChat article, including title, author, publish time, HTML content, and images.

*   **`export_to_pdf(self, title=None)`**
    ```python
    fetcher.export_to_pdf("MyArticleTitle")
    ```
    Exports the current article content to a PDF file. (Note: Functionality depends on `export.pdf.enable` config).

*   **`fix_images(self, content: str) -> str`**
    ```python
    fetcher.fix_images(html_content)
    ```
    Modifies image `src` and `style` attributes within HTML content for better display or proxying.

*   **`get_image_url(self, url: str) -> str`**
    ```python
    fetcher.get_image_url("original_image_path.jpg")
    ```
    Constructs a full URL for an image, potentially using a base URL from configuration.

*   **`get_description(self, content: str, length: int = 200) -> str`**
    ```python
    fetcher.get_description(html_content, 150)
    ```
    Extracts a plain text description from HTML content, truncating it to a specified length.

*   **`proxy_images(self, content: str) -> str`**
    ```python
    fetcher.proxy_images(html_content)
    ```
    Rewrites image `src` attributes in HTML content to point to a proxy URL, and adjusts image styles.

*   **`clean_article_content(html_content: str)`** (Static Method)
    ```python
    WXArticleFetcher.clean_article_content(raw_html)
    ```
    Cleans and processes raw HTML content of an article, removing unwanted elements and attributes.

### `extdata/like.py`

This module contains a `mitmproxy` addon (`RequestHandler`) designed to intercept and process HTTP traffic, specifically for extracting read counts from WeChat public platform responses.

#### Classes

##### `RequestHandler`

A `mitmproxy` addon that intercepts HTTP requests and responses, with specific logic to extract and log read counts from WeChat public platform articles.

**Constructor**

```python
RequestHandler()
```

Initializes the request handler.

**Methods**

*   **`request(self, flow: http.HTTPFlow)`**
    ```python
    # Called by mitmproxy for each outgoing request
    ```
    Intercepts and processes outgoing HTTP requests. Currently, it performs a pass-through.

*   **`response(self, flow: http.HTTPFlow)`**
    ```python
    # Called by mitmproxy for each incoming response
    ```
    Intercepts and processes incoming HTTP responses. If the response is from `mp.weixin.qq.com` and contains `read_num` in its JSON payload, it extracts and prints the read count.

*   **`run_proxy(self)`**
    ```python
    request_handler.run_proxy()
    ```
    Starts the `mitmproxy` listener to enable request/response interception.

#### Global Functions

*   **`run_proxy()`**
    ```python
    run_proxy()
    ```
    Starts the `mitmproxy` proxy server with the `RequestHandler` addon. This function is typically called when the script is executed directly.