# WeChat Mini Program RSS Reader (ygg-we-mp-rss)

## Project Overview

The WeChat Mini Program RSS Reader is a comprehensive RSS feed management system specifically designed for WeChat Mini Programs. It provides a complete solution for RSS feed aggregation, content management, and distribution through WeChat's ecosystem.

## Architecture

### System Components

- **Backend APIs (`apis/`)**: FastAPI-based REST API layer handling all HTTP requests
- **Core Business Logic (`core/`)**: Centralized business rules, data models, and services
- **Web UI (`web_ui/`)**: Vue.js 3 management interface for administration and user management
- **Mini Program Integration**: WeChat Mini Program frontend for end-user access
- **Job Processing (`jobs/`)**: Background tasks for RSS fetching and content processing
- **Notification System**: Multi-channel notifications (DingTalk, Feishu, WeChat)

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM with support for multiple databases
- **Authentication**: JWT with bcrypt password hashing
- **Task Queue**: Custom queue system for background processing
- **RSS Processing**: Custom RSS parser and content extractor

#### Frontend
- **Web UI**: Vue.js 3 with TypeScript, Arco Design
- **Mini Program**: WeChat Mini Program framework
- **State Management**: Pinia for Vue.js
- **Build Tools**: Vite for modern build pipeline

## Key Features

### RSS Management
- RSS feed subscription and management
- Automatic content fetching and parsing
- Duplicate detection and handling
- Content categorization and tagging
- **Feed metadata**: Custom remarks, categorization, and image caching preferences per feed
- **Category filtering**: Organize and filter feeds by custom categories
- **Image caching control**: Per-feed toggle for automatic image caching during content extraction

### Content Processing
- HTML sanitization and cleaning
- Image processing and optimization
- Content format adaptation for mobile
- Full-text search support

### User Management
- WeChat authentication integration
- User preference management
- Multi-language support (12+ languages)
- Personalized content delivery

### Notification System
- Real-time push notifications
- Multiple notification channels
- Scheduled digest delivery
- Custom notification rules

### Admin Interface
- Web-based administration panel
- System monitoring and analytics
- User management and analytics
- Content moderation tools

## Development Workflow

### Project Structure
```
ygg-we-mp-rss/
├── apis/              # API endpoint definitions
├── core/              # Core business logic
├── web_ui/            # Vue.js admin interface
├── jobs/              # Background job processors
├── utils/             # Utility modules
├── tools/             # Development and maintenance tools
├── docs/              # Documentation and guides
├── examples/          # Code examples and demos
├── schemas/           # Data schemas and validation
├── script/            # Setup and maintenance scripts
└── compose/           # Docker configuration
```

### Getting Started

1. **Installation**
   - Clone the repository
   - Install dependencies with `pip install -r requirements.txt`
   - Configure `config.yaml` with your settings

2. **Database Setup**
   - Initialize database with provided scripts
   - Run migrations for schema setup
   - Load initial configuration data

3. **Running the Application**
   - Start the backend server: `python main.py`
   - Access the admin UI at `http://localhost:8000`
   - Configure WeChat Mini Program with API endpoints

### Configuration

#### Environment Variables
- `SECRET_KEY`: JWT signing key
- `DATABASE_URL`: Database connection string
- `WECHAT_APP_ID`: WeChat Mini Program ID
- `WECHAT_APP_SECRET`: WeChat Mini Program secret

#### Configuration File (`config.yaml`)
- Database settings
- API endpoint configuration
- Notification service settings
- RSS fetch intervals

## API Documentation

### Core Endpoints
- `/api/auth/`: Authentication and user management
- `/api/articles/`: Article CRUD operations
- `/api/rss/`: RSS feed management
- `/api/subscriptions/`: User subscription management
- `/api/notifications/`: Notification configuration
- `/api/export/`: Data export functionality

### Authentication
- JWT-based stateless authentication
- WeChat OAuth integration
- Role-based access control
- API key support for external integrations

## Deployment

### Docker Support
- Simplified single Dockerfile for production builds (amd64 architecture)
- Docker Compose for complete stack deployment
- Environment-based configuration
- Automated Aliyun ACR deployment via GitHub Actions

### Production Considerations
- Database connection pooling
- Redis caching layer
- Load balancing support
- SSL/TLS termination
- Logging and monitoring setup

## Security

### Data Protection
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection in content processing
- CSRF protection for web interface

### Access Control
- JWT token-based authentication
- Role-based permissions
- API rate limiting
- Session management

## Monitoring and Maintenance

### Logging
- Structured JSON logging
- Multiple log levels
- Centralized log aggregation
- Performance metrics

### Health Checks
- Application health endpoints
- Database connectivity checks
- External service monitoring
- Automated alerting

## Contributing

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests
- Update documentation for new features

### Testing
- Unit tests for core logic
- Integration tests for APIs
- End-to-end tests for critical workflows
- Performance testing for RSS processing

## License

This project is licensed under the terms specified in the LICENSE file. Please review the license for usage permissions and restrictions.

## Support

For issues, questions, or contributions:
- Create GitHub issues for bug reports
- Check documentation for common questions
- Review examples for integration patterns
- Follow development guidelines for contributions