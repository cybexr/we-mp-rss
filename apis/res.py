from fastapi import APIRouter, Request, HTTPException
import httpx
from fastapi.responses import Response
import os
import hashlib
import time
import json
from core.config import cfg
CACHE_DIR = cfg.get("cache.dir","data/cache")
CACHE_TTL = 3600  # 缓存过期时间1小时

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

router = APIRouter(prefix="/res", tags=["资源反向代理"])
def cache_image_url(url: str, method: str = 'GET') -> bool:
    """
    Cache an image URL to local filesystem.

    Downloads and caches the image from the given URL using the same caching
    logic as the reverse_proxy function. Cached files are stored with SHA256 hash
    filename based on method and URL.

    Args:
        url: The image URL to cache
        method: HTTP method (default: 'GET')

    Returns:
        bool: True if caching succeeded or already cached, False on failure
    """
    try:
        # Normalize URL (replace https with http for consistency)
        url = url.replace("https://", "http://")

        # Generate cache filename
        cache_key = f"{method}_{url}".encode('utf-8')
        cache_filename = os.path.join(CACHE_DIR, hashlib.sha256(cache_key).hexdigest())

        # Check if cache already exists and is valid
        if os.path.exists(cache_filename):
            file_mtime = os.path.getmtime(cache_filename)
            if time.time() - file_mtime < CACHE_TTL:
                # Already cached and valid
                return True

        # Download image using synchronous httpx client
        client = httpx.Client()
        resp = client.request(method=method, url=url, timeout=30.0)

        if resp.status_code != 200:
            print(f"Failed to cache image {url}: HTTP {resp.status_code}")
            return False

        content = resp.content
        headers = dict(resp.headers)

        # Cache response content
        with open(cache_filename, 'wb') as f:
            f.write(content)

        # Cache response headers
        headers_filename = cache_filename + ".headers"
        with open(headers_filename, 'w', encoding='utf-8') as f:
            json.dump(headers, f)

        print(f"Successfully cached image: {url}")
        return True

    except Exception as e:
        print(f"Error caching image {url}: {str(e)}")
        return False


@router.api_route("/logo/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], operation_id="reverse_proxy_logo")
async def reverse_proxy(request: Request, path: str):
    hosts=["mmbiz.qpic.cn","mmbiz.qlogo.cn","mmecoa.qpic.cn"]
    path=path.replace("https://", "http://")
    from urllib.parse import urlparse
    parsed_url = urlparse(path)
    host = parsed_url.netloc
    if  host not  in hosts:
        return Response(
        content="只允许访问微信公众号图标，请使用正确的域名。",
        status_code=301,
        headers={"Location":path},
    )
    
    # 生成缓存文件名
    cache_key = f"{request.method}_{path}".encode('utf-8')
    cache_filename = os.path.join(CACHE_DIR, hashlib.sha256(cache_key).hexdigest())
    
    # 检查缓存是否存在且有效
    if os.path.exists(cache_filename):
        file_mtime = os.path.getmtime(cache_filename)
        if time.time() - file_mtime < CACHE_TTL:
            with open(cache_filename, 'rb') as f:
                content = f.read()
            
            # 读取缓存的状态码和响应头
            headers_filename = cache_filename + ".headers"
            if os.path.exists(headers_filename):
                with open(headers_filename, 'r', encoding='utf-8') as f:
                    headers = json.load(f)
            else:
                headers = {}
            
            media_type = headers.get("Content-Type")
            status_code = 200  # 默认状态码
            
            return Response(
                content=content,
                status_code=status_code,
                headers=headers,
                media_type=media_type
            )
    
    target_url = path
    
    client = httpx.AsyncClient()
    request_data = await request.body()
    headers = dict(request.headers)
    headers.pop("host", host)
    headers.pop("referer", None)
    print(headers)
    resp = await client.request(
        method=request.method,
        url=target_url,
        # headers=headers,
        content=request_data
    )
    
    content = resp.content
    status_code = resp.status_code
    headers = dict(resp.headers)
    media_type = resp.headers.get("Content-Type")
    try:
        # 缓存响应
        with open(cache_filename, 'wb') as f:
            f.write(content)
        
        # 缓存响应头
        headers_filename = cache_filename + ".headers"
        with open(headers_filename, 'w', encoding='utf-8') as f:
            json.dump(headers, f)
    except Exception as e:
        print(f"缓存响应失败: {str(e)}")    
    return Response(
        content=content,
        status_code=status_code,
        headers=headers,
        media_type=media_type
    )