# Core Module Documentation

## Overview

The `core` module contains the core business logic, data models, and utility functions for the WeChat Mini Program RSS Reader system. This module serves as the foundation layer, handling database operations, authentication, RSS processing, and business rules.

## Architecture

### Core Components

- **Data Models**: `models/` contains SQLAlchemy ORM models for all database entities
- **Authentication**: `auth.py` provides JWT-based authentication and password hashing
- **Database**: `db.py` and `database.py` manage database connections and operations
- **RSS Processing**: `rss.py` handles RSS feed parsing and article extraction
- **Configuration**: `config.py` manages system configuration
- **Logging**: `log.py` provides centralized logging functionality
- **Queue System**: `queue/` handles background task processing
- **Notifications**: `notice/` manages various notification channels (DingTalk, Feishu, WeChat)

## Data Models

### Article Models (`models/article.py`)
- **ArticleBase**: Base article model with metadata
  - Fields: id, mp_id, title, pic_url, url, description, status, publish_time, created_at, updated_at, is_export
- **Article**: Extended article model with full content
  - Additional field: content (Text)

### User Model (`models/user.py`)
- Manages user authentication and profile data
- Handles WeChat integration and user preferences

### Other Models
- **Feed** (`models/feed.py`): RSS feed subscription management
  - Fields: id, mp_name, mp_cover, mp_intro, status, sync_time, update_time, created_at, updated_at, faker_id
  - **New Fields**:
    - `cache_images` (Boolean, default=False): Controls automatic image caching during article content extraction
    - `remarks` (String(255), default=''): User-defined notes or comments for this feed
    - `category` (String(255), default=''): Custom category for organizing and filtering feeds
  - Usage Example:
    ```python
    from core.models.feed import Feed

    # Create feed with image caching enabled
    feed = Feed(
        id="MP_WXS_123",
        mp_name="Tech Blog",
        cache_images=True,  # Enable automatic image caching
        remarks="High-quality tech articles",
        category="technology"
    )
    ```
- **MessageTask**: Notification task management
- **Tags**: Article tagging and categorization
- **ConfigManagement**: Dynamic configuration storage

## Authentication System

The authentication system uses JWT (JSON Web Tokens) with bcrypt password hashing:

### Key Features
- JWT-based stateless authentication
- Password hashing with bcrypt
- WeChat login integration
- Token expiration management
- OAuth2PasswordBearer scheme

### Configuration
- `SECRET_KEY`: JWT signing key (configurable)
- `ALGORITHM`: HS256 encryption algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token lifetime (default 30 minutes)

## Database Layer

### Connection Management
- Centralized database connection through `db.py`
- Connection pooling and session management
- Tag-based connection tracking for debugging

### Base Model
- Common fields: id, created_at, updated_at, status
- Soft delete support with status field
- Automatic timestamp management

## RSS Processing

### Feed Management
- RSS feed parsing and validation
- Article extraction and content processing
- Duplicate detection and handling
- Feed update scheduling

### Content Processing
- **Content Formatting** (`content_format.py`): Image preprocessing and HTML sanitization
  - `preprocess_image_attributes()`: Resolves lazy-loading image attributes
    - Priority order: data-src → data-original → data-lazy → srcset → src
    - Handles responsive images (srcset, data-lazy-srcset)
    - Filters data:image and placeholder URLs
  - `format_content()`: Main content formatting entry point
- **RSS Generation** (`rss.py`): Multi-format RSS feed generation
  - `generate_rss()`: Standard RSS 2.0 format with content:encoded support
  - `generate_atom()`: Atom syndication format
  - `generate_json()`: JSON feed format
  - `add_logo_prefix_to_urls()`: Prepends `/static/res/logo/` to image URLs
  - `clear_cache()`: Cache management with path traversal protection
  - `cache_content()`/`get_cached_content()`: Article content caching
  - `datetime_to_rfc822()`: Timezone-aware datetime conversion (CST/UTC+8)
- HTML sanitization
- Image processing and storage

## Notification System

### Supported Channels
- **DingTalk**: Enterprise messaging
- **Feishu**: Collaboration platform
- **WeChat**: In-app notifications
- **Custom**: Extensible notification framework

### Message Queuing
- Background task processing
- Retry mechanisms
- Failure handling and logging

## Utilities

### File Operations (`common/file_tools.py`)
- File upload/download handling
- Image processing and optimization
- Storage management

### Template Processing (`lax/template_parser.py`)
- Custom template engine
- Dynamic content rendering
- RSS feed generation

### Queue Management (`queue/queue.py`)
- Background task scheduling
- Job priority management
- Worker process coordination

## Configuration

The system uses a centralized configuration approach:
- YAML-based configuration files
- Environment variable overrides
- Runtime configuration updates
- Feature flags and toggles

## Error Handling

### Common Patterns
- Custom exception classes
- Consistent error responses
- Logging and monitoring
- Graceful degradation

### Error Categories
- Authentication errors
- Validation errors
- Database errors
- External service errors

## Security Considerations

### Data Protection
- Password hashing with bcrypt
- SQL injection prevention through ORM
- XSS protection in content processing
- Input validation and sanitization

### Access Control
- JWT-based authentication
- Role-based access control
- API rate limiting
- Session management

## Performance Optimizations

### Database
- Connection pooling
- Query optimization
- Index usage
- Caching strategies

### Processing
- Asynchronous task processing
- Batch operations
- Memory-efficient parsing
- Lazy loading

## Integration Points

### External Services
- WeChat API integration
- RSS feed sources
- Notification services
- File storage systems

### Internal APIs
- RESTful API layer
- WebSocket support
- Event-driven architecture
- Service-to-service communication