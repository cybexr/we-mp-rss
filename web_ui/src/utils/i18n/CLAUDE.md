# i18n Module

## Purpose and Scope
This module, `i18n-jsautotranslate` (commonly referred to as `translate.js`), provides a comprehensive solution for automatic HTML translation within web applications. Its primary goal is to enable multi-language support with minimal development effort, offering features such as automatic language detection, dynamic content translation, and SEO-friendly server-side translation capabilities (TCDN). It aims to be highly customizable, performant, and self-contained, requiring no external API keys for basic functionality.

## Structure Overview
The `i18n` directory contains the core JavaScript library (`index.js`), its licensing information (`LICENSE`), package metadata (`package.json`), and extensive documentation (`README.md`).
- `index.js`: The main script implementing all translation logic, UI components, and integration points.
- `LICENSE`: Contains the MIT License under which the library is distributed.
- `package.json`: Defines the module's name, version, description, dependencies, and scripts for npm.
- `README.md`: Provides detailed feature descriptions, usage instructions, configuration options, examples, and deployment guides.

## Key Components
The module exposes a global `translate` object that serves as the primary interface for all its functionalities.

### `translate` (Global Object)
- Description: The main entry point for the translation library.
- Responsibilities: Orchestrates the entire translation process, manages state, and provides utility functions.

#### Key Methods:
#### `setUseVersion2(): void`
- Purpose: (Deprecated) Used to explicitly set the library to use version 2. Newer versions default to v2/v3.
- Parameters: None
- Returns: (void)
#### `changeLanguage(languageName: string): void`
- Purpose: Switches the current display language of the page to the specified `languageName`. It intelligently handles page reloads and propagation to iframes.
- Parameters:
    - `languageName (string)`: The target language code (e.g., 'english', 'chinese_simplified', 'en', 'zh-CN').
- Returns: (void)
#### `setAutoDiscriminateLocalLanguage(): void`
- Purpose: Configures the library to automatically detect and set the user's local language on their first visit.
- Parameters: None
- Returns: (void)
#### `setDocuments(documents: HTMLElement | HTMLElement[]): void`
- Purpose: Specifies which DOM elements should be considered for translation. If not set, the entire `document.documentElement` is considered.
- Parameters:
    - `documents (HTMLElement | HTMLElement[])`: A single DOM element or an array of elements to translate.
- Returns: (void)
#### `getDocuments(): HTMLElement[]`
- Purpose: Retrieves the array of DOM elements currently configured for translation.
- Parameters: None
- Returns: (HTMLElement[]) An array of DOM elements.
#### `execute(docs?: HTMLElement | HTMLElement[]): void`
- Purpose: Initiates the translation process for the specified `docs` or the configured `documents` (or entire page). It scans for translatable text, checks caches, and makes API requests if necessary.
- Parameters:
    - `docs (HTMLElement | HTMLElement[] | undefined)`: Optional. Specific DOM elements to translate. If omitted, uses previously set documents or the entire page.
- Returns: (void)

### `translate.selectLanguageTag`
- Description: Manages the UI component for language selection (typically a `<select>` dropdown).
- Responsibilities: Renders and updates the language selection dropdown, handles user selection.

#### Key Properties:
- `documentId (string)`: The ID for the HTML element where the language selection dropdown will be rendered.
- `show (boolean)`: Controls the visibility of the language selection dropdown.
- `languages (string)`: Comma-separated list of supported language codes to display in the dropdown.
- `alreadyRender (boolean)`: Internal flag indicating if the dropdown has already been rendered.
#### Key Methods:
#### `refreshRender(): void`
- Purpose: Forces a re-render of the language selection dropdown, useful after manual changes to `translate.to`.
- Parameters: None
- Returns: (void)
#### `customUI(languageList: {id: string, name: string}[]): void`
- Purpose: Customizes the rendering logic for the language selection UI.
- Parameters:
    - `languageList ({id: string, name: string}[])`: An array of objects, each containing a language `id` and `name`.
- Returns: (void)
#### `render(): void`
- Purpose: Renders the language selection dropdown based on configured settings and fetched language lists.
- Parameters: None
- Returns: (void)

### `translate.ignore`
- Description: Defines rules for elements, classes, IDs, or specific text to be excluded from translation.
- Responsibilities: Provides methods to check if an element or text should be ignored.

#### Key Properties:
- `tag (string[])`: Array of HTML tag names to ignore (e.g., `['style', 'script']`).
- `class (string[])`: Array of CSS class names to ignore (e.g., `['ignore']`).
- `id (string[])`: Array of element IDs to ignore.
- `text (string[])`: Array of exact text strings to ignore.
- `textRegex (RegExp[])`: Array of regular expressions for text patterns to ignore.
#### Key Methods:
#### `isIgnore(ele: HTMLElement): boolean`
- Purpose: Checks if a given DOM element or any of its parent elements should be ignored based on tag, class, or ID rules.
- Parameters:
    - `ele (HTMLElement)`: The DOM element to check.
- Returns: (boolean) `true` if the element or an ancestor should be ignored, `false` otherwise.
#### `setTextRegexs(arr: RegExp[]): void`
- Purpose: Adds regular expressions to the `textRegex` list for ignoring text patterns.
- Parameters:
    - `arr (RegExp[])`: An array of regular expression objects.
- Returns: (void)

### `translate.nomenclature`
- Description: Manages custom translation terms, allowing users to define specific translations for certain words or phrases.
- Responsibilities: Stores and applies user-defined terminology.

#### Key Properties:
- `data (object)`: A multi-dimensional array storing custom translations keyed by source language, target language, and original text.
#### Key Methods:
#### `append(from: string, to: string, properties: string): void`
- Purpose: Appends custom translation terms to the nomenclature database.
- Parameters:
    - `from (string)`: The source language code.
    - `to (string)`: The target language code.
    - `properties (string)`: A string where each line is in "key=value" format, defining custom translations.
- Returns: (void)
#### `get(): object`
- Purpose: Retrieves the current custom nomenclature data.
- Parameters: None
- Returns: (object) The `data` object containing all custom terms.

### `translate.office`
- Description: Provides utilities for offline translation data management, including exporting and importing custom terms and full extracted translation data.
- Responsibilities: Facilitates the creation and utilization of offline translation resources.

#### Key Methods:
#### `export(): void`
- Purpose: Exports current page translation terms into a format suitable for custom nomenclature. Requires the target language to be different from the local language.
- Parameters: None
- Returns: (void)
#### `showPanel(): void`
- Purpose: Displays a UI panel for exporting configuration information.
- Parameters: None
- Returns: (void)
#### `append(to: string, properties: string): void`
- Purpose: Appends offline translation data (key-value pairs) for a specific target language into the browser's storage.
- Parameters:
    - `to (string)`: The target language code.
    - `properties (string)`: A string with "key=value" pairs, representing original text and its translation.
- Returns: (void)

#### `translate.office.fullExtract`
- Description: Sub-component for managing full extraction of translation data into IndexedDB.
#### Key Methods:
#### `set(hash: string, originalText: string, toLanguage: string, translateText: string): Promise<void>`
- Purpose: Stores a translation pair (original and translated text) along with its hash and target language in IndexedDB.
- Parameters:
    - `hash (string)`: Hashed value of the original text.
    - `originalText (string)`: The original text.
    - `toLanguage (string)`: The language the text was translated into.
    - `translateText (string)`: The translated text.
- Returns: (Promise<void>)
#### `export(to: string): Promise<void>`
- Purpose: Exports all stored translation data from IndexedDB for a given target language into a downloadable text file.
- Parameters:
    - `to (string)`: The target language code for which to export translations.
- Returns: (Promise<void>)
#### Key Properties:
- `isUse (boolean)`: Flag to enable/disable the full extraction capability.

### `translate.listener`
- Description: Monitors DOM changes and dynamically translates newly added or modified content.
- Responsibilities: Detects mutations, filters relevant changes, and triggers translation for new content.

#### Key Properties:
- `isStart (boolean)`: Indicates if the listener has been started.
- `use (boolean)`: Flag from user's code to determine if listener should activate.
- `ignoreNode (object)`: A map of node UUIDs to their expiration times and translated text, used to prevent infinite translation loops.
- `translateExecuteNodeIgnoreExpireTime (number)`: Duration in milliseconds for which a node is ignored after translation by `execute()`.
#### Key Methods:
#### `start(): void`
- Purpose: Initiates the DOM mutation observer to monitor for changes and trigger translations. This method should be called to enable dynamic content translation.
- Parameters: None
- Returns: (void)
#### `addIgnore(node: HTMLElement | string, expireTime: number, showResultText: string): void`
- Purpose: Adds a node to the ignore list for a specified duration, preventing the listener from re-translating it immediately after a programmatic change.
- Parameters:
    - `node (HTMLElement | string)`: The DOM node or its UUID to ignore.
    - `expireTime (number)`: The duration in milliseconds for which to ignore the node.
    - `showResultText (string)`: The text that the node currently displays (used for verification).
- Returns: (void)
#### `refreshIgnoreNode(): void`
- Purpose: Cleans up the `ignoreNode` list by removing expired entries.
- Parameters: None
- Returns: (void)
#### `addListener(): void`
- Purpose: (Internal) Configures and starts the `MutationObserver`. Called by `start()`.
- Parameters: None
- Returns: (void)

### `translate.renderTask` (Class)
- Description: Manages the queue of translation rendering tasks, applying translated text back to the DOM.
- Responsibilities: Collects translation replacements, sorts them to avoid conflicts, and executes the DOM updates.

#### Key Methods:
#### `add(node: HTMLElement, originalText: string, resultText: string, attribute?: string): void`
- Purpose: Adds a translation replacement task to the queue.
- Parameters:
    - `node (HTMLElement)`: The DOM element to be updated.
    - `originalText (string)`: The original text that was translated.
    - `resultText (string)`: The translated text.
    - `attribute (string | undefined)`: Optional. The attribute to update (e.g., 'title'), if not the `nodeValue`.
- Returns: (void)
#### `execute(): void`
- Purpose: Processes the queue of translation tasks, performing the actual DOM updates. It handles text replacement, attribute updates, and interaction with the `ignoreNode` list.
- Parameters: None
- Returns: (void)

## Dependencies
### Internal Dependencies
- `nodeuuid` (utility for generating unique IDs for DOM nodes, likely internal to `translate.js` as no explicit import is shown in `index.js`).
- `msg` (a lightweight JS message/popup utility, used for `office.export`, suggesting it's either bundled or expected to be available globally).

### External Dependencies
- **Browser DOM APIs**: Fundamental for interacting with the web page structure and content.
- **`MutationObserver`**: A browser API used by `translate.listener` for efficiently monitoring DOM changes.
- **External Translation API (configurable)**: The library connects to a backend translation service (e.g., `api.translate.zvo.cn` by default, but configurable for private deployment) to perform the actual translation of text.
- **`IndexedDB`**: Used by `translate.office.fullExtract` for client-side storage of translation data.

## Integration Points
### Public APIs
- The entire `translate` global object, with all its public properties and methods, serves as the main integration point.
- Example: `translate.execute()`, `translate.changeLanguage('english')`, `translate.selectLanguageTag.show = false`.

### Data Flow
1.  **Initialization**: The script is loaded, and `translate.execute()` is called.
2.  **DOM Scanning**: The library traverses the DOM (either the entire page or specified `documents`) to identify text nodes and attributes for translation. Ignored elements are skipped.
3.  **Language Detection/Selection**: Determines the target translation language based on user settings (`translate.to`), browser locale (if `autoDiscriminateLocalLanguage` is enabled), or a selection from the UI (`translate.selectLanguageTag`).
4.  **Caching & Nomenclature**: Checks internal caches (e.g., `localStorage`, `IndexedDB` for full extract) and custom nomenclature (`translate.nomenclature`) for existing translations.
5.  **API Requests**: For text not found in caches or nomenclature, batches API requests to the configured translation service.
6.  **Translation Rendering**: Upon receiving API responses (or hitting cache), `translate.renderTask` updates the DOM by replacing original text with translated text.
7.  **Dynamic Content**: `translate.listener` continuously monitors for new DOM content (e.g., from AJAX updates, framework rendering) and triggers translation for these new elements.

### Event Handling or Callbacks
- `translate.listener.execute.renderStartByApi`: Triggered before sending an API request for translation.
- `translate.listener.execute.renderFinishByApi`: Triggered after an API response is received and rendered.
- `translate.lifecycle.execute.renderFinish`: Triggered after all translation rendering tasks (including cached translations) are completed for an `execute()` call.

### Extension Points for Customization
- `translate.selectLanguageTag.customUI`: Allows developers to fully customize the language selection UI.
- `translate.nomenclature.append`: For adding custom translation pairs.
- `translate.ignore` properties: For defining elements to ignore.
- `translate.refreshCurrentPage`: Can be overridden for custom page refresh logic (e.g., in hybrid apps).
- `translate.storage.rewrite`: (Implied by README, likely a method to redefine storage mechanism).

## Implementation Notes
### Design Patterns
- **Module Pattern**: The entire library is encapsulated within a single global `translate` object, exposing a public API while keeping internal details private.
- **Observer Pattern**: `translate.listener` implements this pattern using `MutationObserver` to react to DOM changes.
- **Strategy Pattern**: The translation service (`translate.service.use`) and storage mechanisms (`translate.storage`) appear to allow for different implementations to be swapped in.

### Technical Decisions
- **Version Evolution**: The library has evolved from a Google Translate wrapper (v1, now deprecated) to a more robust, self-contained solution (v2/v3) with improved performance and flexibility.
- **Performance Optimization**: Employs multiple layers of caching (browser cache, `IndexedDB`), preloading mechanisms, and batching of API requests for fast translation.
- **SEO Friendliness**: By default, it doesn't alter the source HTML for crawlers. An advanced TCDN feature allows for server-side translation and separate domain binding for SEO indexing of translated versions.
- **Dynamic Content Handling**: Uses `MutationObserver` to efficiently detect and translate content rendered asynchronously (e.g., by modern JavaScript frameworks like Vue, React).
- **Error Handling**: Includes checks for duplicate loading, file protocol warnings, and error logging for API requests.

### Considerations
- **Performance**: While optimized, excessive DOM manipulation or very large pages can still impact performance, especially with dynamic content. The `translate.listener.ignoreNode` mechanism helps mitigate this.
- **Security**: The library offers private deployment options for sensitive environments, addressing concerns about data privacy. The `tcdn` feature also provides an isolated server-side solution.
- **Limitations**:
    - The `index.js` file is large and contains many comments, which could impact initial load time if not minified/bundled.
    - Some older features are deprecated (e.g., v1 Google Translate, `includedLanguages`, `resourcesUrl`).
    - Direct DOM manipulation by `translate.renderTask` could potentially conflict with other scripts that extensively modify the DOM if not carefully managed (though `ignoreNode` helps).
    - The hardcoded limit of 500 elements for `execute(docs)` suggests potential performance concerns with very large `docs` arrays.