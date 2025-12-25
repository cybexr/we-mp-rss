 
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from core.log import logger

def preprocess_image_attributes(html_content):
    """
    Comprehensive image attribute preprocessing utility to standardize handling of
    data-src, src, and other lazy-loading attributes across all content formats.

    This function implements priority logic for resolving conflicting attributes
    and handles common lazy-loading patterns used by various websites and CMS systems.

    Priority Logic:
    1. data-src (highest priority - most common lazy-loading attribute)
    2. data-original (second priority - used by many plugins)
    3. data-lazy (third priority - common lazy loading variant)
    4. srcset (extract first URL from responsive image sets)
    5. src (fallback - standard image source)

    Args:
        html_content (str): HTML content to process

    Returns:
        str: HTML content with standardized image src attributes

    Raises:
        Exception: Returns original HTML content if processing fails
    """
    try:
        if not html_content:
            return html_content

        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')

        processed_count = 0

        for img_tag in img_tags:
            try:
                # Collect all potential image sources with their priorities
                image_sources = {}

                # Priority 1: data-src (most common lazy-loading attribute)
                if 'data-src' in img_tag.attrs:
                    data_src = img_tag['data-src']
                    if data_src and data_src.strip() and not data_src.startswith('data:image'):
                        if _is_valid_url(data_src):
                            image_sources['data-src'] = (data_src, 1)

                # Priority 2: data-original (used by many lazy loading plugins)
                if 'data-original' in img_tag.attrs:
                    data_original = img_tag['data-original']
                    if data_original and data_original.strip() and not data_original.startswith('data:image'):
                        if _is_valid_url(data_original):
                            image_sources['data-original'] = (data_original, 2)

                # Priority 3: data-lazy (common lazy loading variant)
                if 'data-lazy' in img_tag.attrs:
                    data_lazy = img_tag['data-lazy']
                    if data_lazy and data_lazy.strip() and not data_lazy.startswith('data:image'):
                        if _is_valid_url(data_lazy):
                            image_sources['data-lazy'] = (data_lazy, 3)

                # Priority 4: data-lazy-src (another common variant)
                if 'data-lazy-src' in img_tag.attrs:
                    data_lazy_src = img_tag['data-lazy-src']
                    if data_lazy_src and data_lazy_src.strip() and not data_lazy_src.startswith('data:image'):
                        if _is_valid_url(data_lazy_src):
                            image_sources['data-lazy-src'] = (data_lazy_src, 4)

                # Priority 5: data-lazy-srcset (lazy responsive images - extract first URL)
                if 'data-lazy-srcset' in img_tag.attrs:
                    data_lazy_srcset = img_tag['data-lazy-srcset']
                    if data_lazy_srcset and data_lazy_srcset.strip():
                        first_url = _extract_first_url_from_srcset(data_lazy_srcset)
                        if first_url and _is_valid_url(first_url):
                            image_sources['data-lazy-srcset'] = (first_url, 5)

                # Priority 6: srcset (responsive images - extract first URL)
                if 'srcset' in img_tag.attrs:
                    srcset = img_tag['srcset']
                    if srcset and srcset.strip():
                        first_url = _extract_first_url_from_srcset(srcset)
                        if first_url and _is_valid_url(first_url):
                            image_sources['srcset'] = (first_url, 6)

                # Priority 7: src (standard src attribute - lowest priority for replacement)
                if 'src' in img_tag.attrs:
                    src = img_tag['src']
                    if src and src.strip():
                        # Don't prioritize placeholder images
                        if not src.startswith('data:image') and not _is_placeholder_url(src):
                            if _is_valid_url(src):
                                image_sources['src'] = (src, 7)

                # Choose the best source based on priority
                if image_sources:
                    # Sort by priority number (lower is higher priority)
                    best_source = min(image_sources.items(), key=lambda x: x[1][1])
                    chosen_url = best_source[1][0]

                    # Set the src attribute to the chosen URL
                    img_tag['src'] = chosen_url

                    # Clean up lazy-loading attributes to prevent conflicts
                    attributes_to_remove = [
                        'data-src', 'data-original', 'data-lazy', 'data-lazy-src',
                        'data-lazy-srcset', 'data-srcset', 'data-sizes', 'loading', 'data-loading', 'srcset'
                    ]

                    for attr in attributes_to_remove:
                        if attr in img_tag.attrs:
                            del img_tag[attr]

                    processed_count += 1
                    logger.debug(f'Processed image: {chosen_url[:100]}...')
                else:
                    # No valid source found, remove invalid src if it's a placeholder
                    if 'src' in img_tag.attrs:
                        src = img_tag['src']
                        if src.startswith('data:image') or _is_placeholder_url(src):
                            del img_tag['src']
                            logger.debug('Removed placeholder image src')

            except Exception as e:
                # Error processing individual image - log and continue
                logger.warning(f'Error processing individual image tag: {e}')
                continue

        if processed_count > 0:
            logger.info(f'Successfully preprocessed {processed_count} image attributes')

        return str(soup)

    except Exception as e:
        logger.error(f'preprocess_image_attributes error: {e}')
        # Return original content if conversion fails
        return html_content

def _is_valid_url(url):
    """
    Validate if a URL is properly formatted and accessible.

    Args:
        url (str): URL to validate

    Returns:
        bool: True if URL appears valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    try:
        # Basic URL validation using urlparse
        parsed = urlparse(url)
        # Check if it has a scheme and netloc (for absolute URLs) or just path (for relative URLs)
        return bool(parsed.scheme or parsed.path)
    except Exception:
        return False

def _is_placeholder_url(url):
    """
    Check if URL is likely a placeholder image.

    Args:
        url (str): URL to check

    Returns:
        bool: True if URL appears to be a placeholder
    """
    if not url:
        return False

    placeholder_patterns = [
        'placeholder', 'spacer', 'blank', 'empty', 'pixel',
        '1x1', 'transparent.gif', 'empty.png', 'no-image',
        'loading.gif', 'spinner', 'lazy-load'
    ]

    url_lower = url.lower()
    return any(pattern in url_lower for pattern in placeholder_patterns)

def _extract_first_url_from_srcset(srcset):
    """
    Extract the first valid URL from a srcset attribute.

    Args:
        srcset (str): srcset attribute value

    Returns:
        str: First URL found, or None if no valid URL
    """
    if not srcset:
        return None

    try:
        # srcset format: "url1 1x, url2 2x, url3 100w"
        # Split by comma and take first entry
        entries = [entry.strip() for entry in srcset.split(',')]
        if not entries:
            return None

        # First entry: extract URL before any space
        first_entry = entries[0]
        url_part = first_entry.split()[0] if ' ' in first_entry else first_entry

        return url_part if url_part else None

    except Exception:
        return None

def convert_data_src_to_src(html_content):
    """
    Convert data-src attributes to src attributes in HTML content.
    This fixes images that have data-src with actual image URLs but src with placeholder data.

    Args:
        html_content (str): HTML content to process

    Returns:
        str: HTML content with data-src attributes converted to src
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')

        for img_tag in img_tags:
            # Prefer data-src over src if both exist
            if 'data-src' in img_tag.attrs:
                data_src = img_tag['data-src']
                # Only convert if data-src has a valid URL (not empty or placeholder)
                if data_src and data_src.strip() and not data_src.startswith('data:image'):
                    img_tag['src'] = data_src
                    # Remove the data-src attribute after conversion
                    del img_tag['data-src']
                elif 'src' in img_tag.attrs and img_tag['src'].startswith('data:image'):
                    # If data-src is empty/invalid but src has placeholder, remove src entirely
                    # to avoid showing placeholder images
                    del img_tag['src']

        return str(soup)
    except Exception as e:
        logger.error('convert_data_src_to_src error: %s', e)
        # Return original content if conversion fails
        return html_content

def format_content(content:str,content_format:str='html'):
    #格式化内容
    # content_format: 'text' or 'markdown' or 'html'
    # content: str
    # return: str
    try:
        # Apply comprehensive image preprocessing universally for all formats
        # This ensures images display correctly in all output formats by handling
        # data-src, data-original, srcset, and other lazy-loading attributes
        content = preprocess_image_attributes(content)

        if content_format == 'text':
            # 去除HTML标签，保留纯文本
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text().strip()
            content = re.sub(r'\n\s*\n', '\n', text)
        elif content_format == 'markdown':
            # 去除span和font标签，只保留内容
            soup = BeautifulSoup(content, 'html.parser')
            for tag in soup.find_all(['span', 'font','div','strong','b']):
                tag.unwrap()
            for tag in soup.find_all(True):
                if 'style' in tag.attrs:
                  del tag.attrs['style']
                if 'class' in tag.attrs:
                  del tag.attrs['class']
                if 'data-pm-slice' in tag.attrs:
                  del tag.attrs['data-pm-slice']
                if 'data-title' in tag.attrs:
                  # tag.append(tag.attrs['data-title'])
                  del tag.attrs['data-title']
            
                    
            content = str(soup)
            # 替换 p 标签中的换行符为空
            content = re.sub(r'(<p[^>]*>)([\s\S]*?)(<\/p>)', lambda m: m.group(1) + re.sub(r'\n', '', m.group(2)) + m.group(3), content)
            content = re.sub(r'\n\s*\n\s*\n+', '\n', content)
            content = re.sub(r'\*', '', content)
            # print(content)
            from markdownify import markdownify as md
            # 处理图片标签，保留title属性
            soup = BeautifulSoup(content, 'html.parser')
            for img in soup.find_all('img'):
                if 'title' in img.attrs:
                    img['alt'] = img['title']
            content = str(soup)
            # 转换HTML到Markdown
            content = md(content, heading_style="ATX", bullets='-*+', code_language='python')
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
            
    except Exception as e:
        logger.error('format_content error: %s',e)
    return content