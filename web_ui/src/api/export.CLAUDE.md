# export.ts

## Purpose and Scope
This module provides API functions for exporting and importing data related to official accounts (MPs) and tags. This includes exporting MP data in OPML format, exporting/importing MP data as a file, and exporting/importing tag data as a file.

## Structure Overview
This file exports functions that encapsulate API calls for various data import/export operations.

## Key Components
### `ExportOPML(): Promise<{code: number, data: string}>`
- Purpose: Exports official account (MP) data in OPML format.
- Parameters: None explicitly, but internally sends `limit` and `offset` parameters.
- Returns: (`Promise<{code: number, data: string}>`) A promise that resolves to an object containing a status code and the OPML data as a string.

### `ExportMPS(): Promise<any>`
- Purpose: Exports official account (MP) data as a file (blob).
- Parameters: None explicitly, but internally sends `limit` and `offset` parameters.
- Returns: (`Promise<any>`) A promise that resolves to a response containing the MP data as a blob, typically to be downloaded by the client.

### `ImportMPS(formData: FormData): Promise<{code: number, data: string}>`
- Purpose: Imports official account (MP) data from a file.
- Parameters:
  - `formData (FormData)`: A `FormData` object containing the file to be imported.
- Returns: (`Promise<{code: number, data: string}>`) A promise that resolves to an object indicating the success or failure of the import operation.

### `ExportTags(): Promise<any>`
- Purpose: Exports tag data as a file (blob).
- Parameters: None explicitly, but internally sends `limit` and `offset` parameters.
- Returns: (`Promise<any>`) A promise that resolves to a response containing the tag data as a blob, typically to be downloaded by the client.

### `ImportTags(formData: FormData): Promise<{code: number, data: string}>`
- Purpose: Imports tag data from a file.
- Parameters:
  - `formData (FormData)`: A `FormData` object containing the file to be imported.
- Returns: (`Promise<{code: number, data: string}>`) A promise that resolves to an object indicating the success or failure of the import operation.

## Dependencies
### Internal Dependencies
- `./http` - Provides the HTTP client for making API requests.

### External Dependencies
- None.

## Integration Points
### Public APIs
- `ExportOPML` - Used to get OPML data for MPs.
- `ExportMPS` - Used to download MP data as a file.
- `ImportMPS` - Used to upload a file for MP data import.
- `ExportTags` - Used to download tag data as a file.
- `ImportTags` - Used to upload a file for tag data import.

### Data Flow
- Input: `FormData` for import operations; implicit `limit` and `offset` for export operations.
- Processing: HTTP requests are made with specific headers for `multipart/form-data` for imports and `responseType: 'blob'` for file exports.
- Output: Promises resolving to API response objects, including file data as blobs.

## Implementation Notes
### Design Patterns
- **Module Pattern**: Functions are grouped by their common purpose (import/export) within this module.

### Technical Decisions
- Uses a shared `http` utility for all API calls.
- Explicitly sets `Content-Type: multipart/form-data` for import operations, which is necessary when sending `FormData`.
- Sets `responseType: 'blob'` for export functions that return file downloads, allowing the browser to handle the file as binary data.
- Export functions implicitly pass `limit: 1000, offset: 0` suggesting an attempt to export all available data within a single call.

### Considerations
- Large Data Exports: The `limit: 1000` for exports might be insufficient for very large datasets, potentially requiring pagination or a different export mechanism for scalability.
- Error Handling: Relies on the `http` client to manage and propagate API errors.
- User Experience: Client-side logic will be needed to handle the downloaded blobs (e.g., creating a download link) and to provide feedback on import status.
