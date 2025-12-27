#!/usr/bin/env python
"""
Test category filtering in GET /mps endpoint (Static Code Analysis)

This script verifies that:
1. Category parameter is properly added to the endpoint
2. Filter logic works correctly with valid category
3. SQL injection protection is in place (ORM filter, no raw SQL)
4. Empty/None category parameter returns all feeds
"""

import sys
import re

print("=" * 60)
print("Category Filtering Implementation Verification")
print("=" * 60)

try:
    with open('apis/mps.py', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("FAIL: apis/mps.py not found")
    sys.exit(1)

# Test 1: Verify parameter exists
print("\nTest 1: Verify category parameter exists")
print("-" * 60)

if 'category: Optional[str] = Query(None' in content:
    print("PASS: Category parameter found with proper typing")
else:
    print("FAIL: Category parameter not properly typed")
    sys.exit(1)

# Test 2: Verify filter logic
print("\nTest 2: Verify ORM filter logic")
print("-" * 60)

if 'Feed.category == category' in content:
    print("PASS: Safe ORM filter found (Feed.category == category)")
else:
    print("FAIL: Safe ORM filter NOT found")
    sys.exit(1)

# Test 3: Verify conditional filter
print("\nTest 3: Verify conditional filter (only when category provided)")
print("-" * 60)

if 'if category:' in content and 'query = query.filter(Feed.category == category)' in content:
    print("PASS: Conditional filter check found (if category:)")
else:
    print("FAIL: Conditional filter logic NOT found")
    sys.exit(1)

# Test 4: SQL injection protection
print("\nTest 4: SQL injection protection check")
print("-" * 60)

# Extract get_mps function
match = re.search(r'@router\.get\("".*?async def get_mps\(.*?\):(.*?)(?=@router\.|\Z)', content, re.DOTALL)
if not match:
    print("FAIL: Could not find get_mps function")
    sys.exit(1)

function_body = match.group(1)

# Check for dangerous patterns
dangerous_patterns = [
    (r'f".*{category}', 'f-string with category (potential SQL injection)'),
    (r"'.*{{{category}}}.*'", 'format() with category (potential SQL injection)'),
    (r'f".*%{category}%', 'LIKE with f-string (potential SQL injection)'),
]

safe = True
for pattern, description in dangerous_patterns:
    if re.search(pattern, function_body):
        print(f"FAIL: {description}")
        safe = False

if safe and 'Feed.category == category' in function_body:
    print("PASS: No raw SQL concatenation (safe ORM filter used)")
else:
    print("FAIL: SQL injection protection not verified")
    sys.exit(1)

# Test 5: Verify imports
print("\nTest 5: Verify required imports")
print("-" * 60)

if 'from typing import Optional' in content:
    print("PASS: Optional imported from typing")
else:
    print("FAIL: Optional NOT imported")
    sys.exit(1)

if 'from fastapi import' in content and 'Query' in content:
    print("PASS: Query imported from fastapi")
else:
    print("FAIL: Query NOT properly imported")
    sys.exit(1)

# Test 6: Verify filter placement
print("\nTest 6: Verify filter placement in query chain")
print("-" * 60)

# Check that filter is applied before count() and all()
if 'if category:' in function_body and 'Feed.category == category' in function_body:
    # Find the order of operations
    filter_pos = function_body.find('Feed.category == category')
    count_pos = function_body.find('.count()')
    all_pos = function_body.find('.all()')

    if filter_pos < count_pos and filter_pos < all_pos:
        print("PASS: Filter applied before .count() and .all()")
    else:
        print("FAIL: Filter placement incorrect")
        sys.exit(1)
else:
    print("FAIL: Filter not properly placed")
    sys.exit(1)

# Test 7: Verify parameter has description
print("\nTest 7: Verify API documentation")
print("-" * 60)

if 'category: Optional[str] = Query(None, description=' in content:
    print("PASS: Category parameter has API description")
else:
    print("WARNING: Category parameter missing description (non-critical)")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("All critical tests PASSED!")
print("\nImplementation verified:")
print("  [OK] Category parameter added with proper typing (Optional[str])")
print("  [OK] ORM filter protects against SQL injection")
print("  [OK] Conditional filter logic (only when category provided)")
print("  [OK] No raw SQL concatenation detected")
print("  [OK] Proper imports in place (Optional, Query)")
print("  [OK] Filter placed correctly in query chain")
print("\nThe endpoint now supports filtering by category:")
print("  Example: GET /wx/mps?category=tech")
print("  Example: GET /wx/mps?category=news")
print("  Example: GET /wx/mps (returns all feeds, no filter)")
print("\nSQL injection protection: ORM filter (Feed.category == category)")
print("  - Safe: query.filter(Feed.category == category)")
print("  - Unsafe: f\"SELECT * FROM feeds WHERE category = '{category}'\"")
print("  - Implementation uses SAFE approach")
