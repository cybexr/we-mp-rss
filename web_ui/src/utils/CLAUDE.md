# utils Module

## Purpose and Scope
The `utils` directory serves as a centralized collection of utility functions and modules designed to provide common helper functionalities across the `web_ui` application. It encapsulates reusable logic, ranging from authentication token management and browser notifications to date formatting, constant definitions, and integration with the internationalization (i18n) library. This promotes code reusability, maintainability, and a clear separation of concerns within the project.

## Structure Overview
The `utils` directory is organized into individual TypeScript files, each dedicated to a specific utility concern. It also contains a subdirectory, `i18n`, which houses the `translate.js` library.

- `auth.ts`: Handles authentication-related utility functions.
- `browserNotification.ts`: Provides functionalities for browser-based notifications.
- `constants.ts`: Defines application-wide constant values.
- `date.ts`: Contains utility functions for date and time manipulation.
- `translate.ts`: Integrates with the i18n library and manages page translation state.
- `i18n/`: A subdirectory containing the `i18n-jsautotranslate` library. For detailed documentation on this module, refer to `i18n/CLAUDE.md`.

## Key Components
### `auth.ts`
- Description: Manages the storage and retrieval of authentication tokens.
- Responsibilities: Provides a simple interface for interacting with `localStorage` for token management.
#### Key Methods:
#### `getToken(): string | null`
- Purpose: Retrieves the authentication token from `localStorage`.
- Parameters: None
- Returns: (string | null) The stored token string, or `null` if not found.

### `browserNotification.ts`
- Description: Implements browser notification features, including playing sounds, flashing the document title, and showing native browser notifications for new articles.
- Responsibilities: Manages notification permissions, state, and triggers visual/auditory alerts.
#### Key Methods:
#### `getNotificationEnabled(): boolean`
- Purpose: Retrieves the current status of browser notifications (enabled/disabled) from `localStorage`.
- Parameters: None
- Returns: (boolean) `true` if notifications are enabled, `false` otherwise.
#### `enableBrowserNotification(): Promise<boolean>`
- Purpose: Enables browser notifications. It requests notification permissions, initializes article count, and starts a polling mechanism to check for new articles.
- Parameters: None
- Returns: (Promise<boolean>) A promise that resolves to `true` if notifications were successfully enabled, `false` otherwise.
#### `disableBrowserNotification(): void`
- Purpose: Disables browser notifications, stops polling, title flashing, and resets the document title.
- Parameters: None
- Returns: (void)
#### `toggleBrowserNotification(): Promise<boolean>`
- Purpose: Toggles the state of browser notifications between enabled and disabled.
- Parameters: None
- Returns: (Promise<boolean>) A promise that resolves to the new notification status (`true` if enabled, `false` if disabled).
#### `initBrowserNotification(): void`
- Purpose: Initializes browser notifications based on the saved state in `localStorage` when the page loads.
- Parameters: None
- Returns: (void)
#### `resetTitle(): void`
- Purpose: Stops title flashing and restores the original document title.
- Parameters: None
- Returns: (void)

### `constants.ts`
- Description: Defines global constants and utility functions related to resource URLs and image handling.
- Responsibilities: Provides consistent access to base URLs and image processing logic.
#### Key Properties:
- `RES_BASE_URL (string)`: Base URL for static resources (e.g., `/static/res/logo/`).
#### Key Methods:
#### `Avatar(url: string): string`
- Purpose: Prepends `RES_BASE_URL` to an image URL if it's not an absolute URL.
- Parameters:
    - `url (string)`: The original image URL.
- Returns: (string) The processed image URL.
#### `ProxyImage(content: string): string`
- Purpose: Replaces image `src` attributes in HTML content to proxy them through `/static/res/logo/` and removes `width` attributes.
- Parameters:
    - `content (string)`: The HTML string containing image tags.
- Returns: (string) The modified HTML string.

### `date.ts`
- Description: Provides utility functions for formatting dates and timestamps.
- Responsibilities: Standardizes date and time display across the application.
#### Key Methods:
#### `formatDateTime(date: string | Date | undefined): string`
- Purpose: Formats a given date or date string into 'YYYY-MM-DD HH:mm' format.
- Parameters:
    - `date (string | Date | undefined)`: The date to format. Can be a string, Date object, or undefined.
- Returns: (string) The formatted date string, or '-' if the input is undefined.
#### `formatTimestamp(timestamp: number | undefined): string`
- Purpose: Formats a given Unix timestamp (seconds or milliseconds) into 'YYYY-MM-DD HH:mm' format.
- Parameters:
    - `timestamp (number | undefined)`: The timestamp to format.
- Returns: (string) The formatted date string, or '-' if the input is undefined.

### `translate.ts`
- Description: Integrates with the `i18n-jsautotranslate` library to handle page translation, manage translation state, and detect content changes.
- Responsibilities: Provides functions to trigger translation, set current language, and manage content hashes for change detection.
#### Key Methods:
#### `hash(str: string): string`
- Purpose: Generates a hash for a given string.
- Parameters:
    - `str (string)`: The input string.
- Returns: (string) The hash value as a string.
#### `set_hash(): void`
- Purpose: Stores the hash of the current `document.body.innerText` in `localStorage` for change detection.
- Parameters: None
- Returns: (void)
#### `get_hash(): string | null`
- Purpose: Retrieves the stored hash of `document.body.innerText` from `localStorage`.
- Parameters: None
- Returns: (string | null) The stored hash, or `null` if not found.
#### `translatePage(): void`
- Purpose: Triggers page translation if a saved language is found in `localStorage` and the page content hash has changed.
- Parameters: None
- Returns: (void)
#### `setCurrentLanguage(language: string): void`
- Purpose: Sets the current language for translation using the `i18n` library and saves it to `localStorage`.
- Parameters:
    - `language (string)`: The language code to set.
- Returns: (void)

## Dependencies
### Internal Dependencies
- `i18n/index.js` - `translate.ts` depends on the global `translate` object exported by the `i18n` module for core translation functionalities.

### External Dependencies
- **`localStorage`**: Used by `auth.ts`, `browserNotification.ts`, and `translate.ts` for persisting user preferences and state (e.g., authentication tokens, notification status, selected language, content hashes).
- **`dayjs`**: A lightweight JavaScript date library used in `date.ts` for parsing, validating, manipulating, and displaying dates and times.
- **`vue`**: Specifically `ref` and `watchEffect` from Vue are imported in `translate.ts`, indicating that this utility module is used within a Vue.js application context.
- **Browser APIs**:
    - `Notification`: Used in `browserNotification.ts` for native browser push notifications.
    - `HTMLAudioElement`: Used in `browserNotification.ts` for playing notification sounds.
    - `document`: Extensively used across multiple utilities for DOM manipulation and access (e.g., `document.title`, `document.body.innerText`).
    - `window.setInterval`, `window.clearInterval`, `setTimeout`: For timed operations in `browserNotification.ts` and `translate.ts`.

## Integration Points
- **Application-wide Utilities**: Functions from this `utils` directory are imported and used throughout the `web_ui` application as needed.
- **Authentication Flow**: `getToken` is used to retrieve user authentication status.
- **User Interface**: `browserNotification` functions integrate with the UI to provide user feedback (e.g., enabling/disabling notifications).
- **Content Display**: `constants` are used for consistent asset paths, and `date` utilities for displaying formatted dates.
- **Internationalization**: `translate.ts` acts as a bridge to the core `i18n` module, handling language switching and ensuring content is translated. It interacts closely with the Vue.js reactivity system (`watchEffect`).
- **Dynamic Content Updates**: `translatePage` and `Has_Change` are designed to re-translate content dynamically in response to DOM changes, likely triggered by Vue component updates or data fetching.

## Implementation Notes
### Design Patterns
- **Modularization**: Each utility concern is separated into its own file, promoting a modular and organized codebase.
- **Facade Pattern**: The `translate.ts` module acts as a facade over the more complex `i18n` library, providing a simplified interface for common translation tasks within the application.
- **Singleton (implicit)**: The browser's `localStorage` acts as an implicit singleton for state management across different utility modules.

### Technical Decisions
- **`localStorage` for Persistence**: User preferences and transient state (like authentication tokens, notification settings, and current language) are stored in `localStorage` for persistence across sessions.
- **Dynamic Imports**: `browserNotification.ts` uses dynamic imports for `getArticles` from `@/api/article` to avoid circular dependencies and load modules only when needed.
- **Content Hashing for Change Detection**: `translate.ts` uses content hashing of `document.body.innerText` to efficiently detect changes in the page content and trigger re-translation only when necessary, optimizing performance.
- **Vue.js Integration**: The use of `ref` and `watchEffect` in `translate.ts` demonstrates direct integration with Vue's reactivity system, allowing translation logic to react to component lifecycle and data changes.

### Considerations
- **Global State**: Reliance on `localStorage` for storing settings means that changes made in one browser tab might not immediately reflect in another, or across different browser profiles.
- **Performance of `document.body.innerText`**: Hashing `document.body.innerText` can be computationally intensive on very large or frequently updated pages, though the `setTimeout` and change detection help mitigate this.
- **`@ts-ignore` Usage**: The presence of `@ts-ignore` comments suggests potential type mismatches or incomplete type definitions for external modules or API responses.
- **Audio File Encoding**: The `NOTIFICATION_SOUND_URL` uses a base64 encoded WAV file, which can increase the size of the JavaScript bundle but avoids an extra network request for the audio file.
