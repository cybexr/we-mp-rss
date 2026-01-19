# APIs Module Documentation

## Purpose and Scope
The `apis` module contains all FastAPI route handlers and API endpoint definitions for the WeChat MP RSS system. This module serves as the web interface layer, handling HTTP requests, authentication, and response formatting. It exposes a comprehensive set of APIs for managing articles, official accounts (MPs), RSS feeds, system configurations, user accounts, and various utility functions.

## Structure Overview
The `apis` module is organized into individual Python files, each typically corresponding to a logical group of related API endpoints. This structure promotes modularity and maintainability.

### File Organization
- `article.py`: Manages article-related operations.
- `auth.py`: Handles user authentication and authorization.
- `base.py`: Provides foundational utilities like response models and search formatting.
- `cache.py`: (No API endpoints documented in this analysis, likely internal caching logic)
- `config_management.py`: Manages system configuration settings.
- `export.py`: Handles data export and import functionalities (CSV, OPML).
- `github_update.py`: Provides endpoints for managing code updates and Git repository operations.
- `message_task.py`: Manages scheduled message tasks.
- `mps.py`: Deals with WeChat Official Account management.
- `queue.py`: Monitors and controls the background task queues.
- `res.py`: Implements resource reverse proxy and caching for images.
- `rss.py`: Generates and serves RSS feeds.
- `sys_info.py`: Provides various system-level information.
- `tags.py`: Manages tags for organizing Official Accounts.
- `tools.py`: Contains miscellaneous utility endpoints, including article export.
- `user.py`: Manages user profiles and administration.
- `ver.py`: Defines API version constants.

## Key Components

### `base.py`
- Description: Core response utilities and search keyword formatting.
- Responsibilities: Standardizing API response format, providing helper functions for success/error responses, and preparing search query conditions.
- Key Methods:
  #### `BaseResponse(BaseModel, Generic[T])`
  - Purpose: A generic Pydantic model for standardized API responses.
  - Parameters:
    - `code` (int): HTTP status code. Default: 0 (success).
    - `message` (str): Human-readable status message. Default: "success".
    - `data` (Optional[T]): Optional payload of any type.
  #### `success_response(data=None, message="success")`
  - Purpose: Creates a successful API response dictionary.
  - Parameters:
    - `data` (Any, optional): The payload to return. Default: `None`.
    - `message` (str, optional): A custom success message. Default: "success".
  - Returns: (dict) A dictionary representing a successful API response.
  #### `error_response(code: int, message: str, data=None)`
  - Purpose: Creates an error API response dictionary.
  - Parameters:
    - `code` (int): The error code.
    - `message` (str): A human-readable error message.
    - `data` (Any, optional): Additional error data. Default: `None`.
  - Returns: (dict) A dictionary representing an error API response.
  #### `format_search_kw(keyword: str)`
  - Purpose: Formats a search keyword into an SQLAlchemy `or_` rule for filtering `Article.title`.
  - Parameters:
    - `keyword` (str): The search keyword, can contain "-" or "|" as delimiters.
  - Returns: (SQLAlchemy `or_` clause) A SQLAlchemy clause for title filtering.

### `auth.py`
- Description: Handles user authentication, token management, and WeChat login flows.
- Responsibilities: Providing endpoints for user login, token refresh, QR code authentication, and token verification.
- Exported APIs:
  - `GET /auth/qr/code` - Get Login QR Code URL (Admin only)
  - `GET /auth/qr/image` - Get Login QR Code Image
  - `GET /auth/qr/status` - Get Scan Status
  - `GET /auth/qr/over` - Finalize QR Code Login
  - `POST /auth/login` - User Login (returns JWT)
  - `POST /auth/token` - Get Token (alternative login, returns JWT)
  - `POST /auth/logout` - User Logout
  - `POST /auth/refresh` - Refresh JWT Token
  - `GET /auth/verify` - Verify Token Validity

### `article.py`
- Description: Provides CRUD and utility operations for article content.
- Responsibilities: Listing, retrieving, deleting, and re-extracting articles, as well as managing article read status and cleaning up orphaned/duplicate entries.
- Exported APIs:
  - `DELETE /articles/clean` - Clean Orphan Articles
  - `PUT /articles/{article_id}/read` - Change Article Read Status
  - `DELETE /articles/clean_duplicate_articles` - Clean Duplicate Articles
  - `GET /articles` (and `POST /articles`) - Get Article List (paginated, filtered)
  - `GET /articles/{article_id}` - Get Article Details
  - `DELETE /articles/{article_id}` - Delete Article (soft delete)
  - `GET /articles/{article_id}/next` - Get Next Article
  - `GET /articles/{article_id}/prev` - Get Previous Article
  - `POST /articles/{article_id}/reextract` - Re-extract Article Content

### `config_management.py`
- Description: Manages system-wide configuration settings.
- Responsibilities: Providing interfaces to list, retrieve, create, update, and delete configuration items.
- Key Models:
  #### `ConfigManagementCreate(BaseModel)`
  - Purpose: Request model for creating or updating configuration items.
  - Parameters:
    - `config_key` (str): The unique key for the configuration item.
    - `config_value` (str): The value associated with the configuration key.
    - `description` (Optional[str]): An optional description for the configuration item.
- Exported APIs:
  - `GET /configs` - List Configuration Items (paginated)
  - `GET /configs/{config_key}` - Get Single Configuration Item Details
  - `POST /configs` - Create Configuration Item
  - `PUT /configs/{config_key}` - Update Configuration Item
  - `DELETE /configs/{config_key}` - Delete Configuration Item

### `export.py`
- Description: Handles the import and export of Official Account and tag data in various formats.
- Responsibilities: Providing functionality to export lists as CSV/OPML and import from CSV.
- Exported APIs:
  - `GET /export/mps/export` - Export Official Account List (CSV)
  - `POST /export/mps/import` - Import Official Account List (CSV)
  - `GET /export/mps/opml` - Export Official Account List as OPML
  - `GET /export/tags` - Export Tag List (CSV)
  - `POST /export/tags/import` - Import Tag List (CSV)

### `github_update.py`
- Description: Manages code updates and Git repository operations directly from GitHub.
- Responsibilities: Checking repository status, updating code, viewing commit history, rolling back to previous commits, and listing branches.
- Key Models:
  #### `UpdateRequest(BaseModel)`
  - Purpose: Request model for initiating a code update.
  - Parameters:
    - `branch` (Optional[str]): Target branch.
    - `backup` (bool): Create backup. Default: `True`.
    - `path` (Optional[str]): Repository path.
  #### `RollbackRequest(BaseModel)`
  - Purpose: Request model for rolling back code.
  - Parameters:
    - `commit_hash` (str): Full commit hash.
    - `path` (Optional[str]): Repository path.
  #### `UpdateResponse(BaseModel)`
  - Purpose: Response model for update operations.
  - Parameters: `success`, `message`, `backup_created`, `backup_path`, `updated_files`, `error`.
  #### `StatusResponse(BaseModel)`
  - Purpose: Response model for Git repository status.
  - Parameters: `is_git_repo`, `current_branch`, `has_changes`, `remote_url`, `last_commit`, `ahead_commits`, `behind_commits`, `error`.
  #### `CommitInfo(BaseModel)`
  - Purpose: Model for a single commit's information.
  - Parameters: `hash`, `message`, `author`, `date`.
- Exported APIs:
  - `GET /github/status` - Check Git Repository Status
  - `POST /github/update` - Update Code from GitHub
  - `GET /github/commits` - Get Commit History
  - `POST /github/rollback` - Rollback to Specific Commit
  - `GET /github/branches` - Get All Branches

### `message_task.py`
- Description: Manages scheduled message tasks for pushing content or notifications.
- Responsibilities: Listing, retrieving, creating, updating, deleting, testing, and running message tasks.
- Key Models:
  #### `MessageTaskCreate(BaseModel)`
  - Purpose: Request model for creating or updating message tasks.
  - Parameters:
    - `message_template` (str): Template for message.
    - `web_hook_url` (str): Webhook URL.
    - `mps_id` (str, optional): Associated WeChat Official Account IDs (JSON string).
    - `name` (str, optional): Task name.
    - `message_type` (int, optional): Message type.
    - `cron_exp` (str, optional): Cron expression.
    - `status` (Optional[int]): Task status.
- Exported APIs:
  - `GET /message_tasks` - List Message Tasks (paginated)
  - `GET /message_tasks/{task_id}` - Get Single Message Task Details
  - `GET /message_tasks/message/test/{task_id}` - Test Message (retrieves task details)
  - `GET /message_tasks/{task_id}/run` - Execute Single Message Task
  - `POST /message_tasks` - Create Message Task
  - `PUT /message_tasks/{task_id}` - Update Message Task
  - `PUT /message_tasks/job/fresh` - Reload Tasks (reloads all message tasks)
  - `DELETE /message_tasks/{task_id}` - Delete Message Task

### `mps.py`
- Description: Handles the management of WeChat Official Accounts.
- Responsibilities: Searching, listing, adding, updating, and deleting Official Accounts, as well as managing their categories and updating their articles.
- Exported APIs:
  - `GET /mps/search/{kw}` - Search Official Accounts
  - `GET /mps` - Get Official Account List (paginated, with article stats)
  - `GET /mps/categories` - Get Official Account Category List
  - `GET /mps/update/{mp_id}` - Update Official Account Articles (submits background task)
  - `GET /mps/jobs/{job_id}` - Query Official Account Article Update Task Status
  - `GET /mps/{mp_id}` - Get Official Account Details
  - `POST /mps/by_article` - Get Official Account Details by Article Link
  - `POST /mps` - Add Official Account (creates or updates)
  - `PUT /mps/batch-category` - Batch Update Official Account Category
  - `PUT /mps/{mp_id}` - Update Official Account Information
  - `DELETE /mps/{mp_id}` - Delete Subscription

### `queue.py`
- Description: Provides monitoring and control for the dual-queue system responsible for WeChat RSS collection.
- Responsibilities: Offering health checks, status reporting, and control (pause/resume) over the article list collection and content extraction queues, along with job tracking.
- Key Models:
  #### `HealthCheckResponse(BaseModel)`
  - Purpose: Response model for the queue system's health check.
  - Parameters: `status`, `timestamp`, `queues`.
  #### `QueueStatusResponse(BaseModel)`
  - Purpose: Response model for individual queue status.
  - Parameters: `name`, `is_paused`, `is_running`, `pending_tasks`, `tag`.
  #### `JobStatusResponse(BaseModel)`
  - Purpose: Response model for the status of a single job.
  - Parameters: `job_id`, `status`, `queue_name`, `task_name`, `created_at`, `updated_at`, `progress`, `error`.
- Exported APIs:
  - `GET /queues/health` - Health Check (overall system health)
  - `GET /queues/status` - Get Queue Status (individual queue status)
  - `POST /queues/list/pause` - Pause Article List Collection Queue
  - `POST /queues/list/resume` - Resume Article List Collection Queue
  - `POST /queues/content/pause` - Pause Article Content Extraction Queue
  - `POST /queues/content/resume` - Resume Article Content Extraction Queue
  - `GET /queues/jobs` - Get Task List (jobs in queues)

### `res.py`
- Description: Implements a resource reverse proxy with caching capabilities, primarily for WeChat image assets.
- Responsibilities: Serving images from allowed WeChat domains through a local cache to improve performance and potentially bypass certain access restrictions.
- Key Methods:
  #### `cache_image_url(url: str, method: str = 'GET') -> bool`
  - Purpose: Downloads and caches an image from a given URL to the local filesystem.
  - Parameters:
    - `url` (str): The image URL to cache.
    - `method` (str, optional): HTTP method (default: 'GET').
  - Returns: (bool) `True` if caching succeeded or already cached, `False` on failure.
- Exported APIs:
  - `ALL /res/logo/{path:path}` - Resource Reverse Proxy (for specific WeChat image hosts)

### `rss.py`
- Description: Generates and serves various RSS feeds based on subscribed WeChat Official Accounts and articles.
- Responsibilities: Providing aggregated feeds, individual account feeds, cached article content viewing, and feed generation in different formats (XML, Atom, JSON, JMD).
- Exported APIs:
  - `GET /rss/{feed_id}/api` - Get Specific RSS Feed Details
  - `GET /rss/fresh` - Update and Get RSS Subscription List
  - `GET /rss` - Get RSS Subscription List (cached or generated)
  - `GET /rss/content/{content_id}` - Get Cached Article Content (HTML view)
  - `POST /rss/{feed_id}/fresh` - Update and Get Official Account Article RSS (currently commented out)
  - `GET /rss/{feed_id}` - Get Official Account Articles (RSS feed for a specific MP or aggregated)
  - `GET /feed/{feed_id}.{ext}` - Get Official Account Article Source (formatted feed)
  - `GET /feed/search/{kw}/{feed_id}.{ext}` - Get Official Account Article Source with Search
  - `GET /feed/tag/{tag_id}.{ext}` - Get Official Account Article Source by Tag

### `sys_info.py`
- Description: Provides various system-level information and diagnostic endpoints.
- Responsibilities: Reporting basic system info, resource usage, and detailed system configuration and status.
- Exported APIs:
  - `GET /sys/base_info` - Basic Information (API version, Docker, UI names)
  - `GET /sys/resources` - Get System Resource Usage (CPU, memory, disk, queue)
  - `GET /sys/info` - Get System Information (OS, Python, uptime, Git, WeChat login, article processing, queue)

### `tags.py`
- Description: Manages tags for organizing WeChat Official Accounts.
- Responsibilities: Listing, creating, retrieving, updating, and deleting tags.
- Key Models:
  #### `TagsCreate(BaseModel)`
  - Purpose: Request model for creating or updating tags.
  - Parameters: `name`, `cover`, `intro`, `mps_id`, `status`.
- Exported APIs:
  - `GET /tags` - Get Tag List (paginated)
  - `POST /tags` - Create New Tag
  - `GET /tags/{tag_id}` - Get Single Tag Details
  - `PUT /tags/{tag_id}` - Update Tag Information
  - `DELETE /tags/{tag_id}` - Delete Tag

### `tools.py`
- Description: Contains miscellaneous utility endpoints, primarily for exporting articles into various document formats.
- Responsibilities: Initiating article export tasks, managing exported files (download, list, delete).
- Key Models:
  #### `ExportArticlesRequest(BaseModel)`
  - Purpose: Request model for initiating an article export.
  - Parameters: `mp_id`, `doc_id`, `page_size`, `page_count`, `add_title`, `remove_images`, `remove_links`, `export_md`, `export_docx`, `export_json`, `export_csv`, `export_pdf`, `zip_filename`.
  #### `ExportArticlesResponse(BaseModel)`
  - Purpose: Response model for successful article export initiation.
  - Parameters: `record_count`, `export_path`, `message`.
  #### `ExportFileInfo(BaseModel)`
  - Purpose: Model for describing an exported file.
  - Parameters: `filename`, `size`, `created_time`, `modified_time`.
  #### `DeleteFileRequest(BaseModel)`
  - Purpose: Request model for deleting an exported file.
  - Parameters: `filename`, `mp_id`.
- Exported APIs:
  - `POST /tools/export/articles` - Export Articles (asynchronously to various formats)
  - `GET /tools/export/download` - Download Exported File
  - `GET /tools/export/list` - List Exported Files
  - `DELETE /tools/export/delete` - Delete Exported File
  - `DELETE /tools/export/delete-by-query` - Delete Exported File (Query Parameters)

### `user.py`
- Description: Manages user profiles and administration.
- Responsibilities: Retrieving user information, listing users (admin only), adding users (admin only), updating user profiles, changing passwords, and handling avatar/file uploads.
- Exported APIs:
  - `GET /user` - Get User Information
  - `GET /user/list` - Get User List (Admin only)
  - `POST /user` - Add User (Admin only)
  - `PUT /user` - Update User Profile
  - `PUT /user/password` - Change Password
  - `POST /user/avatar` - Upload User Avatar
  - `POST /user/upload` - Upload File (generic)

### `ver.py`
- Description: Defines API version constants.
- Responsibilities: Providing the base path for the API.
- Key Constants:
  - `API_VERSION` (str): `"/api/v1/wx"` - Defines the base path for the API version.

## Dependencies

### Internal Dependencies
- `core.auth`: Authentication utilities, token management, `get_current_user`.
- `core.db`: Database session management (`DB.get_session`, `DB.async_session_factory`).
- `core.models`: SQLAlchemy model definitions (`Article`, `Feed`, `MessageTask`, `ConfigManagement`, `Tags`, `User`).
- `core.config`: Configuration management (`cfg`).
- `core.queue`: Background task queue management (`GlobalQueueManager`, `TaskQueue`).
- `core.wx`: WeChat API interactions (`search_Biz`, `WxGather`).
- `core.res`: Resource handling utilities (`save_avatar_locally`).
- `core.print`: Logging and console output utilities (`print_error`, `print_info`, etc.).
- `driver.*`: External service integrations (e.g., `driver.base.WX_API`, `driver.success`, `driver.wx`, `driver.token`, `driver.browser_manager`).
- `jobs.*`: Background job definitions (e.g., `jobs.article.UpdateArticle`, `jobs.mps.run`, `jobs.mps.reload_job`).
- `tools.mdtools.export`: Specific export functionalities for Markdown.
- `schemas.tags`: Pydantic models for tags.

### External Dependencies
- `FastAPI`: Web framework and routing.
- `Pydantic`: Data validation and serialization.
- `SQLAlchemy`: ORM and database operations.
- `httpx`: Asynchronous HTTP client (used in `res.py`).
- `threading`: For managing background tasks (e.g., in `tools.py`).
- `asyncio`: For asynchronous operations.
- `platform`, `time`, `sys`, `psutil`: System information (in `sys_info.py`).
- `uuid`: For generating unique IDs.
- `datetime`: Date and time manipulation.
- `hashlib`: For hashing (in `res.py`).
- `csv`, `io`, `os`: File and I/O operations (in `export.py`).
- `logging`: Standard Python logging.
- `passlib.context.CryptContext`: For password hashing (`pwd_context` in `user.py`).
- `python-multipart`: For file uploads (`UploadFile`).
- `python-jose`: For JWT handling.

## Integration Points

### Public APIs
The module exposes a wide array of public APIs grouped by functionality, as detailed in the "Key Components" section for each file. These APIs typically follow the `/api/v1/wx/{module_prefix}/{endpoint}` pattern, with `/api/v1/wx` being the `API_VERSION` defined in `ver.py`.

### Data Flow
- **Request -> FastAPI Router -> Dependency Injection -> Business Logic -> Database/External Service -> Response**:
    - Incoming HTTP requests are routed by FastAPI to the appropriate endpoint function.
    - Dependencies (like `get_current_user` for authentication, `get_db` for database sessions) are injected.
    - Business logic is executed, often involving interactions with the `core.db` for data persistence, `core.wx` for WeChat API calls, or `core.queue` for background tasks.
    - Responses are formatted using `success_response` or `error_response` from `base.py`.
- **Background Tasks**: Operations like article updating (`mps.py`) and article exporting (`tools.py`) are often offloaded to background queues (`core.queue`) to prevent blocking the main API thread, with their status queryable via dedicated endpoints.
- **Caching**: `res.py` implements a caching layer for static assets, and other modules (`rss.py`, `tags.py`, `article.py`) use `core.cache` to clear relevant cache entries upon data modification.

### Authentication
- All protected endpoints use `Depends(get_current_user)` to ensure JWT-based authentication and retrieve current user information.
- Role-based access control is implemented where necessary (e.g., admin-only access for certain `user.py` and `auth.py` endpoints).

### Configuration
- `core.config.cfg` is extensively used across modules to fetch application settings, influencing behaviors like true deletion, gather content mode, RSS base URL, etc.

## Implementation Notes

### Design Patterns
- **API Gateway Pattern**: The `apis` module effectively acts as an API Gateway for the backend services, providing a unified entry point and handling concerns like routing, authentication, and response formatting.
- **Dependency Injection**: FastAPI's dependency injection system is heavily utilized for managing database sessions (`get_db`) and authentication (`get_current_user`), promoting modularity and testability.
- **Repository Pattern (implied)**: Interaction with the database often goes through SQLAlchemy models, abstracting direct database queries.
- **Asynchronous Programming**: Many endpoints leverage `async/await` and `asyncio` for non-blocking I/O operations, especially when interacting with external services or performing long-running tasks. Background threads (`threading`) and `ThreadPoolExecutor` are also used for CPU-bound or blocking operations.
- **Command Query Responsibility Segregation (CQRS)**: Separates read and write operations, as seen in distinct endpoints for retrieving data versus modifying it.

### Technical Decisions
- **FastAPI Framework**: Chosen for its high performance, automatic interactive API documentation (Swagger UI), and robust data validation with Pydantic.
- **Pydantic for Data Validation**: Ensures that incoming request data and outgoing response data adhere to predefined schemas, reducing errors and improving data consistency.
- **SQLAlchemy ORM**: Used for database interactions, providing an object-relational mapping layer that simplifies database operations and helps prevent SQL injection.
- **Asynchronous Database Sessions**: `DB.async_session_factory()` is used to manage SQLAlchemy sessions in an asynchronous context, aligning with FastAPI's async nature.
- **Background Task Queues**: The implementation of `core.queue.GlobalQueueManager` and `TaskQueue` allows for offloading long-running operations (like article updates or exports) to background tasks, improving API responsiveness.
- **Centralized Error Handling**: A consistent `error_response` utility ensures uniform error reporting across all APIs.
- **Cache Management**: `core.cache` is used to manage cached data, improving performance for frequently accessed information.
- **Secure Password Hashing**: `passlib.context.CryptContext` is used for securely hashing user passwords.

### Considerations
- **Performance**: Heavy use of asynchronous programming and background tasks to ensure responsiveness. Caching (e.g., in `rss.py` and `res.py`) further optimizes performance for frequently requested data.
- **Security**: JWT-based authentication, role-based access control, input validation via Pydantic, password hashing, and path traversal protection (in `tools.py` for file deletion) are implemented.
- **Error Handling**: Comprehensive try-except blocks with `HTTPException` ensure that errors are caught, logged, and returned in a standardized format.
- **Scalability**: The modular design, use of background queues, and asynchronous processing contribute to the scalability of the API services.
- **Maintainability**: Clear separation of concerns into individual files and consistent coding practices enhance maintainability.
- **WeChat API Integration**: Specific drivers and models (`core.wx`, `driver.wx`) are tailored for interacting with the WeChat platform.

### Limitations
- The `POST /rss/{feed_id}/fresh` endpoint is currently commented out, indicating it's either under development or intentionally disabled.
- Some error responses, particularly in `tags.py`, use HTTP status code `201 CREATED` for "not found" or server errors, which deviates from standard HTTP practices (e.g., 404 NOT FOUND, 500 INTERNAL SERVER ERROR). This might lead to unexpected client behavior or incorrect interpretation of API responses.
- The "Test Message" endpoint (`GET /message_tasks/message/test/{task_id}`) in `message_task.py` only fetches task details and does not appear to trigger an actual message test.
