# messageTask.ts

## Purpose and Scope
This module provides API functions for managing message tasks. It allows for listing, retrieving, running, creating, updating, refreshing, and deleting message tasks.

## Structure Overview
This file exports functions that encapsulate API calls related to message task management. It imports interfaces for message task data from a shared types module.

## Key Components
### `listMessageTasks(params?: { offset?: number; limit?: number }): Promise<MessageTask>`
- Purpose: Retrieves a paginated list of message tasks.
- Parameters:
  - `params (object, optional)`: An object containing pagination parameters.
    - `offset (number, optional)`: The starting index for pagination (default: 0).
    - `limit (number, optional)`: The maximum number of tasks to return (default: 10).
- Returns: (`Promise<MessageTask>`) A promise that resolves to a `MessageTask` object, typically containing a list of tasks and pagination metadata.

### `getMessageTask(id: string): Promise<MessageTask>`
- Purpose: Retrieves a single message task by its unique ID.
- Parameters:
  - `id (string)`: The unique identifier of the message task.
- Returns: (`Promise<MessageTask>`) A promise that resolves to a `MessageTask` object representing the requested task.

### `RunMessageTask(id: string, isTest: boolean = false): Promise<MessageTask>`
- Purpose: Executes a specific message task.
- Parameters:
  - `id (string)`: The unique identifier of the message task to run.
  - `isTest (boolean, optional)`: If `true`, runs the task in a test mode (default: `false`).
- Returns: (`Promise<MessageTask>`) A promise that resolves to a `MessageTask` object, likely reflecting the updated status after running.

### `createMessageTask(data: MessageTaskUpdate): Promise<any>`
- Purpose: Creates a new message task.
- Parameters:
  - `data (MessageTaskUpdate)`: An object containing the data for the new message task.
- Returns: (`Promise<any>`) A promise that resolves upon successful creation of the message task.

### `updateMessageTask(id: string, data: MessageTaskUpdate): Promise<any>`
- Purpose: Updates an existing message task identified by its ID.
- Parameters:
  - `id (string)`: The unique identifier of the message task to update.
  - `data (MessageTaskUpdate)`: An object containing the updated data for the message task.
- Returns: (`Promise<any>`) A promise that resolves upon successful update of the message task.

### `FreshJobApi(): Promise<any>`
- Purpose: Triggers a refresh of all message task jobs.
- Parameters: None.
- Returns: (`Promise<any>`) A promise that resolves upon successful refresh of all jobs.

### `FreshJobByIdApi(id: string, data: MessageTaskUpdate): Promise<any>`
- Purpose: Triggers a refresh for a specific message task job identified by its ID.
- Parameters:
  - `id (string)`: The unique identifier of the message task job to refresh.
  - `data (MessageTaskUpdate)`: Contains update information, though its direct use in a "fresh job" context might be for specific status updates or re-initialization.
- Returns: (`Promise<any>`) A promise that resolves upon successful refresh of the specified job.

### `deleteMessageTask(id: string): Promise<any>`
- Purpose: Deletes a message task identified by its ID.
- Parameters:
  - `id (string)`: The unique identifier of the message task to delete.
- Returns: (`Promise<any>`) A promise that resolves upon successful deletion of the message task.

## Dependencies
### Internal Dependencies
- `./http` - Provides the HTTP client for making API requests.
- `@/types/messageTask` - Imports `MessageTask` and `MessageTaskUpdate` interfaces for type safety.

### External Dependencies
- None.

## Integration Points
### Public APIs
- `listMessageTasks` - Used to fetch a collection of message tasks.
- `getMessageTask` - Used to fetch a single message task by ID.
- `RunMessageTask` - Used to execute a message task.
- `createMessageTask` - Used to add new message tasks.
- `updateMessageTask` - Used to modify existing message tasks.
- `FreshJobApi` - Used to refresh all message task jobs.
- `FreshJobByIdApi` - Used to refresh a specific message task job.
- `deleteMessageTask` - Used to remove message tasks.

### Data Flow
- Input: `offset`, `limit` for listing; `id` for specific task operations; `isTest` for running; `MessageTaskUpdate` data for creating/updating.
- Processing: Pagination parameters are passed directly; `isTest` is appended as a query parameter.
- Output: Promises resolving to `MessageTask` objects or generic success responses.

## Implementation Notes
### Design Patterns
- **Module Pattern**: Functions are organized by their common purpose (message task management) within this module.
- **RESTful API Interaction**: Functions directly map to typical REST operations (GET, POST, PUT, DELETE) on `/wx/message_tasks` and related endpoints.

### Technical Decisions
- Uses a shared `http` utility for all API calls to ensure consistent request handling.
- The `RunMessageTask` function demonstrates how query parameters are handled for optional flags like `isTest`.

### Considerations
- Error Handling: Relies on the `http` client to manage and propagate API errors.
- Authentication/Authorization: It's assumed that the `http` client or an upstream layer handles authentication and authorization for these endpoints.
