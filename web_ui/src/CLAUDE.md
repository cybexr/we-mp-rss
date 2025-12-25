# Web UI Source Documentation

## Overview

The `web_ui/src` directory contains the frontend Vue.js application for the WeChat Mini Program RSS Reader management interface. This single-page application provides administrators and users with a modern, responsive interface to manage RSS feeds, articles, and system settings.

## Architecture

### Technology Stack
- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite
- **UI Library**: Arco Design Vue
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **TypeScript**: Full TypeScript support
- **Internationalization**: Vue I18n

### Project Structure

```
web_ui/src/
├── api/              # API service layer
├── assets/           # Static assets (images, styles)
├── components/       # Reusable Vue components
│   ├── Layout/       # Layout components
└── views/            # Page components
```

## API Layer (`api/`)

The API layer provides TypeScript interfaces and service functions for backend communication:

### Core Services
- **article.ts**: Handles all article-related CRUD (Create, Read, Update, Delete) operations, including fetching lists, details, and management actions.
  - **Interfaces**:
    - `Article`: Defines the structure of an article, including `id`, `title`, `content`, `mp_name`, `publish_time`, `status`, `link`, and `created_at`.
    - `ArticleListParams`: Parameters for querying article lists, including `offset`, `limit`, `search`, `status`, and `mp_id`. Note: The `getArticles` function internally converts `page` and `pageSize` from Vue components into `offset` and `limit` for the API.
  - **Functions**:
    - `getArticles(params: ArticleListParams)`: Fetches a paginated list of articles based on provided search, status, and MP ID.
    - `getArticleDetail(id: number, action_type: number)`: Retrieves detailed information for a specific article. The `action_type` parameter (-1 for previous, 1 for next, 0 or default for current) allows navigation.
    - `getPrevArticleDetail(id: number)`: Fetches the previous article relative to the given ID (now typically handled by `getArticleDetail`).
    - `getNextArticleDetail(id: number)`: Fetches the next article relative to the given ID (now typically handled by `getArticleDetail`).
    - `deleteArticle(id: number)`: Deletes a specific article.
    - `ClearArticle()`: Clears all invalid articles from the database.
    - `ClearDuplicateArticle()`: Clears all duplicate articles from the database.
    - `reextractArticle(id: number)`: Triggers a re-extraction of content for a specific article.

- **auth.ts**: Authentication and user session management
- **configManagement.ts**: System configuration management
- **export.ts**: Data export functionality
- **file.ts**: File upload/download operations
- **messageTask.ts**: Notification and message task management
- **subscription.ts**: RSS feed subscription management
- **sysInfo.ts**: System information and status
- **tagManagement.ts**: Article tagging and categorization
- **tools.ts**: Utility functions and tools
- **user.ts**: User profile and preference management
- **http.ts**: HTTP client configuration and interceptors

### API Patterns
- Consistent error handling
- Request/response interceptors
- TypeScript type safety
- Async/await pattern
- Centralized endpoint management

## Components (`components/`)

### Layout Components (`Layout/`)
- **BasicLayout.vue**: Main application layout wrapper
- **Navbar.vue**: Navigation bar with user menu and actions

### Reusable Components
- **ACodeEditor.vue**: Code editor with syntax highlighting
- **CronExpressionPicker.vue**: Cron expression builder for scheduling
- **CustomPieChart.vue**: Data visualization component
- **ExportModal.vue**: Export configuration dialog
- **ExportRecords.vue**: Export history viewer

### Component Patterns
- Composition API with `<script setup>`
- Props and emits typing
- Scoped slots for flexibility
- Reactive state management
- Event-driven communication

## Views (`views/`)

### Page Structure
Each view typically contains:
- Data fetching logic
- State management
- User interaction handling
- Form validation
- Table/list displays
- Modal dialogs

### Common Features
- Responsive design
- Loading states
- Error handling
- Pagination
- Search and filtering
- Bulk operations

### ArticleListDesktop.vue
This component serves as the primary interface for managing articles and subscriptions for desktop users. It integrates various functionalities to provide a comprehensive content management experience.

- **Purpose**: Displays a list of articles from subscribed public accounts, allowing users to view, manage, and interact with article content and subscription settings.
- **Key Features**:
  - **Subscription Management**:
    - **Add Subscription**: Navigate to a page for adding new public accounts.
    - **Export/Import Public Accounts**: Functionality to export and import public account lists (CSV).
    - **Export OPML**: Export subscriptions in OPML format.
    - **Delete Public Account**: Remove a subscribed public account.
    - **Copy MP ID**: Easily copy the ID of a public account.
  - **Article Listing & Interaction**:
    - **Paginated Article List**: Displays articles with server-side pagination.
    - **Search & Filter**: Search articles by title and filter by public account.
    - **Article Details View**: Open articles in a modal for reading, with options to navigate to previous/next articles.
    - **Re-extract Article**: Manually trigger content re-extraction for an article.
    - **Delete Article**: Individual article deletion.
    - **Batch Delete**: Delete multiple selected articles simultaneously.
    - **Clear Invalid Articles**: Remove articles marked as invalid.
    - **Clear Duplicate Articles**: Remove duplicate articles.
  - **Feed Generation**:
    - **Dynamic RSS Feeds**: Generate RSS, Atom, JSON, Markdown, or Text feeds based on the active public account or all articles, with optional search parameters.
  - **Refresh & Authorization**:
    - **Manual Refresh**: Trigger a refresh of articles for a selected public account within a specified page range.
    - **Refresh WeChat Authorization**: Re-authenticate with WeChat if needed.
  - **Export Articles**: Trigger an export modal for articles.
- **Components Used**:
  - `ExportModal.vue`: Used for handling article export configurations.
  - `TextIcon.vue`: Utility component for displaying text as an icon.
- **Data Properties**: Manages various reactive states including `articles`, `mpList`, `pagination` (for articles and public accounts), `searchText`, `mpSearchText`, `selectedRowKeys` (for batch operations), `activeMpId`, `activeFeed`, `refreshForm`, `currentArticle`, and modal visibility states.
- **Methods**: Contains handlers for page changes, search actions, article viewing, deletion, re-extraction, batch operations, subscription management (add, export, import), and feed generation.

## Main Application (`App.vue`)

### Key Features
- Internationalization support with multiple languages
- WeChat integration with QR code authentication
- Theme and layout configuration
- Router-based navigation
- Global state management

### Language Support
The application supports extensive language localization:
- Chinese (Simplified/Traditional)
- English
- Russian
- French
- Dutch
- Norwegian
- And many more...

## State Management

### Global State
- User authentication status
- Application configuration
- Language preferences
- Theme settings

### Component State
- Local reactive data
- Props from parent components
- Computed properties
- Watchers for side effects

## Routing

### Route Structure
- Login page (`/login`)
- Dashboard (`/`)
- Article management
- RSS feed management
- User settings
- System administration

### Navigation Guards
- Authentication checks
- Role-based access control
- Route redirections

## Styling

### CSS Architecture
- Scoped styles for components
- Global CSS variables
- Arco Design theme customization
- Responsive design patterns
- CSS Grid and Flexbox layouts

### Theme System
- Light/dark mode support
- Custom color schemes
- Consistent spacing and typography
- Brand-aligned design tokens

## Performance Optimizations

### Code Splitting
- Route-based code splitting
- Component lazy loading
- Async component loading
- Bundle size optimization

### Runtime Performance
- Virtual scrolling for large lists
- Image lazy loading
- Debounced search
- Efficient reactivity patterns

## Build Configuration

### Vite Setup
- TypeScript compilation
- Hot module replacement
- Development server proxy
- Production optimizations

### Environment Variables
- API endpoint configuration
- Feature flags
- Environment-specific settings

## Testing Strategy

### Component Testing
- Unit tests for individual components
- Mock API responses
- User interaction testing
- Visual regression testing

### Integration Testing
- API integration
- Routing behavior
- State management
- Cross-component communication

## Security Considerations

### Client-Side Security
- XSS prevention
- Input sanitization
- Secure token storage
- CSRF protection

### Data Protection
- Sensitive data handling
- Secure communication
- Access control validation
- Audit logging

## Accessibility

### WCAG Compliance
- Keyboard navigation
- Screen reader support
- Color contrast
- Focus management
- ARIA labels

### Usability Features
- Clear visual hierarchy
- Consistent interactions
- Error messaging
- Help documentation

## Internationalization (i18n)

### Implementation
- Vue I18n integration
- Dynamic language switching
- Date/time formatting
- Number formatting
- RTL language support

### Translation Management
- JSON translation files
- Namespace organization
- Pluralization rules
- Context-aware translations

## Development Workflow

### Development Server
- Hot reload functionality
- API proxy configuration
- Source maps for debugging
- ESLint integration

### Build Process
- TypeScript compilation
- Asset optimization
- Bundle analysis
- Deployment preparation

## Browser Compatibility

### Supported Browsers
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Polyfills
- Core JavaScript features
- Web APIs
- CSS features
- Legacy browser support