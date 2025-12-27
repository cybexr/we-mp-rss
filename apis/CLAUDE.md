# APIs Module Documentation

## Overview

The `apis` module contains all FastAPI route handlers and API endpoint definitions for the WeChat MP RSS system. This module serves as the web interface layer, handling HTTP requests, authentication, and response formatting.

## Architecture

### Core Components

- **Base Infrastructure**: `base.py` provides common response utilities and search functionality
- **Authentication**: `auth.py` handles user authentication, token management, and WeChat login flows
- **Article Management**: `article.py` provides CRUD operations for article content
- **RSS Management**: `rss.py` handles RSS feed operations
- **System APIs**: `sys_info.py`, `ver.py` provide system information and versioning

## File Structure

### Base Infrastructure

- `base.py` - Core response utilities and search keyword formatting
  - `BaseResponse` - Standard API response model
  - `success_response()`, `error_response()` - Response formatting helpers
  - `format_search_kw()` - Search query preprocessing

### Authentication & Security

- `auth.py` - Authentication endpoints and token management
  - OAuth2 password flows
  - WeChat QR code login integration
  - JWT token creation and validation
- `ver.py` - API version information and compatibility

### Content Management

- `article.py` - Article CRUD operations and management
  - **Article List** (`GET/POST /articles`): Paginated article listing with filtering
    - Query parameters: `offset`, `limit`, `status`, `search`, `mp_id`, `has_content`
    - Supports both `ArticleBase` (lightweight) and `Article` (full content) queries
    - Automatic feed name enrichment via `mp_id` lookup
  - **Article Detail** (`GET /articles/{article_id}`): Single article retrieval
  - **Article Deletion** (`DELETE /articles/{article_id}`): Soft/hard delete based on config
  - **Article Navigation** (`GET /articles/{article_id}/(next|prev)`): Sequential article browsing within same feed
  - **Content Re-extraction** (`POST /articles/{article_id}/reextract`): Re-fetch article content
    - Supports both `web` (browser) and `WxGather` extraction modes
    - Handles deleted content detection
  - **Orphan Cleanup** (`DELETE /articles/clean`): Removes articles with non-existent feed references
  - **Duplicate Cleanup** (`DELETE /articles/clean_duplicate_articles`): Removes duplicate articles using `tools.clean.clean_duplicate_articles()`
- `rss.py` - RSS feed operations and management
  - Feed parsing and processing
  - RSS subscription management

### System Operations

- `sys_info.py` - System information and status endpoints
- `config_management.py` - Configuration management APIs
- `export.py` - Data export functionality
- `message_task.py` - Message and task queue operations
- `tools.py` - Utility endpoints and helper functions

### Integration Points

- `github_update.py` - GitHub integration and update mechanisms
- `mps.py` - WeChat MP (Official Account) integration
- `tags.py` - Tag management and categorization
- `user.py` - User management operations
- `res.py` - Resource management endpoints

## Key Patterns

### Response Format Standardization
All endpoints use the consistent response format defined in `base.py`:
```python
{
    "code": 0,           # 0 for success, non-zero for errors
    "message": "success", # Human-readable status message
    "data": {...}        # Response payload (optional)
}
```

### Authentication Flow
- JWT-based authentication with configurable expiration
- WeChat QR code login integration for MP accounts
- Role-based access control through `get_current_user` dependency

### Database Integration
- SQLAlchemy ORM with session management via `core.db.DB`
- Consistent error handling and transaction management
- Search functionality with keyword preprocessing

## Dependencies

### Internal Dependencies
- `core.auth` - Authentication utilities and token management
- `core.db` - Database session management
- `core.models` - SQLAlchemy model definitions
- `core.config` - Configuration management
- `driver.*` - External service integrations (WeChat API)

### External Dependencies
- FastAPI - Web framework and routing
- Pydantic - Data validation and serialization
- SQLAlchemy - ORM and database operations

## API Categories

### Authentication Endpoints (`/auth`)
- User login and token generation
- WeChat QR code authentication
- Token refresh and validation

### Article Management (`/articles`)
- Article CRUD operations
- Search and filtering
- Orphaned article cleanup

### RSS Operations (`/rss`)
- Feed management
- RSS parsing and processing
- Subscription handling

### System Information (`/sys`, `/ver`)
- System status and health checks
- API version information
- Configuration management

### Integration APIs
- GitHub update mechanisms
- WeChat MP integration (`mps.py`)
  - **GET /wx/mps**: List all feeds with optional category filtering
    - Query parameters: `limit`, `offset`, `kw` (keyword), `category`
    - Response includes: `cache_images`, `remarks`, `category` fields
  - **POST /wx/mps**: Create new feed with new field support
    - Body parameters: `cache_images` (bool), `remarks` (string), `category` (string)
  - **PUT /wx/mps/{mp_id}`: Update feed metadata (NEW endpoint)
    - Body: JSON object with any combination of `cache_images`, `remarks`, `category`
    - Validates: `cache_images` is boolean, strings <= 255 characters
  - **GET /wx/mps/categories**: List all unique category values (NEW endpoint)
  - Example usage:
    ```bash
    # Get feeds filtered by category
    GET /wx/mps?category=technology&limit=10

    # Update feed metadata
    PUT /wx/mps/MP_WXS_123
    {
      "cache_images": true,
      "remarks": "Updated notes",
      "category": "tech-news"
    }
    ```
- Message queue operations

## Error Handling

All endpoints follow consistent error handling patterns:
- HTTP status codes mapped to response codes
- Structured error messages with human-readable descriptions
- Database transaction rollback on errors
- Comprehensive logging through `core.print` utilities

## Security Considerations

- JWT token validation on protected endpoints
- Input validation through Pydantic models
- SQL injection prevention through SQLAlchemy ORM
- Rate limiting considerations for API endpoints
- WeChat API security integration

## Development Notes

- All routers follow FastAPI conventions with dependency injection
- Consistent use of `success_response` and `error_response` utilities
- Database operations use context managers for proper session handling
- Integration with core models for data consistency
- Comprehensive error logging for debugging and monitoring