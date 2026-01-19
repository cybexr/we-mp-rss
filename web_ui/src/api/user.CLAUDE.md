# user.ts

## Purpose and Scope
This module provides API functions for user management. It enables fetching user profile information, updating user details (including nickname, email, and activity status), changing user passwords, and uploading a user's avatar.

## Structure Overview
This file defines several interfaces for user-related data structures and exports functions that encapsulate API calls to user management endpoints.

## Key Components
### UserInfo (Interface)
- Description: Represents the detailed profile information of a user.
- Responsibilities: Defines the structure of a user object returned from the API.
- Key Properties:
  - `username (string)`: The unique username of the user.
  - `nickname (string)`: The display name of the user.
  - `email (string)`: The email address of the user.
  - `avatar (string)`: The URL to the user's avatar image.
  - `role (string)`: The role assigned to the user (e.g., 'admin', 'user').
  - `is_active (boolean)`: Indicates if the user account is active.
  - `created_at (string)`: Timestamp when the user account was created.

### UpdateUserParams (Interface)
- Description: Defines the parameters for updating a user's profile.
- Responsibilities: Specifies which user fields can be modified.
- Key Properties:
  - `username (string, optional)`: New username.
  - `nickname (string, optional)`: New nickname.
  - `email (string, optional)`: New email address.
  - `avatar (string, optional)`: New avatar URL.
  - `password (string, optional)`: New password (for a full update, not specifically for password change endpoint).
  - `is_active (boolean, optional)`: New active status.

### ChangePasswordParams (Interface)
- Description: Defines the parameters specifically for changing a user's password.
- Responsibilities: Requires both the old and new passwords for verification.
- Key Properties:
  - `old_password (string)`: The user's current password.
  - `new_password (string)`: The desired new password.

### `getUserInfo(): Promise<{code: number, data: UserInfo}>`
- Purpose: Fetches the detailed profile information of the current authenticated user.
- Parameters: None.
- Returns: (`Promise<{code: number, data: UserInfo}>`) A promise that resolves to an object containing a status code and the `UserInfo` object.

### `updateUserInfo(data: UpdateUserParams): Promise<{code: number, message: string}>`
- Purpose: Updates general profile information for the current user.
- Parameters:
  - `data (UpdateUserParams)`: An object containing the fields to be updated.
- Returns: (`Promise<{code: number, message: string}>`) A promise that resolves to an object indicating the success or failure of the update.

### `changePassword(data: ChangePasswordParams): Promise<{code: number, message: string}>`
- Purpose: Allows the user to change their password by providing the old and new passwords.
- Parameters:
  - `data (ChangePasswordParams)`: An object containing `old_password` and `new_password`.
- Returns: (`Promise<{code: number, message: string}>`) A promise that resolves to an object indicating the success or failure of the password change.

### `changePasswordLegacy(newPassword: string): Promise<{code: number, message: string}>`
- Purpose: A backward-compatible function to change the user's password using the `updateUserInfo` endpoint. This is less secure as it doesn't require the old password.
- Parameters:
  - `newPassword (string)`: The new password to set.
- Returns: (`Promise<{code: number, message: string}>`) A promise that resolves to an object indicating the success or failure of the password change.

### `toggleUserStatus(active: boolean): Promise<{code: number, message: string}>`
- Purpose: Toggles the `is_active` status of the current user.
- Parameters:
  - `active (boolean)`: The desired active status (true for active, false for inactive).
- Returns: (`Promise<{code: number, message: string}>`) A promise that resolves to an object indicating the success or failure of the status update.

### `uploadAvatar(file: File): Promise<{code: number, url: string}>`
- Purpose: Uploads a new avatar image for the user.
- Parameters:
  - `file (File)`: The `File` object representing the avatar image to upload.
- Returns: (`Promise<{code: number, url: string}>`) A promise that resolves to an object containing a status code and the URL of the newly uploaded avatar.

<h2>Dependencies</h2>
<h3>Internal Dependencies</h3>
<ul>
<li><code>./http</code> - Provides the HTTP client for making API requests.</li>
</ul>
<h3>External Dependencies</h3>
<ul>
<li>None.</li>
</ul>

<h2>Integration Points</h2>
<h3>Public APIs</h3>
<ul>
<li><code>getUserInfo</code> - For displaying user profile in the UI.</li>
<li><code>updateUserInfo</code> - For user profile editing forms.</li>
<li><code>changePassword</code> - For dedicated change password functionality.</li>
<li><code>changePasswordLegacy</code> - For backward compatibility in password changes.</li>
<li><code>toggleUserStatus</code> - For administrative or self-service account activation/deactivation.</li>
<li><code>uploadAvatar</code> - For updating user profile pictures.</li>
</ul>
<h3>Data Flow</h3>
<ul>
<li>Input: User credentials, profile data, new password, avatar file.</li>
<li>Processing: Data is sent as JSON for updates and password changes; <code>FormData</code> is used for avatar upload.</li>
<li>Output: Promises resolving to user info objects or success/error messages.</li>
</ul>

<h2>Implementation Notes</h2>
<h3>Design Patterns</h3>
<ul>
<li><strong>Module Pattern</strong>: User management API interactions are encapsulated.</li>
</ul>
<h3>Technical Decisions</h3>
<ul>
<li>Uses a shared <code>http</code> utility for all API calls.</li>
<li><code>changePassword</code> explicitly overrides headers to include <code>Content-Type: application/json</code> and <code>Authorization</code>, potentially for an endpoint that requires specific handling or if the global interceptor is bypassed for some reason. The use of <code>localStorage.getItem('token')</code> here bypasses the global request interceptor's token injection, which might be an oversight or a deliberate design choice for this specific endpoint.</li>
<li><code>uploadAvatar</code> uses <code>FormData</code> and <code>multipart/form-data</code> for file uploads.</li>
<li>Includes a legacy password change method for backward compatibility.</li>
</ul>
<h3>Considerations</h3>
<ul>
<li><strong>Security</strong>: The direct retrieval of token from <code>localStorage</code> in <code>changePassword</code> might be less robust than relying on the `http` interceptor for consistency. Password changes should always be handled securely.</li>
<li><strong>Error Handling</strong>: Relies on the <code>http</code> client's interceptors for global error handling.</li>
</ul>
