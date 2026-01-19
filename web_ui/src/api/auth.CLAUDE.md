# auth.ts

## Purpose and Scope
This module handles all authentication-related API interactions, including user login, token verification, QR code-based authentication, token refreshing, logout, and retrieving current user information.

## Structure Overview
This file exports several interfaces for data structures and functions for interacting with authentication API endpoints. It also manages interval-based polling for QR code status.

## Key Components
### LoginParams (Interface)
- Description: Defines the parameters required for user login.
- Responsibilities: Specifies the username and password for authentication.
- Key Properties:
  - `username (string)`: The user's account username.
  - `password (string)`: The user's account password.

### LoginResult (Interface)
- Description: Represents the result of a successful login operation.
- Responsibilities: Provides authentication tokens.
- Key Properties:
  - `access_token (string)`: The access token for API authorization.
  - `token_type (string)`: The type of the token (e.g., "Bearer").

### VerifyResult (Interface)
- Description: Represents the result of a token verification operation.
- Responsibilities: Indicates if a token is valid and provides associated user information.
- Key Properties:
  - `is_valid (boolean)`: True if the token is valid, false otherwise.
  - `username (string)`: The username associated with the token.
  - `expires_at (number, optional)`: Timestamp when the token expires.

### `login(data: LoginParams): Promise<LoginResult>`
- Purpose: Authenticates a user with a username and password to obtain an access token.
- Parameters:
  - `data (LoginParams)`: An object containing the `username` and `password`.
- Returns: (`Promise<LoginResult>`) A promise that resolves to a `LoginResult` object on successful login.

### `verifyToken(): Promise<VerifyResult>`
- Purpose: Verifies the validity of the current authentication token.
- Parameters: None.
- Returns: (`Promise<VerifyResult>`) A promise that resolves to a `VerifyResult` object, indicating token validity and user details.

### `QRCode(): Promise<any>`
- Purpose: Initiates a QR code-based authentication flow. It fetches a QR code and then continuously polls to check if the QR code has been scanned, resolving once the QR code is successfully scanned or rejecting on timeout/error.
- Parameters: None.
- Returns: (`Promise<any>`) A promise that resolves with the QR code data upon successful scan or rejects if the process times out or encounters an error.
- Throws: `Error` if fetching or polling the QR code times out.

### `checkQRCodeStatus(): Promise<any>`
- Purpose: Continuously polls the server to check the login status initiated by a QR code scan. It resolves when the user has successfully logged in via QR code and displays a success message.
- Parameters: None.
- Returns: (`Promise<any>`) A promise that resolves with the response from the status check once `login_status` is true.

### `refreshToken(): Promise<LoginResult>`
- Purpose: Refreshes the existing access token to extend the user's session without requiring re-authentication.
- Parameters: None.
- Returns: (`Promise<LoginResult>`) A promise that resolves to a new `LoginResult` object containing the refreshed tokens.

### `logout(): Promise<any>`
- Purpose: Invalidates the current user session and logs the user out.
- Parameters: None.
- Returns: (`Promise<any>`) A promise that resolves upon successful logout.

### `getCurrentUser(): Promise<any>`
- Purpose: Retrieves the details of the currently authenticated user.
- Parameters: None.
- Returns: (`Promise<any>`) A promise that resolves with the current user's data.

## Dependencies
### Internal Dependencies
- `./http` - Provides the HTTP client for making API requests.

### External Dependencies
- `axios` - Used directly in `QRCode` for head requests to check QR code status.
- `@arco-design/web-vue` - Specifically `Message` for displaying success notifications in `checkQRCodeStatus`.

## Integration Points
### Public APIs
- `login` - Used for username/password authentication.
- `verifyToken` - Used to check the validity of an existing token.
- `QRCode` - Used to initiate and monitor QR code login.
- `checkQRCodeStatus` - Used to continuously monitor QR code login status.
- `refreshToken` - Used to renew authentication tokens.
- `logout` - Used to terminate a user session.
- `getCurrentUser` - Used to fetch details of the logged-in user.

### Data Flow
- Input: `LoginParams` for `login`, implicit token for other calls.
- Processing: `login` converts parameters to `URLSearchParams`; `QRCode` and `checkQRCodeStatus` involve interval-based polling.
- Output: Promises resolving to `LoginResult`, `VerifyResult`, or other API response data.

## Implementation Notes
### Design Patterns
- **Module Pattern**: Functions are organized within the module by authentication concerns.
- **Polling**: `QRCode` and `checkQRCodeStatus` utilize polling mechanisms with `setInterval` to monitor asynchronous authentication states.

### Technical Decisions
- Uses `URLSearchParams` for `login` to send form-urlencoded data, which is common for token endpoints.
- Employs `axios.head` in `QRCode` to efficiently check for the existence of the QR code status endpoint without downloading the full response body.
- Integrates `Arco Design Vue`'s `Message` component for user feedback on QR code login success.
- Uses `clearInterval` to prevent memory leaks from `setInterval` calls, especially when re-initiating QR code processes.

### Considerations
- Performance: Polling mechanisms, especially with short intervals, can be resource-intensive. The `QRCode` function has a `maxAttempts` to prevent indefinite polling.
- Error Handling: Polling functions include `reject` calls for timeout or network errors. Callers of these functions should implement proper error handling.
- Security: Token management (storage, expiration, refresh) is crucial but largely handled by the `http` client and potentially higher-level application logic. This module focuses on the API interactions.
