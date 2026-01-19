# tagManagement.ts

## Purpose and Scope
This module provides API functions for managing tags. It allows for listing, retrieving, creating, updating, and deleting tag entries.

## Structure Overview
This file exports functions that encapsulate API calls related to tag management. It imports interfaces for tag data from a shared types module.

## Key Components
### `listTags(params?: { offset?: number; limit?: number }): Promise<Tag[]>`
- Purpose: Retrieves a paginated list of tags.
- Parameters:
  - `params (object, optional)`: An object containing pagination parameters.
    - `offset (number, optional)`: The starting index for pagination (default: 0).
    - `limit (number, optional)`: The maximum number of tags to return (default: 100).
- Returns: (`Promise<Tag[]>`) A promise that resolves to an array of `Tag` objects.

### `getTag(id: string): Promise<Tag>`
- Purpose: Retrieves a single tag entry by its unique ID.
- Parameters:
  - `id (string)`: The unique identifier of the tag to retrieve.
- Returns: (`Promise<Tag>`) A promise that resolves to a `Tag` object representing the requested tag.

### `createTag(data: TagCreate): Promise<any>`
- Purpose: Creates a new tag entry.
- Parameters:
  - `data (TagCreate)`: An object containing the data for the new tag (e.g., tag name).
- Returns: (`Promise<any>`) A promise that resolves upon successful creation of the tag.

### `updateTag(id: string, data: TagCreate): Promise<any>`
- Purpose: Updates an existing tag entry identified by its ID.
- Parameters:
  - `id (string)`: The unique identifier of the tag to update.
  - `data (TagCreate)`: An object containing the updated data for the tag.
- Returns: (`Promise<any>`) A promise that resolves upon successful update of the tag.

### `deleteTag(id: string): Promise<any>`
- Purpose: Deletes a tag entry identified by its ID.
- Parameters:
  - `id (string)`: The unique identifier of the tag to delete.
- Returns: (`Promise<any>`) A promise that resolves upon successful deletion of the tag.

## Dependencies
### Internal Dependencies
- `./http` - Provides the HTTP client for making API requests.
- `@/types/tagManagement` - Imports `Tag` and `TagCreate` interfaces for type safety.

### External Dependencies
- None.

## Integration Points
### Public APIs
- `listTags` - Used to fetch a collection of tags.
- `getTag` - Used to fetch a single tag by ID.
- `createTag` - Used to add new tags.
- `updateTag` - Used to modify existing tags.
- `deleteTag` - Used to remove tags.

### Data Flow
- Input: `offset`, `limit` for listing; `id` for specific tag operations; `TagCreate` data for creating/updating.
- Processing: Pagination parameters are passed directly as query parameters.
- Output: Promises resolving to `Tag` objects or generic success responses.

## Implementation Notes
### Design Patterns
- **Module Pattern**: Functions are organized by their common purpose (tag management) within this module.
- **RESTful API Interaction**: Functions directly map to typical REST operations (GET, POST, PUT, DELETE) on `/wx/tags` endpoints.

### Technical Decisions
- Uses a shared `http` utility for all API calls to ensure consistent request handling.
- The `limit` for `listTags` defaults to 100, suggesting that tag lists are expected to be relatively small or that a higher default limit is preferred.

### Considerations
- Error Handling: Relies on the `http` client to manage and propagate API errors.
- Authentication/Authorization: It's assumed that the `http` client or an upstream layer handles authentication and authorization for these endpoints.
