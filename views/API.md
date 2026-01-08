# API Documentation

This document describes the API endpoints for the `views` module.

## Module: `views`

The `views` module provides a web-based interface for previewing WeChat Official Account articles, tags, and official accounts (MPs). It uses FastAPI for routing and `core.lax.template_parser` for rendering HTML templates.

### Endpoints

---

### Home Page

#### `GET /views/home`

Displays a home page with all tags, supporting pagination.

**Summary**: Home Page - Display all tags

**Parameters**:
- `page` (int, optional): Page number. Default is `1`. Minimum value is `1`.
- `limit` (int, optional): Number of items per page. Default is `12`. Minimum value is `1`, maximum value is `50`.

**Responses**:
- `200 OK`: Returns an HTML response containing the rendered home page.
- `500 Internal Server Error`: Returns an HTML response with an error message if data loading fails.

---

### Article List Page

#### `GET /views/articles`

Displays a list of articles, supporting filters, search, and sorting.

**Summary**: Article List Page

**Parameters**:
- `page` (int, optional): Page number. Default is `1`. Minimum value is `1`.
- `limit` (int, optional): Number of items per page. Default is `5`. Minimum value is `1`, maximum value is `20`.
- `mp_id` (str, optional): Official Account ID for filtering articles.
- `tag_id` (str, optional): Tag ID for filtering articles.
- `keyword` (str, optional): Keyword for searching article titles or content.
- `sort` (str, optional): Sorting criteria. Accepted values: `publish_time`, `created_at`. Default is `publish_time`.
- `order` (str, optional): Sorting order. Accepted values: `asc`, `desc`. Default is `desc`.

**Responses**:
- `200 OK`: Returns an HTML response containing the rendered article list page.
- `500 Internal Server Error`: Returns an HTML response with an error message if data loading fails.

---

### Article Detail Page

#### `GET /views/article/{article_id}`

Displays the full content of a specific article.

**Summary**: Article Detail Page

**Parameters**:
- `article_id` (str, path): The unique identifier of the article.

**Responses**:
- `200 OK`: Returns an HTML response containing the rendered article detail page.
- `404 Not Found`: Returns an HTTPException if the article does not exist.
- `500 Internal Server Error`: Returns an HTML response with an error message if data loading fails.

---

### Official Account List Page

#### `GET /views/mps`

Displays a list of all official accounts (MPs), supporting pagination.

**Summary**: Official Account List Page

**Parameters**:
- `page` (int, optional): Page number. Default is `1`. Minimum value is `1`.
- `limit` (int, optional): Number of items per page. Default is `8`. Minimum value is `1`, maximum value is `20`.

**Responses**:
- `200 OK`: Returns an HTML response containing the rendered official account list page.
- `500 Internal Server Error`: Returns an HTML response with an error message if data loading fails.

---

### Tag List Page

#### `GET /views/tags`

Displays a list of all tags, supporting pagination.

**Summary**: Tag List Page

**Parameters**:
- `page` (int, optional): Page number. Default is `1`. Minimum value is `1`.
- `limit` (int, optional): Number of items per page. Default is `8`. Minimum value is `1`, maximum value is `20`.

**Responses**:
- `200 OK`: Returns an HTML response containing the rendered tag list page.
- `500 Internal Server Error`: Returns an HTML response with an error message if data loading fails.

---

### Tag Detail Page

#### `GET /views/tag/{tag_id}`

Displays details of a specific tag and its associated articles.

**Summary**: Tag Detail Page

**Parameters**:
- `tag_id` (str, path): The unique identifier of the tag.
- `page` (int, optional): Page number for associated articles. Default is `1`. Minimum value is `1`.
- `limit` (int, optional): Number of associated articles per page. Default is `20`. Minimum value is `1`, maximum value is `100`.

**Responses**:
- `200 OK`: Returns an HTML response containing the rendered tag detail page with associated articles.
- `404 Not Found`: Returns an HTTPException if the tag does not exist.
- `500 Internal Server Error`: Returns an HTML response with an error message if data loading fails.
