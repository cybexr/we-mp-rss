
import core.wx as wx
import core.db as db
from core.config import DEBUG, cfg
from core.models.article import Article
from core.models.feed import Feed
from bs4 import BeautifulSoup
from apis.res import cache_image_url
from core.print import print_info

DB=db.Db(tag="文章采集API")


def cache_article_images(html_content: str) -> int:
    """
    Extract and cache all image URLs from HTML content.

    Args:
        html_content: HTML content containing img tags

    Returns:
        int: Number of images successfully cached
    """
    if not html_content:
        return 0

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')

        cached_count = 0
        seen_urls = set()  # Avoid duplicate caching

        for img_tag in img_tags:
            # Extract image URL with priority: data-src > data-original > src
            img_url = (
                img_tag.get('data-src') or
                img_tag.get('data-original') or
                img_tag.get('src', '')
            )

            # Skip empty, data URLs, or already cached URLs
            if not img_url or img_url in seen_urls:
                continue

            if img_url.startswith('data:image'):
                continue

            if '/static/res/logo/' in img_url:
                continue  # Already using cached URL

            seen_urls.add(img_url)

            # Cache the image
            if cache_image_url(img_url, 'GET'):
                cached_count += 1

        return cached_count

    except Exception as e:
        print(f"Error caching article images: {str(e)}")
        return 0


def UpdateArticle(art:dict,check_exist=True):
    mps_count=0
    if DEBUG:
        # DB.delete_article(art)
        pass
    if  DB.add_article(art,check_exist=check_exist):
        mps_count=mps_count+1

        # Log successful insertion
        article_id = art.get('id', 'unknown')
        article_title = art.get('title', '(no title)')
        print_info(f'[INSERT] Article inserted: {article_id} - {article_title}')

        # Check if feed has image caching enabled
        try:
            mp_id = art.get('mp_id')
            if mp_id:
                session = db.DB.get_session()
                feed = session.query(Feed).filter_by(id=mp_id).first()

                if feed and feed.cache_images:
                    # Cache images from article content
                    content = art.get('content', '')
                    if content:
                        cached_count = cache_article_images(content)
                        if cached_count > 0:
                            article_id = art.get('id', 'unknown')
                            print_info(f"Cached {cached_count} images for article {article_id}")

                session.close()
        except Exception as e:
            print(f"Error in image caching: {str(e)}")
            # Don't fail article save if caching fails

        return True
    return False
def Update_Over(data=None):
    print("更新完成")
    pass