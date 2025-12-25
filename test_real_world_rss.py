#!/usr/bin/env python3
"""
Real-World RSS Feed Image Validation Test

This test simulates real-world RSS content that might contain various
lazy-loading image patterns found in modern websites.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.rss import RSS
from core.content_format import format_content

def test_real_world_lazy_loading_scenarios():
    """Test real-world lazy loading scenarios from common CMS and websites"""
    print("=== Real-World RSS Feed Lazy Loading Test ===")

    # Scenario 1: WordPress with Jetpack lazy loading
    wordpress_content = """
    <article>
        <h2>WordPress Article with Jetpack Lazy Load</h2>
        <img class="alignnone size-large wp-image-1234"
             src="https://example.com/wp-content/uploads/2023/12/placeholder.jpg"
             data-lazy-src="https://example.com/wp-content/uploads/2023/12/real-image.jpg"
             alt="WordPress lazy load image"
             width="800" height="600">

        <img class="aligncenter size-medium"
             src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20300%20200'%3E%3C/svg%3E"
             data-lazy-srcset="https://example.com/wp-content/uploads/2023/12/image-1.jpg 300w,
                             https://example.com/wp-content/uploads/2023/12/image-2.jpg 600w,
                             https://example.com/wp-content/uploads/2023/12/image-3.jpg 1024w"
             data-sizes="(max-width: 300px) 100vw, 300px"
             alt="Responsive lazy image">

        <p>Article content here...</p>
    </article>
    """

    # Scenario 2: Medium-style article
    medium_content = """
    <div>
        <h3>Medium-style Article Images</h3>
        <figure>
            <img src="https://cdn.example.com/placeholder.gif"
                 data-original="https://cdn.example.com/images/article-main.jpg"
                 alt="Article hero image">
        </figure>

        <p>Some content with inline images:</p>
        <img src="https://miro.medium.com/1x1.gif"
             data-src="https://miro.medium.com/resize/fit/640/format/webp/1*image1.jpg"
             alt="Inline image 1">

        <img src="https://miro.medium.com/1x1.gif"
             data-original="https://miro.medium.com/resize/fit/800/format/webp/1*image2.jpg"
             loading="lazy"
             alt="Inline image 2">
    </div>
    """

    # Scenario 3: E-commerce product page
    ecommerce_content = """
    <div class="product-gallery">
        <img class="product-image-main"
             src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
             data-src="https://cdn.shop.com/products/main-product.jpg"
             alt="Product main image">

        <div class="product-thumbnails">
            <img src="/images/spacer.gif"
                 data-src="https://cdn.shop.com/products/thumb1.jpg"
                 data-lazy="true"
                 alt="Thumbnail 1">

            <img src="/images/loading.gif"
                 data-src="https://cdn.shop.com/products/thumb2.jpg"
                 alt="Thumbnail 2">

            <img srcset="https://cdn.shop.com/products/thumb3-small.jpg 100w,
                        https://cdn.shop.com/products/thumb3-medium.jpg 200w"
                 sizes="100px"
                 src="/images/placeholder.png"
                 alt="Thumbnail 3">
        </div>
    </div>
    """

    # Test scenarios
    scenarios = [
        ("WordPress Jetpack Lazy Load", wordpress_content),
        ("Medium-style Article", medium_content),
        ("E-commerce Product Page", ecommerce_content)
    ]

    results = []

    for scenario_name, content in scenarios:
        print(f"\nTesting: {scenario_name}")
        print("-" * 50)

        # Test content formatting
        formatted_content = format_content(content, 'html')

        # Check for successful conversion
        has_data_src = 'data-src=' in formatted_content
        has_data_original = 'data-original=' in formatted_content
        has_lazy_src = 'data-lazy-src=' in formatted_content
        has_srcset = 'srcset=' in formatted_content
        has_real_images = 'src="https://' in formatted_content

        print(f"Data-src attributes removed: {not has_data_src}")
        print(f"Data-original attributes removed: {not has_data_original}")
        print(f"Lazy-src attributes removed: {not has_lazy_src}")
        print(f"Srcset attributes removed: {not has_srcset}")
        print(f"Real image URLs present: {has_real_images}")

        # Generate RSS feed with this content
        mock_articles = [{
            'id': f'test-{scenario_name.lower().replace(" ", "-")}',
            'title': f'Test: {scenario_name}',
            'description': f'Testing {scenario_name}',
            'link': 'https://example.com/article',
            'image': 'https://example.com/cover.jpg',
            'content': formatted_content,
            'mp_name': 'Test Feed',
            'feed': 'test-feed',
            'updated': datetime.now(timezone.utc)
        }]

        # Mock config for full context
        import core.config
        original_cfg = getattr(core.config, 'cfg', {})
        core.config.cfg = {'rss.full_context': True, 'rss.add_cover': False}

        try:
            # Test RSS format
            rss_generator = RSS(ext="rss")
            rss_content = rss_generator.generate_rss(mock_articles, title="Test RSS Feed")

            # Test Atom format
            atom_generator = RSS(ext="atom")
            atom_content = atom_generator.generate_atom(mock_articles, title="Test Atom Feed")

            # Test JSON format
            json_generator = RSS(ext="json")
            json_content = json_generator.generate_json(mock_articles, title="Test JSON Feed")

            print(f"RSS feed generated successfully: {len(rss_content)} characters")
            print(f"Atom feed generated successfully: {len(atom_content)} characters")
            print(f"JSON feed generated successfully: {len(json_content)} characters")

            # Validate feeds contain proper images
            rss_has_images = 'src="https://' in rss_content
            atom_has_images = 'src="https://' in atom_content

            json_data = json.loads(json_content)
            json_has_images = 'src="https://' in json_data['items'][0]['content']

            print(f"RSS feed contains proper images: {rss_has_images}")
            print(f"Atom feed contains proper images: {atom_has_images}")
            print(f"JSON feed contains proper images: {json_has_images}")

            success = (not has_data_src and not has_data_original and not has_lazy_src and
                      not has_srcset and has_real_images and rss_has_images and atom_has_images and json_has_images)

            results.append({
                'scenario': scenario_name,
                'success': success,
                'rss_images': rss_has_images,
                'atom_images': atom_has_images,
                'json_images': json_has_images
            })

            print(f"Overall result: {'PASS' if success else 'FAIL'}")

        except Exception as e:
            print(f"Error testing scenario: {e}")
            results.append({
                'scenario': scenario_name,
                'success': False,
                'error': str(e)
            })
        finally:
            core.config.cfg = original_cfg

    # Summary
    print("\n" + "=" * 60)
    print("REAL-WORLD RSS FEED TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get('success', False))
    total = len(results)

    print(f"Total Scenarios: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    print("\nDetailed Results:")
    for result in results:
        status = "PASS" if result.get('success', False) else "FAIL"
        print(f"  {status}: {result['scenario']}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
        else:
            print(f"    RSS: {result.get('rss_images', False)}, "
                  f"Atom: {result.get('atom_images', False)}, "
                  f"JSON: {result.get('json_images', False)}")

    print("\nReal-world RSS validation complete!")

if __name__ == "__main__":
    test_real_world_lazy_loading_scenarios()