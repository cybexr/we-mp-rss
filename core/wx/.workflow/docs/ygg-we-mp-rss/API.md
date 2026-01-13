# API Documentation for `core/wx`

This document provides API-level documentation for the `core/wx` module, detailing classes and functions with their signatures.

## Module `core.wx` (`__init__.py`)

- `search_Biz(kw: str = "", limit=5, offset=0) -> Any`
    - Searches for WeChat Official Accounts (Biz).

## Module `core.wx.base` (`base.py`)

### Class `PageCrawlStats`

Tracks page-level crawl statistics including articles discovered, records inserted, and timing.

- `__init__(self, mp_name: str = "", page_num: int = 0)`
- `start(self)`
    - Records the start time of the page crawl.
- `complete(self, articles_found: int, records_inserted: int)`
    - Records completion with counts.
- `elapsed_seconds(self) -> float`
    - Calculates execution time in seconds.
- `format_log(self) -> str`
    - Generates formatted log message for this page crawl.

### Class `WxGather`

Base class for WeChat article gathering operations.

- `__init__(self, is_add: bool = False)`
- `all_count(self) -> int`
    - Returns the total number of articles.
- `RecordAid(self, aid: str)`
    - Records an article ID.
- `HasGathered(self, aid: str) -> bool`
    - Checks if an article ID has already been gathered and records it if not.
- `Model(self, type=None) -> Any`
    - Returns an instance of a specific WeChat gathering model (app, web, or api).
- `increment_page_stats(self, articles_found: int, records_inserted: int)`
    - Accumulates total statistics from each page.
- `get_token(self)`
    - Retrieves token and cookie information.
- `fix_header(self, url) -> dict`
    - Fixes and returns request headers with a random User-Agent.
- `content_extract(self, url) -> str`
    - Extracts content from a given URL (synchronous version).
- `Wait(self, min=10, max=60, tips: str = "")`
    - Pauses execution for a random duration.
- `FillBack(self, CallBack=None, data=None, Ext_Data=None)`
    - Fills back data using a callback function and appends articles.
- `search_Biz(self, kw: str = "", limit=10, offset=0) -> dict`
    - Searches for WeChat Official Accounts (Biz).
- `Start(self, mp_id=None)`
    - Initializes the gathering process.
- `Item_Over(self, item=None, CallBack=None)`
    - Handles post-item processing and cookie saving.
- `Error(self, error: str, code=None)`
    - Handles and logs errors, potentially triggering re-authentication.
- `Over(self, CallBack=None)`
    - Cleans up and provides a summary of the gathering process.
- `dateformat(self, timestamp: any) -> str`
    - Formats a timestamp into a datetime string.
- `remove_common_html_elements(self, html_content: str) -> str`
    - Removes common HTML elements from content.
- `update_mps(self, mp_id: str, mp: Feed)`
    - Updates the synchronization status and time of a WeChat Official Account.
