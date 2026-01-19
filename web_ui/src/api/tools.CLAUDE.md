# tools.ts

## Purpose and Scope
This module provides API functions for various utility tools, primarily focusing on the export of articles and the management of their corresponding export records. It allows for flexible article export options (e.g., format, content modifications) and the ability to list and delete generated export files.

## Structure Overview
This file exports functions that encapsulate API calls for interacting with tools-related endpoints on the backend.

## Key Components
### `exportArticles(params: any): Promise<{code: number, data: string}>`
- Purpose: Initiates an article export process based on specified criteria.
- Parameters:
  - `params (any)`: An object containing various export configuration options.
    - `mp_id (string)`: The ID of the official account from which to export articles.
    - `scope ('all' | 'selected')`: Determines whether to export all articles or only selected ones.
    - `ids (string[]), optional)`: An array of article IDs to export if `scope` is 'selected'.
    - `limit (number, optional)`: Number of articles per page to process (default: 10).
    - `page_count (number, optional)`: Number of pages to export (default: 1).
    - `add_title (boolean, optional)`: Whether to include titles in the exported content (default: true).
    - `remove_images (boolean, optional)`: Whether to remove images from the exported content (default: false).
    - `remove_links (boolean, optional)`: Whether to remove links from the exported content (default: false).
    - `export_md (boolean)`: Whether to export in Markdown format.
    - `export_docx (boolean)`: Whether to export in DOCX format.
    - `export_json (boolean)`: Whether to export in JSON format.
    - `export_csv (boolean)`: Whether to export in CSV format.
    - `export_pdf (boolean)`: Whether to export in PDF format.
    - `zip_filename (string, optional)`: Custom filename for a ZIP archive if multiple formats/files are exported.
- Returns: (`Promise<{code: number, data: string}>`) A promise that resolves to an object containing a status code and potentially a URL or identifier for the exported file(s).

### `getExportRecords(params: any): Promise<{code: number, data: string}>`
- Purpose: Retrieves a list of previously generated article export records.
- Parameters:
  - `params (any)`: An object containing query parameters.
    - `mp_id (string)`: The ID of the official account to filter export records by.
- Returns: (`Promise<{code: number, data: string}>`) A promise that resolves to an object containing a status code and a list of export records.

### `DeleteExportRecords(params: any): Promise<{code: number, data: string}>`
- Purpose: Deletes specific article export records.
- Parameters:
  - `params (any)`: An object containing parameters for deletion.
    - `mp_id (string, optional)`: The ID of the official account associated with the records to delete.
    - `filename (string)`: The filename of the specific export record to delete.
- Returns: (`Promise<{code: number, data: string}>`) A promise that resolves to an object indicating the success or failure of the deletion.

## Dependencies
### Internal Dependencies
- `./http` - Provides the HTTP client for making API requests.

### External Dependencies
- None.

## Integration Points
### Public APIs
- `exportArticles` - Used to trigger the export of articles, likely from an administration or content management interface.
- `getExportRecords` - Used to display a history or list of generated export files to the user.
- `DeleteExportRecords` - Used to clean up old or unwanted export files.

### Data Flow
- Input: `params` objects containing detailed configurations for export, filtering for records, and identification for deletion.
- Processing: `exportArticles` constructs a request body with boolean flags for various export formats and content modifications. `getExportRecords` and `DeleteExportRecords` use query parameters or request body for filtering and identification.
- Output: Promises resolving to objects containing status codes and data relevant to the operation (e.g., export file identifiers, record lists).

## Implementation Notes
### Design Patterns
- **Module Pattern**: All tools-related API interactions are encapsulated within this module.

### Technical Decisions
- Uses a shared `http` utility for all API calls, ensuring consistency in request handling and error management.
- The `exportArticles` function explicitly sets `Content-Type: application/json` and `Accept: application/json` headers, indicating a JSON-based request body and expected JSON response. It also includes `X-Requested-With: XMLHttpRequest`, which is often used to identify AJAX requests.
- The `DeleteExportRecords` function uses a request body (`data`) for the DELETE operation, which is less common than query parameters but valid.

### Considerations
- **Error Handling**: Relies on the `http` client's interceptors for global error handling and notifications.
- **Backend Coupling**: The extensive parameter list for `exportArticles` suggests a tightly coupled frontend-backend understanding of export logic.
- **Asynchronous Nature**: Exporting articles, especially a large number, can be a long-running process on the server. The `data` field in the response might contain a job ID for status polling rather than the direct exported file.
