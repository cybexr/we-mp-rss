# http.ts

## Purpose and Scope
This module configures and exports a pre-configured Axios instance (`http`) for making API requests. It centralizes HTTP request handling, including adding authorization tokens, standardizing API response processing, and displaying user-friendly error messages through interceptors. It serves as the core communication layer for all API interactions within the application.

## Structure Overview
This file initializes an Axios instance, defines request and response interceptors for global handling of API calls, and then exports this configured instance as the default export.

## Key Components
### `http` (AxiosInstance)
- Description: A pre-configured Axios instance for making HTTP requests to the backend API.
- Responsibilities:
  - Handles base URL and timeout settings.
  - Automatically attaches authorization tokens to requests.
  - Processes API responses, extracting data or handling errors based on standard API formats.
  - Displays toast notifications for errors.
  - Redirects to the login page on authentication failures.

#### Request Interceptor
- Purpose: Modifies outgoing request configurations before they are sent.
- Functionality:
  - Retrieves an authentication token using `getToken()`.
  - If a token exists, it adds an `Authorization` header with a `Bearer` token to the request.
  - Passes the modified (or original) `config` object to the next handler.
  - Rejects the promise if an error occurs during request preparation.

#### Response Interceptor
- Purpose: Processes incoming responses from the API or handles errors that occur during the request.
- Functionality (Successful Response Path):
  - Checks for a `response.data?.code === 0`, which indicates a successful API call according to the application's standard response format.
  - Extracts the actual data from `response.data?.data`, `response.data?.detail`, or `response.data`.
  - If `response.data?.code === 401`, it displays an "Unauthorized" message and redirects the user to the `/login` page.
  - If the `Content-Type` is `application/json` and the `code` is not `0` or `401`, it extracts an error message and displays it using `Message.error`.
  - Rejects the promise with an `Error` object containing the error message.
- Functionality (Error Response Path - `error.response` exists):
  - Extracts the HTTP status code (`error.response.status`).
  - Attempts to extract a specific error message from `error.response.data` (checking `detail.message`, `detail`, or `message`).
  - Handles specific HTTP status codes:
    - `401`: Displays "未登录或登录已过期，请重新登录。" and redirects to `/login`.
    - `403`: Displays "没有权限访问此资源" or specific error message.
    - `404`: Displays "请求的资源不存在" or specific error message.
    - `400`: Displays "请求参数错误" or specific error message.
    - `5xx`: Displays "服务器内部错误" or specific error message.
  - Displays the final error message using `Message.error`.
  - Rejects the promise with a new `Error` object containing the error message.
- Functionality (Network Error Path - no `error.response`):
  - Displays a generic "网络错误，请检查网络连接" message.
  - Rejects the promise with a new `Error` object containing the network error message.

## Dependencies
### Internal Dependencies
- `@/utils/auth` - Specifically `getToken()` for retrieving the authentication token.
- `@/router` - The Vue Router instance for programmatic navigation (e.g., to `/login`).

### External Dependencies
- `axios` - The HTTP client library used for making requests.
- `@arco-design/web-vue` - Specifically `Message` for displaying toast notifications to the user.

## Integration Points
### Public APIs
- `default export http` - This Axios instance is intended to be imported and used by all other API modules to make HTTP requests.

### Data Flow
- Outgoing Requests: All requests pass through the request interceptor, where an `Authorization` header may be added.
- Incoming Responses: All responses and errors pass through the response interceptor for standardized processing, data extraction, error notification, and potential redirection.

## Implementation Notes
### Design Patterns
- **Singleton**: The `http` Axios instance is configured once and then reused throughout the application, acting as a singleton for API communication.
- **Interceptor Pattern**: Axios interceptors are used to globally handle cross-cutting concerns like authentication and error handling.

### Technical Decisions
- **Base URL Configuration**: The `baseURL` is dynamically set using `import.meta.env.VITE_API_BASE_URL`, allowing for easy environment-specific API endpoint configuration.
- **Standardized Error Handling**: A consistent approach to parsing and displaying error messages from various API response formats and HTTP error statuses.
- **Vue Router Integration**: Direct integration with Vue Router for navigation to the login page upon authentication expiry.
- **Arco Design Integration**: Uses `Message.error` for user feedback, ensuring a consistent UI/UX for error notifications.

### Considerations
- **Security**: Ensures that tokens are sent with every authenticated request. The `getToken` utility is assumed to handle secure token storage.
- **Scalability**: Centralizing HTTP logic improves maintainability and makes it easier to implement global features like logging, retry mechanisms, or caching in the future.
- **Testability**: Components that use this `http` instance can be easily mocked during testing by mocking the `http` module itself.
