# tools

## Purpose and Scope
The `tools` directory serves as a repository for various utility scripts and modules that support the `ygg-we-mp-rss` project. These tools cover a range of functionalities including data processing (e.g., Base64 encoding, HTML cleaning), system monitoring (e.g., browser resource monitoring), database maintenance (e.g., article cleaning, admin user initialization), content manipulation (e.g., Markdown conversion), and development operations (e.g., GitHub updates, proxying for debugging). Its main responsibility is to provide auxiliary functionalities that enhance development, maintenance, and data handling within the larger system.

## Structure Overview
The `tools` directory is organized into a collection of standalone Python scripts and a dedicated subdirectory (`mdtools`) for Markdown-related utilities.

```
tools/
├── base64_tools.py
├── browser_monitor.py
├── clean.py
├── fix.py
├── github_updater.py
├── html.py
├── init_admin_user.py
├── moinfo.py
├── proxy.py
└── mdtools/
    └── CLAUDE.md (referenced)
```

## Key Components

### `base64_tools.py`
- Description: Provides utility functions for Base64 encoding and decoding of strings, bytes, and images, including URL-safe variations.
- Responsibilities: Encodes and decodes data to/from Base64 format, handles URL-safe Base64, and converts image files to/from Base64 data URLs.
- Key Methods:
  #### `base64_encode(data: str): str`
  - Purpose: Encodes a string to its Base64 representation.
  - Parameters:
    - `data (str)`: The string to encode.
  - Returns: (str) The Base64 encoded string.

  #### `base64_decode(encoded_data: str): str`
  - Purpose: Decodes a Base64 encoded string back to its original form.
  - Parameters:
    - `encoded_data (str)`: The Base64 encoded string.
  - Returns: (str) The decoded string.
  - Throws: `binascii.Error` if the input is not valid Base64.

  #### `image_to_base64(image_path: str, mime_type: Optional[str] = None): str`
  - Purpose: Converts an image file into a Base64 encoded data URL string.
  - Parameters:
    - `image_path (str)`: The path to the image file.
    - `mime_type (str, optional)`: The MIME type of the image. If `None`, it's inferred from the file extension.
  - Returns: (str) The Base64 encoded image data URL.
  - Throws: `FileNotFoundError` if the image file does not exist, `ValueError` if image processing fails.

### `browser_monitor.py`
- Description: A tool to detect and monitor unclosed browser processes, helping identify resource leaks. It can also force cleanup of browser processes.
- Responsibilities: Monitors browser-related processes, reports their status, checks for potential resource leaks, and can forcibly terminate identified browser processes.
- Core Class: `BrowserMonitor`
  - Description: Manages the logic for identifying, monitoring, and controlling browser processes.
  - Key Methods:
    #### `get_browser_processes(): List[Dict]`
    - Purpose: Retrieves a list of currently running browser process information (PID, name, memory, CPU, etc.).
    - Returns: (List[Dict]) A list of dictionaries, each representing a browser process.

    #### `print_status()`
    - Purpose: Prints a formatted report of the current browser process status, including counts and details.

    #### `check_resource_leak(): bool`
    - Purpose: Compares current browser process count against initial count to detect potential resource leaks.
    - Returns: (bool) `True` if a leak is detected, `False` otherwise.

    #### `force_cleanup_browser_processes()`
    - Purpose: Attempts to terminate all identified browser processes. Use with caution.

### `clean.py`
- Description: Script to clean duplicate articles from the database based on title and `mp_id`.
- Responsibilities: Queries the database for articles, identifies duplicates, and removes them to maintain data integrity.
- Key Methods:
  #### `clean_duplicate_articles(): Tuple[str, int]`
  - Purpose: Identifies and removes duplicate articles from the database.
  - Returns: (Tuple[str, int]) A message indicating the number of articles cleaned and the count.

### `fix.py`
- Description: Provides functions to fix HTML content, specifically for article content, by cleaning and converting markdown to HTML.
- Responsibilities: Takes raw content, formats it as Markdown, converts it to HTML, and applies HTML cleaning rules.
- Key Methods:
  #### `fix_html(content: str): str`
  - Purpose: Processes and cleans HTML content by first formatting it as Markdown, converting to HTML, and then applying cleaning rules.
  - Parameters:
    - `content (str)`: The HTML content string to fix.
  - Returns: (str) The cleaned and fixed HTML content.

  #### `fix_article(article): Dict`
  - Purpose: Takes an article object, extracts its content, and applies the HTML fixing process.
  - Parameters:
    - `article`: An article object (expected to have a `to_dict` method and a `content` field).
  - Returns: (Dict) A dictionary representation of the article with fixed HTML content.

### `github_updater.py`
- Description: A tool for updating source code from a GitHub repository, including checking repository status, fetching updates, creating backups, and rolling back to specific commits.
- Responsibilities: Interacts with Git to manage code updates, ensures repository integrity, and provides rollback capabilities.
- Core Class: `GitHubUpdater`
  - Description: Handles all Git-related operations for updating and managing a local GitHub repository.
  - Key Methods:
    #### `check_git_status(): Dict`
    - Purpose: Retrieves detailed status information about the Git repository (e.g., branch, changes, remote).
    - Returns: (Dict) A dictionary containing the repository status.

    #### `update_from_github(branch: str = None, backup: bool = True): Dict`
    - Purpose: Pulls the latest changes from the configured GitHub repository.
    - Parameters:
      - `branch (str, optional)`: The target branch to update. Defaults to the current branch.
      - `backup (bool)`: If `True`, a backup of the repository is created before updating.
    - Returns: (Dict) A dictionary with the update results (success, message, files updated).

    #### `rollback_to_commit(commit_hash: str): Dict`
    - Purpose: Reverts the repository to a specified commit hash, creating a backup beforehand.
    - Parameters:
      - `commit_hash (str)`: The hash of the commit to roll back to.
    - Returns: (Dict) A dictionary with the rollback results.

### `html.py`
- Description: Provides utilities for cleaning and manipulating HTML content, including removing regions, common elements, and elements based on IDs, classes, selectors, XPaths, or attributes.
- Responsibilities: Offers a comprehensive set of functions to sanitize HTML content, removing unwanted elements or attributes based on various selection criteria.
- Core Class: `HtmlTools`
  - Description: Encapsulates methods for advanced HTML cleaning and manipulation using regular expressions and BeautifulSoup.
  - Key Methods:
    #### `clean_html(html_content: str, remove_ids: list = [], remove_classes: list = [], remove_selectors: list = [], remove_xpaths: list = [], remove_attributes: list = [], remove_regx: list = [], remove_normal_tag: bool = False): str`
    - Purpose: The main entry point for HTML cleaning, allowing removal of elements by IDs, classes, CSS selectors, XPaths, attributes, or regular expressions.
    - Parameters:
      - `html_content (str)`: The HTML content to clean.
      - `remove_ids (list)`: List of HTML `id` attributes to remove.
      - `remove_classes (list)`: List of HTML `class` attributes to remove.
      - `remove_selectors (list)`: List of CSS selectors to remove.
      - `remove_xpaths (list)`: List of XPath expressions to remove (requires `lxml`).
      - `remove_attributes (list)`: List of dictionaries specifying attributes to remove.
      - `remove_regx (list)`: List of regex patterns to remove.
      - `remove_normal_tag (bool)`: If `True`, removes common HTML elements like `<script>`, `<style>`, comments.
    - Returns: (str) The cleaned HTML content.

    #### `remove_elements_by_attributes(html_content: str, attributes: list): str`
    - Purpose: Removes HTML elements based on their attribute names and optional values.
    - Parameters:
      - `html_content (str)`: The HTML content.
      - `attributes (list)`: A list of dictionaries, each specifying an attribute to target for removal.
    - Returns: (str) The HTML content with specified elements removed.

### `init_admin_user.py`
- Description: Ensures the admin user in the database has the correct 'admin' role, addressing issues from a specific commit that introduced RBAC checks without migrating existing admin users' roles.
- Responsibilities: Verifies and corrects the role of the 'admin' user in the database to ensure proper access control.
- Key Methods:
  #### `check_admin_role(): Optional[bool]`
  - Purpose: Checks the current role assigned to the 'admin' user in the database.
  - Returns: (Optional[bool]) `True` if the role is 'admin', `False` if not, `None` if the admin user is not found or an error occurs.

  #### `fix_admin_role(): bool`
  - Purpose: Updates the 'admin' user's role to 'admin' if it's not already set, and clears the user cache.
  - Returns: (bool) `True` if the role was successfully fixed or already correct, `False` otherwise.

### `moinfo.py`
- Description: A script to retrieve additional information (read count, like count) for WeChat articles from a given URL. This script typically relies on manually extracted cookies and keys for authentication and data retrieval.
- Responsibilities: Makes HTTP requests to WeChat's MP platform to fetch article metrics, parses the JSON response, and prints the read and like counts.
- Key Methods:
  #### `getMoreInfo(link: str): Tuple[int, int, int]`
  - Purpose: Extracts article metrics (read count, like count, old like count) from a WeChat article URL.
  - Parameters:
    - `link (str)`: The URL of the WeChat article.
  - Returns: (Tuple[int, int, int]) A tuple containing the read count, like count, and old like count.

### `proxy.py`
- Description: Implements an HTTP/HTTPS proxy server with interception capabilities, based on the `baseproxy` project. It can intercept and modify HTTP/HTTPS requests and responses, and includes CA certificate generation for HTTPS interception.
- Responsibilities: Acts as an intermediary between clients and servers, forwarding requests and responses, with the ability to inspect and alter traffic, particularly useful for debugging and security analysis.
- Core Class: `MitmProxy` (Main proxy server)
  - Description: A multi-threaded HTTP/HTTPS proxy server that can intercept and manipulate requests and responses.
  - Key Methods:
    #### `register(intercept_plug: InterceptPlug)`
    - Purpose: Registers plugins for request or response interception.
    - Parameters:
      - `intercept_plug (InterceptPlug)`: An instance of an `InterceptPlug` subclass.

- Core Class: `CAAuth`
  - Description: Manages the generation and signing of CA and server certificates for HTTPS interception.
  - Key Methods:
    #### `_gen_ca(again: bool = False)`
    - Purpose: Generates the root CA certificate and private key.
    #### `__getitem__(cn: str)`
    - Purpose: Generates a server certificate for a given common name (CN) using the root CA.

### `mdtools/CLAUDE.md`
- Description: This subdirectory contains tools specifically designed for processing and converting Markdown content into various formats like DOCX, HTML, PDF, JSON, and CSV.
- Refer to `mdtools/CLAUDE.md` for detailed documentation on its purpose, structure, components, dependencies, integration points, and implementation notes.

## Dependencies

### Internal Dependencies
- `core.print` (from `browser_monitor.py`, `html.py`, `init_admin_user.py`): For standardized logging and output.
- `core.models.article` (from `clean.py`, `fix.py`): Database model for articles.
- `core.db` (from `clean.py`, `init_admin_user.py`): Database utility for managing sessions.
- `core.content_format` (from `fix.py`): Function for formatting article content.
- `tools.mdtools.md2html` (from `fix.py`): Module for Markdown to HTML conversion.
- `tools.html` (from `fix.py`): Module for HTML cleaning and manipulation.
- `core.models.User` (from `init_admin_user.py`): Database model for users.
- `core.auth` (from `init_admin_user.py`): For clearing user cache.

### External Dependencies
- `base64` (from `base64_tools.py`): Standard library for Base64 encoding/decoding.
- `binascii` (from `base64_tools.py`): Standard library for converting between binary and ASCII.
- `os` (from `base64_tools.py`, `browser_monitor.py`, `github_updater.py`, `proxy.py`): Standard library for interacting with the operating system.
- `typing` (from `base64_tools.py`, `browser_monitor.py`, `github_updater.py`): Standard library for type hints.
- `psutil` (from `browser_monitor.py`): Third-party library for system and process utilities.
- `sys` (from `browser_monitor.py`, `github_updater.py`, `init_admin_user.py`): Standard library for system-specific parameters and functions.
- `time` (from `browser_monitor.py`, `moinfo.py`, `proxy.py`): Standard library for time-related functions.
- `datetime` (from `browser_monitor.py`, `github_updater.py`): Standard library for date and time operations.
- `sqlalchemy` (from `clean.py`): Third-party library for SQL database toolkit and Object-Relational Mapper.
- `copy` (from `fix.py`): Standard library for shallow and deep copy operations.
- `subprocess` (from `github_updater.py`): Standard library for spawning new processes.
- `logging` (from `github_updater.py`, `proxy.py`): Standard library for logging events.
- `json` (from `github_updater.py`): Standard library for JSON data handling.
- `argparse` (from `github_updater.py`, `init_admin_user.py`): Standard library for parsing command-line arguments.
- `re` (from `html.py`, `proxy.py`): Standard library for regular expressions.
- `bs4` (BeautifulSoup) (from `html.py`): Third-party library for parsing HTML/XML documents.
- `lxml` (from `html.py` - optional for XPath): Third-party library for processing XML and HTML.
- `pathlib` (from `init_admin_user.py`): Standard library for object-oriented filesystem paths.
- `requests` (from `moinfo.py`, `proxy.py`): Third-party library for making HTTP requests.
- `pandas` (from `moinfo.py`): Third-party library for data manipulation and analysis.
- `select` (from `proxy.py`): Standard library for I/O multiplexing.
- `zlib` (from `proxy.py`): Standard library for compression and decompression.
- `chardet` (from `proxy.py`): Third-party library for character encoding detection.
- `http.client` (from `proxy.py`): Standard library for HTTP client protocol.
- `http.server` (from `proxy.py`): Standard library for HTTP servers.
- `socketserver` (from `proxy.py`): Standard library for creating network servers.
- `urllib.parse` (from `proxy.py`): Standard library for parsing URLs.
- `tempfile` (from `proxy.py`): Standard library for creating temporary files and directories.
- `ssl` (from `proxy.py`): Standard library for SSL/TLS operations.
- `socket` (from `proxy.py`): Standard library for low-level networking.
- `OpenSSL.crypto` (from `proxy.py`): Third-party library for OpenSSL cryptography.

## Integration Points

### Public APIs
- `base64_tools.py`: Provides functions for direct Base64 encoding/decoding and image conversion.
- `browser_monitor.py`: Can be run as a standalone script with command-line arguments (`status`, `monitor`, `cleanup`).
- `clean.py`: The `clean_duplicate_articles` function can be imported and called.
- `fix.py`: The `fix_html` and `fix_article` functions can be imported and utilized in content processing pipelines.
- `github_updater.py`: Provides a `GitHubUpdater` class for programmatic repository management and can be executed via CLI.
- `html.py`: The `HtmlTools` class offers methods for detailed HTML cleaning, intended for use in content processing.
- `init_admin_user.py`: Designed to be run as a command-line utility (`--check`, `--fix`) for database administration.
- `moinfo.py`: The `getMoreInfo` function can be used to programmatically fetch WeChat article statistics.
- `proxy.py`: The `MitmProxy` class provides the core proxy functionality, and `ReqIntercept`/`RspIntercept` classes define extension points for interception logic. It can be started as a standalone proxy server.

### Data Flow
- **Content Processing**: Raw article content (often Markdown or HTML) flows through `fix.py` and `html.py` for cleaning and conversion, potentially leveraging `mdtools.md2html`. This cleaned content might then be stored in the database or exported.
- **Database Operations**: `clean.py` and `init_admin_user.py` directly interact with the project's database (`core.db`) to manage articles and user roles.
- **System Interactions**: `browser_monitor.py` and `github_updater.py` interact with the operating system (processes, file system) and external services (GitHub) respectively. `moinfo.py` makes external HTTP requests to WeChat.
- **Network Traffic**: `proxy.py` intercepts and processes all HTTP/HTTPS network traffic, allowing other modules or plugins to inspect or modify it.

## Implementation Notes

### Design Patterns
- **Utility Modules**: Many scripts within `tools` are designed as standalone utility modules (`base64_tools.py`, `html.py`), providing focused functionalities that can be imported and reused across the project.
- **Command-Line Interfaces**: Several scripts (`browser_monitor.py`, `github_updater.py`, `init_admin_user.py`) provide command-line interfaces, making them easy to execute for specific tasks or automation.
- **Plugin Architecture (Proxy)**: `proxy.py` utilizes a plugin-like architecture for request and response interception, allowing custom logic to be injected without modifying the core proxy implementation.
- **Configuration Objects**: Classes like `GitHubUpdater` and components within `proxy.py` accept configuration parameters during initialization, promoting flexibility.

### Technical Decisions
- **`psutil` for Process Monitoring**: `browser_monitor.py` leverages `psutil` for robust cross-platform process management and information retrieval.
- **`python-git` or `subprocess` for Git**: `github_updater.py` uses `subprocess` to directly call Git commands, providing fine-grained control over Git operations.
- **`BeautifulSoup` and `lxml` for HTML Parsing**: `html.py` relies on `BeautifulSoup` for HTML parsing and manipulation, with optional `lxml` support for XPath selectors, offering powerful content cleaning capabilities.
- **`OpenSSL.crypto` for SSL Interception**: `proxy.py` utilizes `OpenSSL.crypto` to generate and manage SSL certificates for HTTPS interception, enabling inspection of encrypted traffic.
- **External Dependencies for Specialized Tasks**: Tools like `moinfo.py` rely on `requests` and `pandas` for web scraping and data processing, demonstrating the use of appropriate external libraries for specialized tasks.

### Considerations
- **Security (Proxy)**: The `proxy.py` script, while powerful for debugging, inherently introduces security considerations due to its ability to intercept and potentially modify network traffic. Proper usage and secure configuration are critical.
- **External Service Dependencies (`moinfo.py`)**: `moinfo.py` relies on manually obtained session tokens/cookies for WeChat data retrieval, which can be fragile and break if the external service changes its authentication mechanisms.
- **Error Handling**: Many scripts include `try-except` blocks to handle common errors such as `FileNotFoundError`, network issues, or invalid input, aiming for graceful degradation.
- **Performance**: Some scripts might involve I/O-intensive operations (e.g., image processing in `base64_tools.py`, large file operations in `github_updater.py`, network requests in `moinfo.py`, `proxy.py`), and their performance should be monitored.
- **Maintainability**: The modular design with clear responsibilities for each script contributes to the overall maintainability of the `tools` directory.
