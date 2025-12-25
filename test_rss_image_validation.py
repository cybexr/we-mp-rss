#!/usr/bin/env python3
"""
RSS Image Conversion Validation Test Suite

This test validates that RSS feeds properly convert data-src and other lazy-loading
attributes to src attributes across all output formats (RSS, Atom, JSON).
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.rss import RSS
from core.content_format import format_content

class TestImageValidation:
    """Test image conversion in RSS feed generation"""

    def __init__(self):
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")

    def create_test_data_with_lazy_images(self):
        """Create test article data with various lazy-loading image scenarios"""

        # Test case 1: data-src with placeholder src
        content_1 = """
        <article>
            <h1>Article with data-src images</h1>
            <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                 data-src="https://example.com/image1.jpg" alt="Test image 1">
            <p>Some content here</p>
            <img src="https://example.com/placeholder.gif"
                 data-original="https://example.com/image2.jpg" alt="Test image 2">
        </article>
        """

        # Test case 2: srcset responsive images
        content_2 = """
        <article>
            <h1>Article with srcset images</h1>
            <img srcset="https://example.com/image3-small.jpg 1x,
                              https://example.com/image3-large.jpg 2x"
                 src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                 alt="Responsive image">
            <img data-lazy="https://example.com/image4.jpg"
                 src="https://example.com/spacer.gif" alt="Lazy loaded image">
        </article>
        """

        # Test case 3: Mixed lazy-loading attributes
        content_3 = """
        <article>
            <h1>Article with mixed lazy attributes</h1>
            <img data-src="https://example.com/image5.jpg"
                 data-original="https://example.com/image5-original.jpg"
                 src="https://example.com/loading.gif"
                 alt="Multiple data attributes">
            <img data-lazy-src="https://example.com/image6.jpg"
                 data-srcset="https://example.com/image6-1x.jpg 1x, https://example.com/image6-2x.jpg 2x"
                 loading="lazy"
                 src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%201%201'%3E%3C/svg%3E"
                 alt="Advanced lazy loading">
        </article>
        """

        # Test case 4: Normal images (no conversion needed)
        content_4 = """
        <article>
            <h1>Article with normal images</h1>
            <img src="https://example.com/normal-image.jpg" alt="Normal image">
            <img src="/relative/path/image.jpg" alt="Relative path image">
        </article>
        """

        # Create article data
        articles = [
            {
                "id": "test-1",
                "title": "Test Article 1 - Data-src Images",
                "description": "Test article with data-src lazy loading",
                "link": "https://example.com/article1",
                "image": "https://example.com/cover1.jpg",
                "content": content_1,
                "mp_name": "Test Feed 1",
                "feed": "test-feed-1",
                "updated": datetime.now(timezone.utc)
            },
            {
                "id": "test-2",
                "title": "Test Article 2 - Srcset Images",
                "description": "Test article with srcset responsive images",
                "link": "https://example.com/article2",
                "image": "https://example.com/cover2.jpg",
                "content": content_2,
                "mp_name": "Test Feed 2",
                "feed": "test-feed-2",
                "updated": datetime.now(timezone.utc)
            },
            {
                "id": "test-3",
                "title": "Test Article 3 - Mixed Lazy Attributes",
                "description": "Test article with various lazy-loading attributes",
                "link": "https://example.com/article3",
                "image": "https://example.com/cover3.jpg",
                "content": content_3,
                "mp_name": "Test Feed 3",
                "feed": "test-feed-3",
                "updated": datetime.now(timezone.utc)
            },
            {
                "id": "test-4",
                "title": "Test Article 4 - Normal Images",
                "description": "Test article with normal images (no lazy loading)",
                "link": "https://example.com/article4",
                "image": "https://example.com/cover4.jpg",
                "content": content_4,
                "mp_name": "Test Feed 4",
                "feed": "test-feed-4",
                "updated": datetime.now(timezone.utc)
            }
        ]

        return articles

    def test_format_content_image_conversion(self):
        """Test format_content function directly"""
        print("\n=== Testing format_content Image Conversion ===")

        test_content = """
        <div>
            <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                 data-src="https://example.com/real-image.jpg" alt="Test image">
            <img data-original="https://example.com/another-image.jpg"
                 src="https://example.com/placeholder.gif" alt="Another test">
            <img srcset="https://example.com/srcset-image.jpg 1x, https://example.com/srcset-large.jpg 2x"
                 src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%201%201'%3E%3C/svg%3E"
                 alt="Srcset test">
        </div>
        """

        # Test HTML format
        html_result = format_content(test_content, 'html')

        # Verify data-src conversion
        has_data_src = 'data-src=' in html_result
        has_real_image_src = 'src="https://example.com/real-image.jpg"' in html_result

        self.log_test(
            "HTML format - data-src conversion",
            not has_data_src and has_real_image_src,
            f"data-src removed: {not has_data_src}, real image src added: {has_real_image_src}"
        )

        # Verify data-original conversion
        has_data_original = 'data-original=' in html_result
        has_another_image_src = 'src="https://example.com/another-image.jpg"' in html_result

        self.log_test(
            "HTML format - data-original conversion",
            not has_data_original and has_another_image_src,
            f"data-original removed: {not has_data_original}, converted to src: {has_another_image_src}"
        )

        # Verify srcset conversion
        has_srcset = 'srcset=' in html_result
        has_srcset_image_src = 'src="https://example.com/srcset-image.jpg"' in html_result

        self.log_test(
            "HTML format - srcset conversion",
            not has_srcset and has_srcset_image_src,
            f"srcset removed: {not has_srcset}, first srcset URL used as src: {has_srcset_image_src}"
        )

        # Test other formats (markdown, text)
        markdown_result = format_content(test_content, 'markdown')
        text_result = format_content(test_content, 'text')

        # For markdown and text, we expect different handling
        # Markdown should preserve some HTML structure
        has_md_img = '![' in markdown_result
        self.log_test(
            "Markdown format image handling",
            has_md_img,
            f"Markdown images present: {has_md_img}"
        )

        # Text should remove images entirely
        has_text_img = '<img' in text_result or 'http' in text_result
        self.log_test(
            "Text format image removal",
            not has_text_img,
            f"Images removed from text: {not has_text_img}"
        )

    def test_rss_format_image_conversion(self):
        """Test RSS XML format image conversion"""
        print("\n=== Testing RSS Format Image Conversion ===")

        articles = self.create_test_data_with_lazy_images()
        rss_generator = RSS(ext="rss")

        try:
            # Mock the config to enable full context
            import core.config
            original_cfg = getattr(core.config, 'cfg', {})

            # Create mock config with full context enabled
            mock_cfg = {
                "rss.full_context": True,
                "rss.add_cover": False
            }
            core.config.cfg = mock_cfg

            # Generate RSS content
            rss_content = rss_generator.generate_rss(
                articles,
                title="Test RSS Feed",
                description="Test feed for image validation"
            )

            # Parse XML to verify structure
            root = ET.fromstring(rss_content)
            channel = root.find('channel')

            # Verify each article's content in RSS
            for article in articles:
                item = None
                for channel_item in channel.findall('item'):
                    if channel_item.find('id').text == article['id']:
                        item = channel_item
                        break

                if item is not None:
                    content_encoded = item.find('content:encoded',
                                               {'content': 'http://purl.org/rss/1.0/modules/content/'})
                    if content_encoded is not None:
                        content_text = content_encoded.text

                        # Debug output for failing tests
                        print(f"DEBUG RSS {article['id']}: content_text = {content_text[:200]}...")

                        # Check for data-src removal
                        has_data_src = 'data-src=' in content_text
                        has_data_original = 'data-original=' in content_text
                        has_lazy_attrs = 'data-lazy' in content_text

                        # Check for proper src attributes
                        has_proper_src = 'src="https://example.com/' in content_text

                        article_id = article['id']
                        self.log_test(
                            f"RSS Article {article_id} - Lazy attributes removed",
                            not has_data_src and not has_data_original and not has_lazy_attrs,
                            f"Removed lazy attributes: data-src={has_data_src}, data-original={has_data_original}, data-lazy={has_lazy_attrs}"
                        )

                        self.log_test(
                            f"RSS Article {article_id} - Proper src attributes",
                            has_proper_src,
                            f"Added proper src attributes: {has_proper_src}"
                        )

        except Exception as e:
            self.log_test("RSS Format Generation", False, f"Error: {e}")
        finally:
            # Restore original config
            import core.config
            if 'original_cfg' in locals():
                core.config.cfg = original_cfg

    def test_atom_format_image_conversion(self):
        """Test Atom XML format image conversion"""
        print("\n=== Testing Atom Format Image Conversion ===")

        articles = self.create_test_data_with_lazy_images()
        rss_generator = RSS(ext="atom")

        try:
            # Mock the config to enable full context
            import core.config
            original_cfg = getattr(core.config, 'cfg', {})

            # Create mock config with full context enabled
            mock_cfg = {
                "rss.full_context": True,
                "rss.add_cover": False
            }
            core.config.cfg = mock_cfg

            # Generate Atom content
            atom_content = rss_generator.generate_atom(
                articles,
                title="Test Atom Feed",
                description="Test feed for image validation"
            )

            # Parse XML to verify structure
            root = ET.fromstring(atom_content)

            # Verify each article's content in Atom
            for article in articles:
                entry = None
                for feed_entry in root.findall('entry'):
                    if feed_entry.find('id').text == article['id']:
                        entry = feed_entry
                        break

                if entry is not None:
                    content_elem = entry.find('content')
                    if content_elem is not None:
                        content_text = content_elem.text

                        # Check for data-src removal
                        has_data_src = 'data-src=' in content_text
                        has_data_original = 'data-original=' in content_text

                        # Check for proper src attributes
                        has_proper_src = 'src="https://example.com/' in content_text

                        article_id = article['id']
                        self.log_test(
                            f"Atom Article {article_id} - Lazy attributes removed",
                            not has_data_src and not has_data_original,
                            f"Removed lazy attributes from {article_id}"
                        )

                        self.log_test(
                            f"Atom Article {article_id} - Proper src attributes",
                            has_proper_src,
                            f"Added proper src attributes to {article_id}"
                        )

        except Exception as e:
            self.log_test("Atom Format Generation", False, f"Error: {e}")
        finally:
            # Restore original config
            import core.config
            if 'original_cfg' in locals():
                core.config.cfg = original_cfg

    def test_json_format_image_conversion(self):
        """Test JSON format image conversion"""
        print("\n=== Testing JSON Format Image Conversion ===")

        articles = self.create_test_data_with_lazy_images()
        rss_generator = RSS(ext="json")

        try:
            # Generate JSON content
            json_content = rss_generator.generate_json(
                articles,
                title="Test JSON Feed",
                description="Test feed for image validation"
            )

            # Parse JSON to verify structure
            feed_data = json.loads(json_content)

            # Verify each article's content in JSON
            for article in articles:
                # Find matching article in JSON
                article_data = None
                for item in feed_data['items']:
                    if item['id'] == article['id']:
                        article_data = item
                        break

                if article_data is not None:
                    content_text = article_data['content']

                    # Check for data-src removal
                    has_data_src = 'data-src=' in content_text
                    has_data_original = 'data-original=' in content_text
                    has_lazy_attrs = 'data-lazy' in content_text

                    # Check for proper src attributes
                    has_proper_src = 'src="https://example.com/' in content_text

                    article_id = article['id']
                    self.log_test(
                        f"JSON Article {article_id} - Lazy attributes removed",
                        not has_data_src and not has_data_original and not has_lazy_attrs,
                        f"Removed lazy attributes from {article_id}"
                    )

                    self.log_test(
                        f"JSON Article {article_id} - Proper src attributes",
                        has_proper_src,
                        f"Added proper src attributes to {article_id}"
                    )

        except Exception as e:
            self.log_test("JSON Format Generation", False, f"Error: {e}")

    def test_relative_url_handling(self):
        """Test relative URL preservation in image conversion"""
        print("\n=== Testing Relative URL Handling ===")

        # Test case 1: Images with both src and data-src (data-src should take priority)
        test_content_priority = """
        <div>
            <img src="/images/relative.jpg" data-src="/images/lazy-relative.jpg" alt="Relative path">
            <img src="images/no-leading-slash.jpg" data-src="images/lazy-no-leading.jpg" alt="No leading slash">
            <img src="../parent/image.jpg" data-src="../parent/lazy-image.jpg" alt="Parent path">
        </div>
        """

        html_result_priority = format_content(test_content_priority, 'html')

        # Since data-src has higher priority, those URLs should be used as src
        has_lazy_relative_converted = '/images/lazy-relative.jpg' in html_result_priority
        has_no_leading_converted = 'images/lazy-no-leading.jpg' in html_result_priority
        has_parent_converted = '../parent/lazy-image.jpg' in html_result_priority

        self.log_test(
            "Relative URL priority handling - data-src over src",
            has_lazy_relative_converted and has_no_leading_converted and has_parent_converted,
            f"Data-src URLs prioritized: leading={has_lazy_relative_converted}, no leading={has_no_leading_converted}, parent={has_parent_converted}"
        )

        # Test case 2: Images with only src (should be preserved)
        test_content_normal = """
        <div>
            <img src="/images/normal-relative.jpg" alt="Normal relative">
            <img src="images/normal-no-leading.jpg" alt="Normal no leading">
            <img src="../parent/normal-parent.jpg" alt="Normal parent">
        </div>
        """

        html_result_normal = format_content(test_content_normal, 'html')

        # Normal relative URLs should be preserved
        has_normal_relative = '/images/normal-relative.jpg' in html_result_normal
        has_normal_no_leading = 'images/normal-no-leading.jpg' in html_result_normal
        has_normal_parent = '../parent/normal-parent.jpg' in html_result_normal

        self.log_test(
            "Relative URL preservation - src only images",
            has_normal_relative and has_normal_no_leading and has_normal_parent,
            f"Normal relative URLs preserved: leading={has_normal_relative}, no leading={has_normal_no_leading}, parent={has_normal_parent}"
        )

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Testing Edge Cases ===")

        # Test empty content
        empty_result = format_content("", 'html')
        self.log_test("Empty content handling", empty_result == "",
                     f"Empty content returned: {empty_result == ''}")

        # Test None content
        none_result = format_content(None, 'html')
        self.log_test("None content handling", none_result is None or none_result == "",
                     f"None content handled gracefully")

        # Test malformed HTML
        malformed = '<img src="test.jpg" data-src="real.jpg"</div>'
        malformed_result = format_content(malformed, 'html')
        self.log_test("Malformed HTML handling", isinstance(malformed_result, str),
                     f"Malformed HTML handled without crashing")

        # Test base64 data images (should be ignored)
        base64_content = '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" data-src="https://example.com/real.jpg">'
        base64_result = format_content(base64_content, 'html')
        has_real_src = 'src="https://example.com/real.jpg"' in base64_result
        self.log_test("Base64 image handling", has_real_src,
                     f"Base64 placeholder replaced with real image: {has_real_src}")

    def run_all_tests(self):
        """Run all image validation tests"""
        print("Starting RSS Image Conversion Validation Tests")
        print("=" * 60)

        self.test_format_content_image_conversion()
        self.test_rss_format_image_conversion()
        self.test_atom_format_image_conversion()
        self.test_json_format_image_conversion()
        self.test_relative_url_handling()
        self.test_edge_cases()

        # Generate summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.test_results if "PASS" in r["status"])
        failed = sum(1 for r in self.test_results if "FAIL" in r["status"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if "FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")

        print("\nImage Conversion Validation Complete!")

if __name__ == "__main__":
    validator = TestImageValidation()
    validator.run_all_tests()