# Module: `core/wx`

This directory contains modules for interacting with WeChat, primarily focused on gathering articles from WeChat Official Accounts. It provides functionalities for searching official accounts, extracting article content, and managing the gathering process with different strategies (API, App-like browser, Web-like browser).

## Modules

### `__init__.py`
This module serves as the package initializer for `core.wx`. It imports and re-exports functionalities from other sub-modules, such as `search_Biz` from `core.wx.base`, making them directly accessible from the `core.wx` package.

### `base.py`
This module defines the foundational classes and methods for WeChat article gathering. It includes:
-   **`PageCrawlStats`**: A utility class for tracking statistics and timing during page-level crawls.
-   **`WxGather`**: The base class that encapsulates common functionalities required for gathering WeChat articles, such as managing cookies and tokens, handling headers, content extraction (synchronous), error handling, and overall job management. It also provides methods to switch between different gathering models (API, App, Web).

### `cfg.py`
This module handles configuration loading specific to WeChat operations. It primarily imports and re-exports `wx_cfg` and `cfg` objects from `driver.token`, making configuration settings easily accessible across the `core.wx` package. It also disables `urllib3` warnings.

### `wx.py`
This module provides lower-level, standalone functions for WeChat interaction, often complementing the functionalities in `base.py`. Key features include:
-   Configuration management (`set_config`, `save_config`).
-   Direct interaction with WeChat API endpoints for searching businesses (`search_Biz`) and retrieving article lists (`get_Articles`).
-   Content extraction (`content_extract`) and article ID parsing (`get_id`).
-   Database interaction for managing article lists (`get_list`) and updating WeChat Official Account statuses (`update_mps`).

## Usage

The `core/wx` package offers a flexible way to interact with WeChat Official Account data. The `WxGather` class in `base.py` is the central component for initiating and managing gathering tasks. The `__init__.py` makes some core functionalities directly accessible.

### Example: Searching for WeChat Official Accounts

You can use the `search_Biz` function directly from the `core.wx` package (which is re-exported from `core.wx.base`).

```python
from core.wx import search_Biz

# Search for official accounts containing "Google Deepmind"
results = search_Biz(kw="Google Deepmind", limit=3)

if results and 'biz_list' in results:
    print("Found Official Accounts:")
    for biz in results['biz_list']:
        print(f"  - Name: {biz.get('nickname')}, Fake ID: {biz.get('fakeid')}")
else:
    print("No official accounts found or an error occurred.")
```

### Example: Using `WxGather` for Article Gathering

For more complex gathering tasks, especially those involving browser automation (which are implemented in `core.wx.model` and integrated via `WxGather.Model`), you would typically use the `WxGather` class. A basic synchronous example is shown below (for asynchronous examples, refer to the `core/wx/model` documentation, e.g., `MpsAppMsg` or `MpsWeb` usage).

```python
import asyncio
from core.wx.base import WxGather
from core.models import Feed # Assuming Feed is defined in core.models

# Define a simple callback function to process each article
def my_article_callback(article_data: dict) -> bool:
    print(f"Processing article: {article_data.get('title')}")
    # In a real scenario, you would save this to a database, etc.
    # Return True if successfully processed, False otherwise
    return True

async def gather_example():
    gatherer = WxGather()
    mp_id = "your_mp_id_here" # Replace with actual MP ID
    faker_id = "your_faker_id_here" # Replace with actual faker ID

    try:
        # Assuming you have a specific model for gathering, e.g., MpsApi for API-based
        # For browser-based gathering (App/Web), you would use:
        # gatherer_instance = gatherer.Model(type="app") # or "web"
        # Then call await gatherer_instance.get_Articles(...)
        # For simplicity, here we're demonstrating the base WxGather's search_Biz
        # For actual article fetching, you'd likely use a specific model from core/wx/model

        # This example uses search_Biz which is synchronous in WxGather.
        # For article fetching, you'd normally instantiate MpsApi, MpsAppMsg, or MpsWeb
        # and call their get_Articles method.
        print(f"Starting gathering process for MP ID: {mp_id}")

        # If using MpsApi directly (synchronous):
        # from core.wx.model.api import MpsApi
        # api_gatherer = MpsApi()
        # api_gatherer.get_Articles(
        #     faker_id=faker_id,
        #     Mps_id=mp_id,
        #     Mps_title="Example MP Title",
        #     CallBack=my_article_callback,
        #     MaxPage=1,
        #     Gather_Content=False
        # )
        
        # Demonstrating the WxGather Start/Over lifecycle (without actual article fetch here)
        gatherer.Start(mp_id=mp_id)
        # In a real application, article fetching logic would go here,
        # likely calling a specialized model's get_Articles.
        gatherer.Over(CallBack=lambda articles: print(f"Gathering finished. Total articles collected: {len(articles)}"))

    except Exception as e:
        print(f"An error occurred during gathering: {e}")
    finally:
        # Ensure cleanup is called if using browser-based models (MpsAppMsg/MpsWeb)
        # if hasattr(gatherer_instance, 'cleanup'):
        #     await gatherer_instance.cleanup()
        pass

# To run the example (for synchronous parts, or if gather_example was made synchronous):
# If gather_example is truly async (e.g., using MpsAppMsg/MpsWeb), uncomment and run:
# asyncio.run(gather_example())

# For synchronous parts or if no async operations:
# The search_Biz example above is directly runnable.
