"""
Browser Lifecycle Manager for WeChat MP Article Fetching

Implements:
1. Browser instance reuse (5-10 articles per browser)
2. Retry mechanism with exponential backoff
3. Human-like delays between requests
"""

import asyncio
import random
from typing import Dict, Optional, Callable
from playwright.async_api import Page
from core.print import print_info, print_warning, print_error, print_success


class BrowserManager:
    """Manages browser lifecycle with reuse and retry logic"""

    def __init__(
        self,
        max_articles_per_browser: int = 7,
        max_retries: int = 3,
        min_delay: float = 2.0,
        max_delay: float = 5.0
    ):
        """
        Initialize browser manager

        Args:
            max_articles_per_browser: Maximum articles to fetch per browser instance (default: 7)
            max_retries: Maximum retry attempts (default: 3)
            min_delay: Minimum delay between requests in seconds (default: 2.0)
            max_delay: Maximum delay between requests in seconds (default: 5.0)
        """
        from .playwright_driver import PlaywrightController

        self.max_articles_per_browser = max_articles_per_browser
        self.max_retries = max_retries
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.controller = PlaywrightController()
        self.articles_fetched = 0
        self.browser_started = False

    async def _start_browser_if_needed(self, mobile_mode: bool = False):
        """Start browser if not already started"""
        if not self.browser_started:
            print_info("Starting new browser instance")
            await self.controller.start_browser(mobile_mode=mobile_mode)
            self.browser_started = True
            self.articles_fetched = 0

    def _should_restart_browser(self) -> bool:
        """Check if browser should be restarted"""
        return self.articles_fetched >= self.max_articles_per_browser

    async def _restart_browser(self, mobile_mode: bool = False):
        """Restart browser instance"""
        print_warning(f"Restarting browser after {self.articles_fetched} articles")
        await self.controller.cleanup()
        self.browser_started = False
        await self._start_browser_if_needed(mobile_mode)

    async def _human_delay(self):
        """Add human-like random delay between requests"""
        delay = random.uniform(self.min_delay, self.max_delay)
        print_info(f"Waiting {delay:.2f}s before next request (human-like delay)")
        await asyncio.sleep(delay)

    async def _fetch_with_retry(
        self,
        url: str,
        fetch_func: Callable,
        *args,
        **kwargs
    ) -> Dict:
        """
        Fetch article with retry mechanism

        Args:
            url: Article URL
            fetch_func: Async function to call for fetching
            *args, **kwargs: Arguments to pass to fetch_func

        Returns:
            Article data dictionary

        Raises:
            Exception: If all retries exhausted
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    print_warning(f"Retry attempt {attempt}/{self.max_retries} for {url}")

                result = await fetch_func(*args, **kwargs)

                # Check for common error conditions
                if result.get("content") == "DELETED":
                    print_warning(f"Article marked as deleted: {url}")
                    return result

                if not result.get("content") or result.get("content") == "":
                    if attempt < self.max_retries:
                        print_warning(f"Empty content on attempt {attempt}, retrying...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                        continue
                    else:
                        print_error(f"Failed to fetch content after {self.max_retries} attempts")
                        return result

                return result

            except Exception as e:
                last_error = e
                print_error(f"Attempt {attempt}/{self.max_retries} failed: {str(e)}")

                if attempt < self.max_retries:
                    # Exponential backoff: 2^attempt seconds (2s, 4s, 8s)
                    backoff_time = 2 ** attempt
                    print_warning(f"Waiting {backoff_time}s before retry (exponential backoff)")
                    await asyncio.sleep(backoff_time)
                else:
                    print_error(f"All {self.max_retries} retry attempts exhausted")

        # All retries failed
        raise Exception(f"Failed to fetch article after {self.max_retries} attempts: {last_error}")

    async def fetch_article(
        self,
        url: str,
        mobile_mode: bool = False
    ) -> Dict:
        """
        Fetch article with browser reuse and retry logic

        Args:
            url: Article URL
            mobile_mode: Whether to use mobile mode

        Returns:
            Article data dictionary
        """
        from .wxarticle import WXArticleFetcher

        # Start browser if needed
        await self._start_browser_if_needed(mobile_mode)

        # Check if browser needs restart
        if self._should_restart_browser():
            await self._restart_browser(mobile_mode)

        try:
            # Create fetcher with current page
            fetcher = WXArticleFetcher(page=self.controller.page)

            # Fetch with retry - need to call async method
            result = await self._fetch_with_retry(url, fetcher.async_get_article_content, url)

            # Increment counter
            self.articles_fetched += 1
            print_success(f"Successfully fetched article {self.articles_fetched}/{self.max_articles_per_browser}")

            # Add delay before next request (not on last article before restart)
            if not self._should_restart_browser():
                await self._human_delay()

            return result

        except Exception as e:
            print_error(f"Error fetching article: {str(e)}")
            # On error, restart browser to get fresh state
            await self._restart_browser(mobile_mode)
            raise

    async def batch_fetch_articles(
        self,
        urls: list,
        mobile_mode: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> list:
        """
        Batch fetch multiple articles with browser reuse

        Args:
            urls: List of article URLs
            mobile_mode: Whether to use mobile mode
            progress_callback: Optional async callback function(current, total, result)

        Returns:
            List of article data dictionaries
        """
        results = []
        total = len(urls)

        for idx, url in enumerate(urls, 1):
            try:
                print_info(f"Fetching article {idx}/{total}: {url}")

                result = await self.fetch_article(url, mobile_mode)
                results.append(result)

                # Call progress callback if provided
                if progress_callback:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(idx, total, result)
                    else:
                        progress_callback(idx, total, result)

            except Exception as e:
                print_error(f"Failed to fetch article {idx}/{total} ({url}): {str(e)}")
                # Add error result
                results.append({
                    "url": url,
                    "error": str(e),
                    "content": "",
                    "title": "Error"
                })

        print_success(f"Batch fetch complete: {len(results)} articles processed")
        return results

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser_started:
            print_info("Cleaning up browser manager")
            await self.controller.cleanup()
            self.browser_started = False
            self.articles_fetched = 0

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - auto cleanup"""
        await self.cleanup()
        return False

    def __del__(self):
        """Destructor - ensure cleanup"""
        try:
            # Note: Can't use async cleanup in __del__, just log warning
            if self.browser_started:
                print_warning("BrowserManager destroyed without proper cleanup")
        except:
            pass
