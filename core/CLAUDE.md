# core Module

## Purpose and Scope
The `core` module serves as the foundational layer of the `ygg-we-mp-rss` application, encompassing essential functionalities and configurations required for the system's operation. It provides core services such as authentication, configuration management, database interactions, RSS feed generation, and utility functions, acting as the central nervous system for the application.

## Structure Overview
The `core` directory is structured into various Python modules and subdirectories, each dedicated to a specific set of functionalities. This organization promotes modularity and maintainability.

**Top-level Python Files:**
-   `article_lax.py`: (Details to be provided in a dedicated CLAUDE.md if this file becomes a major component)
-   `auth.py`: Handles user authentication, authorization, and JWT token management.
-   `base.py`: (Details to be provided in a dedicated CLAUDE.md if this file becomes a major component)
-   `cache.py`: Provides caching mechanisms.
-   `config.py`: Manages application configuration, loading, and persistence.
-   `content_format.py`: Deals with formatting content for various outputs.
-   `database.py`: Provides a simple interface to the database session.
-   `db.py`: Manages SQLAlchemy database engine, sessions, and CRUD operations.
-   `file.py`: Contains file-related utility functions.
-   `log.py`: Handles logging mechanisms.
-   `print.py`: Utility for formatted console output.
-   `resource.py`: Manages application resources.
-   `rss.py`: Generates and manages RSS, Atom, and JSON feeds.
-   `thread.py`: Deals with threading utilities.
-   `ver.py`: Stores the application's version information.
-   `wait.py`: (Details to be provided in a dedicated CLAUDE.md if this file becomes a major component)

**Subdirectories:**
-   `common/` - Refer to `common/CLAUDE.md` for details.
-   `lax/` - Refer to `lax/CLAUDE.md` for details.
-   `models/` - Refer to `models/CLAUDE.md` for details.
-   `notice/` - Refer to `notice/CLAUDE.md` for details.
-   `queue/` - Refer to `queue/CLAUDE.md` for details.
-   `res/` - Refer to `res/CLAUDE.md` for details.
-   `task/` - Refer to `task/CLAUDE.md` for details.
-   `webhook/` - Refer to `webhook/CLAUDE.md` for details.
-   `wx/` - Refer to `wx/CLAUDE.md` for details.
-   `yaml_db/` - Refer to `yaml_db/CLAUDE.md` for details.

## Key Components

### `ver.py`
-   Description: Defines the application's version string.
-   Responsibilities: Provides a central, easily accessible version identifier for the application.
-   Key Methods:
    #### `VERSION: str`
    -   Purpose: Stores the current version string of the application.
    -   Parameters: (None)
    -   Returns: (str) The version string (e.g., '1.4.32').

### `auth.py`
-   Description: Manages user authentication, authorization, and JWT token handling for the application's API.
-   Responsibilities: Securely verifies user credentials, generates authentication tokens, and provides mechanisms to control access based on user roles and permissions.
-   Key Methods:
    #### `PasswordHasher` Class
    -   Description: Utility class for securely hashing and verifying passwords using `bcrypt`.
    -   Responsibilities: Encapsulates password-related cryptographic operations.
    -   Key Methods:
        ##### `verify(plain_password: str, hashed_password: str) -> bool`
        -   Purpose: Verifies if a given plain password matches a hashed password.
        -   Parameters:
            -   `plain_password` (str): The password in plain text.
            -   `hashed_password` (str): The hashed password to compare against.
        -   Returns: (bool) `True` if the passwords match, `False` otherwise.
        ##### `hash(password: str) -> str`
        -   Purpose: Generates a bcrypt hash for a given plain password.
        -   Parameters:
            -   `password` (str): The plain text password to hash.
        -   Returns: (str) The bcrypt hashed password string.

    #### `get_login_attempts(username: str) -> int`
    -   Purpose: Retrieves the number of failed login attempts for a specific username.
    -   Parameters:
        -   `username` (str): The username to check.
    -   Returns: (int) The count of failed login attempts.

    #### `get_user(username: str) -> Optional[dict]`
    -   Purpose: Fetches user information from the database, utilizing an in-memory cache for performance.
    -   Parameters:
        -   `username` (str): The username of the user to retrieve.
    -   Returns: (Optional[dict]) A dictionary representing the user if found, `None` otherwise.

    #### `clear_user_cache(username: str)`
    -   Purpose: Removes a specific user's data from the in-memory cache.
    -   Parameters:
        -   `username` (str): The username whose cache entry should be cleared.
    -   Returns: (None)

    #### `authenticate_user(username: str, password: str) -> Optional[DBUser]`
    -   Purpose: Authenticates a user by verifying their username and password against stored credentials. It also handles login attempt limits.
    -   Parameters:
        -   `username` (str): The username provided by the user.
        -   `password` (str): The plain text password provided by the user.
    -   Returns: (Optional[DBUser]) The user object if authentication is successful.
    -   Throws: `HTTPException` with status `HTTP_202_ACCEPTED` if login attempts exceed the maximum or credentials are invalid.

    #### `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`
    -   Purpose: Creates a JSON Web Token (JWT) for authentication.
    -   Parameters:
        -   `data` (dict): The payload to encode into the token (e.g., `{"sub": username}`).
        -   `expires_delta` (Optional[timedelta]): The timedelta object specifying the token's expiration time. If `None`, defaults to 15 minutes.
    -   Returns: (str) The encoded JWT string.

    #### `get_current_user(token: str = Depends(oauth2_scheme)) -> dict`
    -   Purpose: A FastAPI dependency function that decodes and validates a JWT token from an incoming request to retrieve the current authenticated user's information.
    -   Parameters:
        -   `token` (str): The JWT token extracted from the request headers (injected by `OAuth2PasswordBearer`).
    -   Returns: (dict) A dictionary containing the authenticated user's `username`, `role`, `permissions`, and `original_user` object.
    -   Throws: `HTTPException` with status `HTTP_401_UNAUTHORIZED` if token validation fails.

    #### `requires_role(role: str)`
    -   Purpose: A decorator factory that creates a decorator to restrict access to endpoints based on the user's role.
    -   Parameters:
        -   `role` (str): The required role for accessing the decorated endpoint.
    -   Returns: (function) A decorator function.
    -   Throws: `HTTPException` with status `HTTP_403_FORBIDDEN` if the current user does not have the required role.

    #### `requires_permission(permission: str)`
    -   Purpose: A decorator factory that creates a decorator to restrict access to endpoints based on specific user permissions.
    -   Parameters:
        -   `permission` (str): The required permission for accessing the decorated endpoint.
    -   Returns: (function) A decorator function.
    -   Throws: `HTTPException` with status `HTTP_403_FORBIDDEN` if the current user does not have the required permission.

### `config.py`
-   Description: Provides a robust mechanism for loading, managing, and persisting application configurations from YAML files, with support for environment variable substitution and optional encryption.
-   Responsibilities: Centralizes configuration access, ensures configuration integrity, and provides dynamic configuration capabilities.
-   Key Methods:
    #### `Config` Class
    -   Description: Manages the application's configuration settings.
    -   Responsibilities: Loads configurations from YAML files, handles encryption/decryption, environment variable replacement, and provides methods to get and set configuration values.
    -   Key Methods:
        ##### `__init__(self, config_path: str = None, encrypt: bool = False)`
        -   Purpose: Initializes the `Config` instance, parses command-line arguments, sets the configuration file path, and initializes encryption if enabled.
        -   Parameters:
            -   `config_path` (str): Path to the YAML configuration file. [optional] [default: 'config.yaml']
            -   `encrypt` (bool): Whether encryption is enabled for the configuration file. [default: False]
        -   Returns: (None)
        ##### `save_config(self)`
        -   Purpose: Saves the current configuration object back to the YAML file, applying encryption if enabled.
        -   Parameters: (None)
        -   Returns: (None)
        -   Throws: `Exception` if saving fails, e.g., due to invalid YAML format or file write errors.
        ##### `get_config(self)`
        -   Purpose: Loads the configuration from the YAML file, decrypting it if necessary, and performs environment variable substitution. Utilizes a cache to avoid redundant file reads.
        -   Parameters: (None)
        -   Returns: (dict) The loaded and processed configuration as a dictionary.
        -   Throws: `Exception` if loading or decryption fails.
        ##### `reload(self)`
        -   Purpose: Reloads the configuration from the file and updates the internal cache.
        -   Parameters: (None)
        -   Returns: (None)
        ##### `set(self, key: str, default: any = None)`
        -   Purpose: Sets a configuration value for a given key and immediately saves the configuration to the file.
        -   Parameters:
            -   `key` (str): The configuration key (can be nested, e.g., "db.host").
            -   `default` (any): The value to set for the key. [optional] [default: None]
        -   Returns: (None)
        ##### `get(self, key: str, default: any = None) -> any`
        -   Purpose: Retrieves a configuration value for a given key, supporting nested keys and providing a default fallback. Performs environment variable substitution on the retrieved value.
        -   Parameters:
            -   `key` (str): The configuration key (can be nested, e.g., "db.host").
            -   `default` (any): The default value to return if the key is not found. [optional] [default: None]
        -   Returns: (any) The configuration value, or the default value if the key is not found.

    #### `cfg`
    -   Description: A global instance of the `Config` class, providing convenient access to configuration settings throughout the application.
    -   Responsibilities: Acts as the primary entry point for all configuration-related operations.

    #### `set_config(key: str, value: str)`
    -   Purpose: Wrapper function to set a configuration value using the global `cfg` instance.
    -   Parameters:
        -   `key` (str): The configuration key.
        -   `value` (str): The value to set.
    -   Returns: (None)

    #### `save_config()`
    -   Purpose: Wrapper function to save the current configuration using the global `cfg` instance.
    -   Parameters: (None)
    -   Returns: (None)

    #### `DEBUG: bool`
    -   Purpose: Global boolean flag indicating if debug mode is enabled, derived from configuration.

    #### `APP_NAME: str`
    -   Purpose: Global string indicating the application's name, derived from configuration.

### `database.py`
-   Description: Provides a simplified, high-level interface for obtaining database sessions.
-   Responsibilities: Abstracts the underlying database session management details from consumers.
-   Key Methods:
    #### `get_db()`
    -   Purpose: Retrieves a new database session instance.
    -   Parameters: (None)
    -   Returns: (sqlalchemy.orm.session.Session) An active SQLAlchemy session.

### `db.py`
-   Description: Manages SQLAlchemy database engine, session factories, and provides core CRUD operations and session handling for the application's data models.
-   Responsibilities: Initializes database connections (sync and async), handles session lifecycle, creates database tables, and offers methods for common data manipulation tasks.
-   Key Methods:
    #### `Db` Class
    -   Description: Central class for database management.
    -   Responsibilities: Configures and manages SQLAlchemy engines (sync and async), session factories, and provides methods for interacting with the database.
    -   Key Methods:
        ##### `__init__(self, tag: str = "默认", User_In_Thread: bool = True)`
        -   Purpose: Initializes the `Db` instance, setting up database connections based on configuration.
        -   Parameters:
            -   `tag` (str): A descriptive tag for the database instance, used for logging. [default: "默认"]
            -   `User_In_Thread` (bool): Flag indicating if sessions should be scoped per thread. [default: True]
        -   Returns: (None)
        ##### `get_engine() -> Engine`
        -   Purpose: Returns the synchronous SQLAlchemy engine.
        -   Parameters: (None)
        -   Returns: (sqlalchemy.engine.Engine) The SQLAlchemy engine.
        -   Throws: `ValueError` if the engine is not initialized.
        ##### `get_session_factory()`
        -   Purpose: Returns the synchronous session factory.
        -   Parameters: (None)
        -   Returns: (sqlalchemy.orm.sessionmaker) The session factory.
        ##### `get_async_engine()`
        -   Purpose: Returns the asynchronous SQLAlchemy engine.
        -   Parameters: (None)
        -   Returns: (sqlalchemy.ext.asyncio.engine.AsyncEngine) The asynchronous SQLAlchemy engine.
        -   Throws: `ValueError` if the async engine is not initialized.
        ##### `init(self, con_str: str)`
        -   Purpose: Initializes (or re-initializes) database connections based on the provided connection string. Handles SQLite path creation and adapts connection strings for async.
        -   Parameters:
            -   `con_str` (str): The database connection string (e.g., "sqlite:///./test.db").
        -   Returns: (None)
        -   Throws: `Exception` if connection creation fails.
        ##### `create_tables()`
        -   Purpose: Creates all database tables defined in the application's models using the configured engine.
        -   Parameters: (None)
        -   Returns: (None)
        -   Throws: `Exception` if table creation fails.
        ##### `close()`
        -   Purpose: Closes the active database session.
        -   Parameters: (None)
        -   Returns: (None)
        ##### `delete_article(article_data: dict) -> bool`
        -   Purpose: Deletes an article from the database based on its ID.
        -   Parameters:
            -   `article_data` (dict): A dictionary containing article information, including its `id` and `mp_id`.
        -   Returns: (bool) `True` if the article was successfully deleted, `False` otherwise.
        ##### `add_article(self, article_data: dict, check_exist: bool = True) -> bool`
        -   Purpose: Adds a new article to the database. It checks for duplicates before adding and sets creation/update timestamps.
        -   Parameters:
            -   `article_data` (dict): A dictionary containing the article's data.
            -   `check_exist` (bool): If `True`, checks if an article with the same URL or ID already exists before adding. [default: True]
        -   Returns: (bool) `True` if the article was successfully added, `False` if it was a duplicate or an error occurred.
        ##### `get_articles(self, id: str = None, limit: int = 30, offset: int = 0) -> List[Article]`
        -   Purpose: Retrieves a list of articles from the database, with optional filtering by ID, limit, and offset for pagination.
        -   Parameters:
            -   `id` (str): Optional article ID to filter by. [optional] [default: None]
            -   `limit` (int): Maximum number of articles to return. [default: 30]
            -   `offset` (int): Number of articles to skip. [default: 0]
        -   Returns: (List[Article]) A list of `Article` objects.
        ##### `get_all_mps() -> List[Feed]`
        -   Purpose: Retrieves all `Feed` records (representing public accounts/sources) from the database.
        -   Parameters: (None)
        -   Returns: (List[Feed]) A list of `Feed` objects.
        ##### `get_mps_list(self, mp_ids: str) -> List[Feed]`
        -   Purpose: Retrieves a list of `Feed` records based on a comma-separated string of `mp_ids`.
        -   Parameters:
            -   `mp_ids` (str): A comma-separated string of `mp_ids`.
        -   Returns: (List[Feed]) A list of `Feed` objects matching the provided IDs.
        ##### `get_mps(self, mp_id: str) -> Optional[Feed]`
        -   Purpose: Retrieves a single `Feed` record by its `mp_id`.
        -   Parameters:
            -   `mp_id` (str): The ID of the public account/source.
        -   Returns: (Optional[Feed]) A `Feed` object if found, `None` otherwise.
        ##### `get_faker_id(self, mp_id: str)`
        -   Purpose: Retrieves the `faker_id` for a given `mp_id`.
        -   Parameters:
            -   `mp_id` (str): The ID of the public account/source.
        -   Returns: (any) The `faker_id` associated with the `mp_id`.
        ##### `expire_all(self)`
        -   Purpose: Expires all objects currently loaded in the session.
        -   Parameters: (None)
        -   Returns: (None)
        ##### `get_session(self)`
        -   Purpose: Retrieves an active synchronous database session, handling session closure and reconnection if necessary.
        -   Parameters: (None)
        -   Returns: (sqlalchemy.orm.session.Session) An active SQLAlchemy session.
        ##### `session_dependency(self)`
        -   Purpose: A FastAPI dependency for managing synchronous database sessions within request contexts.
        -   Parameters: (None)
        -   Returns: (Generator[Session, None, None]) A generator that yields a session and ensures its removal after use.
        ##### `get_async_session(self)`
        -   Purpose: Retrieves an active asynchronous database session.
        -   Parameters: (None)
        -   Returns: (AsyncGenerator[AsyncSession, None]) An asynchronous generator that yields an async session.
        ##### `async_session_dependency(self)`
        -   Purpose: A FastAPI dependency for managing asynchronous database sessions within request contexts.
        -   Parameters: (None)
        -   Returns: (Callable[..., AsyncGenerator[AsyncSession, None]]) A callable that returns an asynchronous generator for sessions.

    #### `DB`
    -   Description: A global instance of the `Db` class, providing convenient access to database operations throughout the application.
    -   Responsibilities: Acts as the primary entry point for all database-related functionalities.

### `rss.py`
-   Description: Provides functionality for generating RSS 2.0, Atom, and JSON feeds from a list of articles. It also includes content caching, datetime conversion, and URL manipulation utilities.
-   Responsibilities: Creates standardized syndication feeds, manages feed content caching, and assists in content presentation.
-   Key Methods:
    #### `RSS` Class
    -   Description: Generates and manages various types of RSS feeds.
    -   Responsibilities: Handles the creation of XML/JSON structures for feeds, caches article content, and provides utilities for feed-related data manipulation.
    -   Key Methods:
        ##### `__init__(self, name: str = "all", cache_dir: str = None, ext: str = "rss")`
        -   Purpose: Initializes the `RSS` instance, setting up cache directories and the target RSS file path.
        -   Parameters:
            -   `name` (str): The base name for the RSS file. [default: "all"]
            -   `cache_dir` (str): The directory to store RSS cache files. [optional]
            -   `ext` (str): The file extension, indicating the type of feed. [default: "rss"]
        -   Returns: (None)
        -   Throws: `ValueError` if an invalid file path is provided (path traversal detected).
        ##### `get_type(self)`
        -   Purpose: Returns the MIME type corresponding to the feed's file extension.
        -   Parameters: (None)
        -   Returns: (str) The MIME type (e.g., "application/xml", "application/json").
        ##### `cache_content(self, content_id: str, content: dict)`
        -   Purpose: Caches article content as a JSON file.
        -   Parameters:
            -   `content_id` (str): Unique identifier for the content.
            -   `content` (dict): The article content to cache.
        -   Returns: (None)
        -   Throws: `ValueError` if an invalid content path is provided.
        ##### `get_cached_content(self, content_id: str) -> dict`
        -   Purpose: Retrieves cached article content by its ID.
        -   Parameters:
            -   `content_id` (str): Unique identifier of the cached content.
        -   Returns: (dict) The cached content as a dictionary if found, `None` otherwise.
        ##### `serialize_datetime(self, obj)`
        -   Purpose: Serializes datetime objects to ISO format for JSON output.
        -   Parameters:
            -   `obj` (any): The object to serialize.
        -   Returns: (any) The ISO formatted string if `obj` is a datetime, otherwise `obj` itself.
        ##### `datetime_to_rfc822(self, dt) -> str`
        -   Purpose: Converts a datetime object or ISO string to an RFC 822 formatted string, assuming CST (UTC+8) for naive datetimes.
        -   Parameters:
            -   `dt` (datetime | str): The datetime object or string.
        -   Returns: (str) The RFC 822 formatted datetime string.
        ##### `add_logo_prefix_to_urls(self, text: str) -> str`
        -   Purpose: Prepends a static logo prefix to image URLs within a given text string.
        -   Parameters:
            -   `text` (str): The input string containing URLs.
        -   Returns: (str) The processed string with prefixes added to image URLs.
        ##### `generate_rss(self, rss_list: dict, title: str = "Mp-We-Rss", link: str = "https://github.com/rachelos/we-mp-rss", description: str = "RSS频道", language: str = "zh-CN", image_url: str = "") -> str`
        -   Purpose: Generates an RSS 2.0 formatted XML string from a list of RSS items.
        -   Parameters:
            -   `rss_list` (dict): A dictionary of RSS items.
            -   `title` (str): The title of the RSS channel. [default: "Mp-We-Rss"]
            -   `link` (str): The link for the RSS channel. [default: "https://github.com/rachelos/we-mp-rss"]
            -   `description` (str): The description of the RSS channel. [default: "RSS频道"]
            -   `language` (str): The language of the RSS channel. [default: "zh-CN"]
            -   `image_url` (str): URL of the channel image/logo. [optional]
        -   Returns: (str) The RSS 2.0 XML string.
        ##### `generate_atom(self, rss_list: dict, title: str = "Mp-We-Rss", link: str = "https://github.com/rachelos/we-mp-rss", description: str = "RSS频道", language: str = "zh-CN", image_url: str = "") -> str`
        -   Purpose: Generates an Atom formatted XML string from a list of RSS items.
        -   Parameters:
            -   `rss_list` (dict): A dictionary of RSS items.
            -   `title` (str): The title of the Atom feed. [default: "Mp-We-Rss"]
            -   `link` (str): The link for the Atom feed. [default: "https://github.com/rachelos/we-mp-rss"]
            -   `description` (str): The description of the Atom feed. [default: "RSS频道"]
            -   `language` (str): The language of the Atom feed. [default: "zh-CN"]
            -   `image_url` (str): URL of the feed image/logo. [optional]
        -   Returns: (str) The Atom XML string.
        ##### `get_content_type(self) -> str`
        -   Purpose: Determines the content type (e.g., "html", "markdown", "text") based on the configured extension.
        -   Parameters: (None)
        -   Returns: (str) The determined content type.
        ##### `generate_json(self, rss_list: dict, title: str = "Mp-We-Rss", link: str = "https://github.com/rachelos/we-mp-rss", description: str = "RSS频道", language: str = "zh-CN", image_url: str = "") -> str`
        -   Purpose: Generates a JSON formatted string from a list of RSS items.
        -   Parameters:
            -   `rss_list` (dict): A dictionary of RSS items.
            -   `title` (str): The title of the JSON feed. [default: "Mp-We-Rss"]
            -   `link` (str): The link for the JSON feed. [default: "https://github.com/rachelos/we-mp-rss"]
            -   `description` (str): The description of the JSON feed. [default: "RSS频道"]
            -   `language` (str): The language of the JSON feed. [default: "zh-CN"]
            -   `image_url` (str): URL of the feed image/logo. [optional]
        -   Returns: (str) The JSON string.
        ##### `get_cache(self)`
        -   Purpose: Retrieves the content of the cached RSS file.
        -   Parameters: (None)
        -   Returns: (Optional[str]) The content of the cached file as a string, or `None` if not found.
        ##### `generate(self, rss_list: dict, ext: str, title: str = "Mp-We-Rss", link: str = "https://github.com/rachelos/we-mp-rss", description: str = "RSS频道", language: str = "zh-CN", image_url: str = "", template: str = None) -> str`
        -   Purpose: A unified method to generate RSS, Atom, or JSON feeds based on the specified file extension or a custom template.
        -   Parameters:
            -   `rss_list` (dict): A dictionary of RSS items.
            -   `ext` (str): The desired output format extension (e.g., "rss", "atom", "json").
            -   `title` (str): The title of the feed. [default: "Mp-We-Rss"]
            -   `link` (str): The link for the feed. [default: "https://github.com/rachelos/we-mp-rss"]
            -   `description` (str): The description of the feed. [default: "RSS频道"]
            -   `language` (str): The language of the feed. [default: "zh-CN"]
            -   `image_url` (str): URL of the feed image/logo. [optional]
            -   `template` (str): Optional path to a custom template file for rendering. [optional]
        -   Returns: (str) The generated feed content as a string.
        -   Throws: `ValueError` if the extension is unsupported and no template is provided.
        ##### `generate_by_template(self, rss_list: dict, template: str, title: str = "Mp-We-Rss", link: str = "https://github.com/rachelos/we-mp-rss", description: str = "RSS频道", language: str = "zh-CN", image_url: str = "")`
        -   Purpose: Generates feed content using a custom template and the `core.lax.TemplateParser`.
        -   Parameters:
            -   `rss_list` (dict): A dictionary of RSS items.
            -   `template` (str): The path to the custom template file.
            -   `title` (str): The title to pass to the template. [default: "Mp-We-Rss"]
            -   `link` (str): The link to pass to the template. [default: "https://github.com/rachelos/we-mp-rss"]
            -   `description` (str): The description to pass to the template. [default: "RSS频道"]
            -   `language` (str): The language to pass to the template. [default: "zh-CN"]
            -   `image_url` (str): The image URL to pass to the template. [optional]
        -   Returns: (str) The rendered content from the template.
        ##### `clear_cache(self, mp_id: str = "")`
        -   Purpose: Clears cached RSS and content files, optionally filtered by `mp_id`.
        -   Parameters:
            -   `mp_id` (str): Optional ID to filter cached files. Only files containing this ID in their name will be deleted. [default: ""]
        -   Returns: (None)

## Dependencies

### Internal Dependencies
-   `core.config` - For accessing application configuration settings (e.g., `jwt_secret_key`, `token_expire_minutes`, `db` connection string, `rss.full_context`, `rss.add_cover`, `rss.cdata`).
-   `core.db` - For managing database connections and sessions.
-   `core.models` - For `User` (in `auth.py`), `DBUser` (in `auth.py`), `Article`, `Feed` (in `db.py`), `Base` (in `db.py`).
-   `core.print` - For logging and printing messages (e.g., `print_error`, `print_warning`, `print_info`, `print_success`).
-   `core.file` - For `FileCrypto` (in `config.py`) to handle encrypted configuration files.
-   `core.content_format` - For formatting article content before inclusion in feeds (in `rss.py`).
-   `core.lax.TemplateParser` - For rendering feeds using custom templates (in `rss.py`).
-   `apis.base.error_response` - For constructing error responses in authentication.

### External Dependencies
-   `datetime` (standard library) - For handling dates and times (e.g., JWT expiration, RSS `pubDate`).
-   `jwt` (PyJWT) - For encoding and decoding JSON Web Tokens (`auth.py`).
-   `bcrypt` - For password hashing and verification (`auth.py`).
-   `functools.wraps` - For preserving metadata of decorated functions (`auth.py`).
-   `fastapi` - For building the API, including `Depends`, `HTTPException`, `status`, `OAuth2PasswordBearer` (`auth.py`, `database.py`, `db.py`).
-   `typing` - For type hints (`auth.py`, `db.py`).
-   `sqlalchemy` - For ORM functionalities, database engine, session management, and table creation (`db.py`, `database.py`).
-   `sqlalchemy.orm` - For `sessionmaker`, `declarative_base`, `scoped_session` (`db.py`).
-   `sqlalchemy.ext.asyncio` - For `create_async_engine`, `AsyncSession`, `async_sessionmaker` (`db.py`).
-   `yaml` (PyYAML) - For parsing and generating YAML configuration files (`config.py`).
-   `sys`, `os` (standard library) - For system-level operations, environment variables, file paths (`config.py`, `rss.py`).
-   `argparse` (standard library) - For parsing command-line arguments (`config.py`).
-   `json` (standard library) - For handling JSON data (e.g., caching in `rss.py`).
-   `xml.etree.ElementTree` (standard library) - For building XML structures for RSS and Atom feeds (`rss.py`).
-   `re` (standard library) - For regular expression operations (e.g., URL manipulation in `rss.py`, env var replacement in `config.py`).
-   `shutil` (standard library) - For high-level file operations (e.g., deleting directories in `rss.py`).

## Integration Points

### Public APIs
-   `core.auth.authenticate_user()`: Authenticates users against stored credentials.
-   `core.auth.create_access_token()`: Generates JWT access tokens for authenticated users.
-   `core.auth.get_current_user()`: FastAPI dependency to extract and validate the current user from a JWT.
-   `core.auth.requires_role()`: Decorator for role-based access control.
-   `core.auth.requires_permission()`: Decorator for permission-based access control.
-   `core.config.cfg`: Global `Config` instance for application-wide configuration access.
-   `core.config.set_config()`: Function to dynamically set and save configuration values.
-   `core.config.save_config()`: Function to persist current configuration to file.
-   `core.database.get_db()`: Function to obtain a synchronous database session.
-   `core.db.DB`: Global `Db` instance for comprehensive database operations.
-   `core.db.Db.get_session()`: Method to get a synchronous SQLAlchemy session.
-   `core.db.Db.session_dependency()`: FastAPI dependency for synchronous session management.
-   `core.db.Db.get_async_session()`: Method to get an asynchronous SQLAlchemy session.
-   `core.db.Db.async_session_dependency()`: FastAPI dependency for asynchronous session management.
-   `core.rss.RSS` class: Entry point for generating various feed formats and managing related caching.
-   Subdirectory `CLAUDE.md` files: Each subdirectory exposes its public interfaces, documented within its respective `CLAUDE.md`.

### Data Flow
-   **Authentication Flow**: User credentials -> `auth.authenticate_user()` -> JWT token -> `auth.create_access_token()` -> API requests with token -> `auth.get_current_user()` for validation and user context.
-   **Configuration Flow**: `config.yaml` (or environment variables) -> `core.config.cfg.get_config()` (with optional decryption and env var substitution) -> application components using `cfg.get()`. Configuration changes can be persisted via `cfg.save_config()`.
-   **Database Interaction Flow**: Application logic requests session via `core.database.get_db()` or `core.db.DB.get_session()` (or async equivalents) -> performs CRUD operations on models -> `session.commit()`.
-   **RSS Feed Generation Flow**: Article data (from DB or other sources) -> `core.rss.RSS().generate()` (with format selection) -> formatted XML/JSON output. Caching is handled internally by the `RSS` class.

## Implementation Notes

### Design Patterns
-   **Singleton**: The `core.config.cfg` and `core.db.DB` instances follow a singleton-like pattern, providing a single, globally accessible point for configuration and database management, respectively. This simplifies access and ensures consistent state across the application.
-   **Decorator**: The `requires_role` and `requires_permission` functions in `auth.py` are implemented as decorator factories, enabling declarative access control for FastAPI endpoints.
-   **Dependency Injection**: FastAPI's `Depends` mechanism is heavily utilized in `auth.py` and `db.py` (`get_current_user`, `session_dependency`, `async_session_dependency`) to manage and inject dependencies like database sessions and current user objects, promoting loose coupling and testability.

### Technical Decisions
-   **SQLAlchemy ORM**: Chosen for database interactions, providing a powerful and flexible object-relational mapper that supports both synchronous and asynchronous operations. This allows for a unified approach to data persistence.
-   **FastAPI Integration**: Core components are designed to integrate seamlessly with FastAPI, leveraging its dependency injection system and exception handling for API development.
-   **YAML for Configuration**: YAML is used for configuration files due to its human-readable nature and support for complex data structures, making configurations easy to manage.
-   **Bcrypt for Password Hashing**: `bcrypt` is employed for password hashing in `auth.py` for its strong cryptographic properties and resistance to brute-force attacks.
-   **JWT for Authentication**: JSON Web Tokens are used for stateless authentication, providing a secure and scalable method for API authorization.
-   **Content Caching**: `rss.py` implements caching mechanisms for generated feeds and individual article content, improving performance and reducing redundant processing.

### Considerations
-   **Performance**: Extensive use of caching (e.g., user cache in `auth.py`, config cache in `config.py`, feed cache in `rss.py`) and SQLAlchemy's connection pooling (`db.py`) is implemented to optimize application performance.
-   **Security**: Sensitive information such as JWT secret keys and database connection strings are managed through environment variables or encrypted configuration (`config.py`). Password hashing (`auth.py`) and path traversal checks (`rss.py`) are in place to enhance security.
-   **Error Handling**: Centralized error handling is suggested through `HTTPException` in API-related components and `try-except` blocks in critical operations to ensure graceful degradation and informative error messages.
-   **Scalability**: The modular design and use of robust libraries like SQLAlchemy and FastAPI lay a foundation for building a scalable application. Asynchronous database operations further support handling concurrent requests efficiently.
-   **Maintainability**: The separation of concerns into distinct modules and subdirectories, along with clear documentation (like this `CLAUDE.md`), contributes to the overall maintainability of the codebase.