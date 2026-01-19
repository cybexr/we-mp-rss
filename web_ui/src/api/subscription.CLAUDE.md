# subscription.ts

## Purpose and Scope
This module provides a comprehensive set of API functions for managing user subscriptions to official accounts (MPs). This includes functionality for retrieving lists of subscriptions, fetching details, adding new subscriptions, updating existing ones, deleting subscriptions, searching for MPs, managing MP categories, and triggering updates for MP articles.

## Structure Overview
This file defines several interfaces for data models and response structures, and exports numerous functions that encapsulate API calls related to subscription management.

## Key Components
### Subscription (Interface)
- Description: Represents a single official account subscription.
- Responsibilities: Defines the structure of an MP subscription object.
- Key Properties:
  - `id (string)`: Unique identifier for the subscription.
  - `mp_name (string)`: Name of the official account.
  - `mp_cover (string)`: URL for the cover image of the official account.
  - `mp_intro (string)`: Introduction or description of the official account.
  - `status (number)`: Current status of the subscription.
  - `cache_images (boolean)`: Indicates if images from this MP should be cached.
  - `remarks (string)`: User-defined remarks for the subscription.
  - `category (string)`: The category this MP belongs to.
  - `created_at (string)`: Timestamp when the subscription was created.
  - `last_publish_time (string | null, optional)`: The last time an article was published by this MP.
  - `article_count (number, optional)`: The total number of articles from this MP.
  - `sync_time (string, optional)`: Frontend-added field for last sync time.
  - `updated_at (string, optional)`: Frontend-added field for last update time.

### SubscriptionListResult (Interface)
- Description: Represents the API response structure for a list of subscriptions.
- Responsibilities: Provides a list of subscriptions and the total count.
- Key Properties:
  - `code (number)`: Status code of the API response.
  - `data (object)`:
    - `list (Subscription[])`: An array of `Subscription` objects.
    - `total (number)`: Total number of subscriptions available.

### AddSubscriptionParams (Interface)
- Description: Defines the parameters required to add a new subscription.
- Responsibilities: Specifies the essential information for a new official account subscription.
- Key Properties:
  - `mp_name (string)`: Name of the official account.
  - `mp_id (string)`: Unique ID of the official account.
  - `avatar (string)`: URL for the avatar image of the official account.
  - `mp_intro (string, optional)`: Introduction of the official account.
  - `cache_images (boolean, optional)`: Whether to cache images.
  - `remarks (string, optional)`: Remarks for the subscription.
  - `category (string, optional)`: Category for the subscription.

### MpItem (Interface)
- Description: Represents a simplified official account item, typically used in search results.
- Key Properties:
  - `mp_id (string)`: Unique ID of the official account.
  - `mp_name (string)`: Name of the official account.
  - `avatar (string)`: URL for the avatar image.

### MpSearchResult (Interface)
- Description: Represents the API response structure for searching official accounts.
- Key Properties:
  - `code (number)`: Status code of the API response.
  - `data (MpItem[])`: An array of `MpItem` objects.

### BatchUpdateCategoryParams (Interface)
- Description: Defines parameters for updating the category of multiple official accounts in a batch.
- Key Properties:
  - `mp_ids (string[])`: An array of official account IDs to update.
  - `category (string)`: The new category to assign to the specified MPs.

### `getSubscriptions(params?: { page?: number; pageSize?: number; kw?: string; category?: string }): Promise<SubscriptionListResult>`
- Purpose: Retrieves a paginated list of subscribed official accounts, with optional keyword and category filtering.
- Parameters:
  - `params (object, optional)`: Query parameters.
    - `page (number, optional)`: Current page number (0-indexed, default 0).
    - `pageSize (number, optional)`: Items per page (default 10).
    - `kw (string, optional)`: Keyword for searching MP names (default empty string).
    - `category (string, optional)`: Category to filter subscriptions by. If undefined, all categories are included.
- Returns: (`Promise<SubscriptionListResult>`) A promise that resolves to a `SubscriptionListResult`.

### `getSubscriptionDetail(mp_id: string): Promise<{code: number, data: Subscription}>`
- Purpose: Retrieves detailed information for a specific subscribed official account.
- Parameters:
  - `mp_id (string)`: The unique ID of the official account.
- Returns: (`Promise<{code: number, data: Subscription}>`) A promise resolving to an object with status code and `Subscription` details.

### `addSubscription(data: AddSubscriptionParams): Promise<{code: number, message: string}>`
- Purpose: Adds a new official account subscription.
- Parameters:
  - `data (AddSubscriptionParams)`: The data for the new subscription.
- Returns: (`Promise<{code: number, message: string}>`) A promise resolving to an object indicating success or failure.

### `getSubscriptionInfo(url: string): Promise<{code: number, message: string}>`
- Purpose: Retrieves subscription information by an article URL. This likely extracts MP details from the article.
- Parameters:
  - `url (string)`: The URL of an article from an official account.
- Returns: (`Promise<{code: number, message: string}>`) A promise resolving to an object with status code and message.

### `deleteMpApi(mp_id: string): Promise<{code: number, message: string}>`
- Purpose: Deletes an official account subscription by its ID.
- Parameters:
  - `mp_id (string)`: The unique ID of the official account to delete.
- Returns: (`Promise<{code: number, message: string}>`) A promise resolving to an object indicating success or failure.
- Note: This function is functionally identical to `deleteSubscription`.

### `deleteSubscription(mp_id: string): Promise<{code: number, message: string}>`
- Purpose: Deletes an official account subscription by its ID.
- Parameters:
  - `mp_id (string)`: The unique ID of the official account to delete.
- Returns: (`Promise<{code: number, message: string}>`) A promise resolving to an object indicating success or failure.
- Note: This function is functionally identical to `deleteMpApi`.

### `UpdateMps(mp_id: string, params: { start_page?: number; end_page?: number }): Promise<{code: number, message: string}>`
- Purpose: Triggers an update for articles of a specific official account (or all if `mp_id` is 'all').
- Parameters:
  - `mp_id (string)`: The ID of the official account to update, or 'all' to update all.
  - `params (object)`:
    - `start_page (number, optional)`: Starting page for article updates (default 0).
    - `end_page (number, optional)`: Ending page for article updates (default 1).
- Returns: (`Promise<{code: number, message: string}>`) A promise resolving to an object indicating success or failure.

### `updateSubscription(mp_id: string, data: Partial<Subscription>): Promise<{code: number, message: string}>`
- Purpose: Updates specific fields of an existing official account subscription.
- Parameters:
  - `mp_id (string)`: The unique ID of the official account to update.
  - `data (Partial<Subscription>)`: An object containing the fields to be updated.
- Returns: (`Promise<{code: number, message: string}>`) A promise resolving to an object indicating success or failure.

### `searchBiz(kw: string, params: { page?: number; pageSize?: number }): Promise<SubscriptionListResult>`
- Purpose: Searches for official accounts by a keyword, returning paginated results. This may search a broader "business" or general MP directory.
- Parameters:
  - `kw (string)`: The keyword to search for.
  - `params (object)`: Pagination parameters similar to `getSubscriptions`.
- Returns: (`Promise<SubscriptionListResult>`) A promise that resolves to a `SubscriptionListResult` (though the data type suggests `MpSearchResult` might be more appropriate given `MpItem`).

### `searchMps(kw: string, params: { page?: number; pageSize?: number }): Promise<SubscriptionListResult>`
- Purpose: Searches for official accounts by a keyword, returning paginated results. This endpoint might search specifically within already subscribed MPs or a filtered list.
- Parameters:
  - `kw (string)`: The keyword to search for (default empty string).
  - `params (object)`: Pagination parameters.
- Returns: (`Promise<SubscriptionListResult>`) A promise that resolves to a `SubscriptionListResult`.

### `getCategories(): Promise<{code: number, data: { categories: string[] }}>`
- Purpose: Retrieves a list of all available categories for official accounts.
- Parameters: None.
- Returns: (`Promise<{code: number, data: { categories: string[] }}>`) A promise resolving to an object containing a list of category strings.

### `batchUpdateCategory(params: BatchUpdateCategoryParams): Promise<{updated_count: number}>`
- Purpose: Updates the category for multiple official accounts in a single request.
- Parameters:
  - `params (BatchUpdateCategoryParams)`: An object containing an array of `mp_ids` and the `category` to assign.
- Returns: (`Promise<{updated_count: number}>`) A promise resolving to an object indicating the number of updated subscriptions.

## Dependencies
### Internal Dependencies
- `./http` - Provides the HTTP client for making API requests.

### External Dependencies
- None.

## Integration Points
### Public APIs
- `getSubscriptions` - Main entry point for fetching subscribed MP lists.
- `getSubscriptionDetail` - For displaying detailed MP information.
- `addSubscription` - For user-initiated subscriptions.
- `getSubscriptionInfo` - For adding subscriptions via article URL.
- `deleteMpApi`, `deleteSubscription` - For removing subscriptions.
- `UpdateMps` - For triggering article updates for MPs.
- `updateSubscription` - For modifying MP details.
- `searchBiz`, `searchMps` - For finding official accounts.
- `getCategories` - For populating category filters or management UIs.
- `batchUpdateCategory` - For bulk category assignments.

### Data Flow
- Input: Pagination parameters, keywords, MP IDs, subscription data, category data, article URLs.
- Processing: Parameters are converted from `page`/`pageSize` to `offset`/`limit`. Queries are constructed with path parameters and query strings.
- Output: Promises resolving to various structured data (lists, single items, status messages, updated counts).

## Implementation Notes
### Design Patterns
- **Module Pattern**: All subscription-related API interactions are encapsulated within this module.
- **RESTful API Interaction**: Functions directly correspond to REST endpoints and HTTP methods.

### Technical Decisions
- Uses a shared `http` utility for all API calls, ensuring consistency in request handling, authorization, and error management.
- Handles pagination by converting `page` and `pageSize` into `offset` and `limit` for backend compatibility.
- The `category` parameter in `getSubscriptions` is conditionally included to allow for filtering including blank categories.

### Considerations
- **Redundant Functions**: `deleteMpApi` and `deleteSubscription` are identical, which could indicate a refactoring opportunity.
- **Search Result Type**: The `searchBiz` and `searchMps` functions return `SubscriptionListResult` but might be logically better suited to return `MpSearchResult` if they are truly for searching *potential* MPs rather than *subscribed* ones.
- **Error Handling**: Relies on the `http` client's interceptors for global error handling and notifications.
