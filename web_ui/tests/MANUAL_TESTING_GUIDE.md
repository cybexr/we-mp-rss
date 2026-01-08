# Manual Testing Guide for Category Filtering

## Prerequisites
1. Backend server running (`python main.py`)
2. Frontend dev server running (`npm run dev`)
3. Browser with DevTools open (Network tab)
4. Test data in database (various categorized and uncategorized feeds)

---

## Test Scenario Checklist

### Scenario 1: All Categories Display
**Objective:** Verify that "All Categories" shows all feeds including uncategorized ones

**Steps:**
1. Navigate to WeChat MP Management page
2. Observe the Category dropdown (default: "全部分类")
3. Check the displayed feed list

**Expected Results:**
- [ ] Category dropdown shows "全部分类" selected by default
- [ ] Feed list includes feeds WITH categories (e.g., "技术", "新闻")
- [ ] Feed list includes feeds WITHOUT categories (shows "-" in category column)
- [ ] Total count includes all feeds
- [ ] Network request shows `category=undefined` or no category parameter

**Network Verification:**
```
Request URL: /wx/mps?offset=0&limit=10&kw=
Response: Should include feeds with various categories + empty category feeds
```

**Screenshot Evidence:**
- Capture: Full page showing dropdown and feed table
- Capture: Network tab request details
- Capture: Console (should be empty, no errors)

---

### Scenario 2: Blank Category Filter
**Objective:** Verify that "(空白尚未维护)" shows only uncategorized feeds

**Steps:**
1. Click Category dropdown
2. Select "(空白尚未维护)" option
3. Wait for results to load

**Expected Results:**
- [ ] Dropdown shows "(空白尚未维护)" selected
- [ ] Feed list ONLY contains feeds with category="" (empty)
- [ ] Category column shows "-" for all feeds
- [ ] Feeds with categories are NOT displayed
- [ ] Total count matches only uncategorized feeds
- [ ] Network request shows `category=` (empty string)

**Network Verification:**
```
Request URL: /wx/mps?offset=0&limit=10&kw=&category=
Response: Should ONLY include feeds where category=""
```

**SQL Query (Backend Verification):**
```sql
-- Run this query to verify backend logic
SELECT id, mp_name, category, remarks
FROM feeds
WHERE category = '' OR category IS NULL;
-- Result should match frontend display
```

**Screenshot Evidence:**
- Capture: Dropdown with "(空白尚未维护)" selected
- Capture: Table showing only uncategorized feeds
- Capture: Network tab showing category= parameter

---

### Scenario 3: Specific Category Filter
**Objective:** Verify that selecting a specific category shows only that category's feeds

**Steps:**
1. Click Category dropdown
2. Select a specific category (e.g., "技术")
3. Wait for results to load

**Expected Results:**
- [ ] Dropdown shows selected category name
- [ ] Feed list ONLY contains feeds with that exact category
- [ ] All visible feeds have the same category tag
- [ ] Feeds with other categories are NOT displayed
- [ ] Uncategorized feeds are NOT displayed
- [ ] Total count matches only that category's feeds
- [ ] Network request shows `category=技术`

**Network Verification:**
```
Request URL: /wx/mps?offset=0&limit=10&kw=&category=技术
Response: Should ONLY include feeds where category="技术"
```

**SQL Query (Backend Verification):**
```sql
-- Verify backend filtering
SELECT id, mp_name, category, remarks
FROM feeds
WHERE category = '技术';
-- Result should match frontend display
```

**Screenshot Evidence:**
- Capture: Dropdown with category selected
- Capture: Table showing only that category's feeds
- Capture: Network tab showing category parameter

---

### Scenario 4: Combined Filtering (Category + Keyword)
**Objective:** Verify that category and keyword search work together

**Steps:**
1. Select a category (e.g., "技术")
2. Enter a keyword in search box (e.g., "技术")
3. Press Enter or click search button
4. Wait for results to load

**Expected Results:**
- [ ] Both filters are active visually
- [ ] Feed list contains feeds matching BOTH conditions
- [ ] Category matches selected category
- [ ] Name/remarks contain the keyword
- [ ] Total count reflects intersection of both filters
- [ ] Network request shows both `category=` and `kw=` parameters

**Network Verification:**
```
Request URL: /wx/mps?offset=0&limit=10&kw=技术&category=技术
Response: Should include feeds matching BOTH conditions
```

**SQL Query (Backend Verification):**
```sql
-- Verify backend logic combines filters with AND
SELECT id, mp_name, category, remarks
FROM feeds
WHERE category = '技术'
  AND mp_name ILIKE '%技术%';
-- Result should match frontend display
```

**Test Matrix:**
| Category | Keyword | Expected Result |
|----------|---------|-----------------|
| (empty) | (empty) | All feeds |
| 技术 | (empty) | Only 技术 category feeds |
| (empty) | 技术 | All feeds with "技术" in name |
| 技术 | 技术 | Feeds with BOTH category="技术" AND "技术" in name |

**Screenshot Evidence:**
- Capture: Both filters active (dropdown + search box)
- Capture: Filtered results table
- Capture: Network tab with both parameters

---

### Scenario 5: Pagination with Filter
**Objective:** Verify that filters persist across page changes

**Steps:**
1. Select a category (e.g., "技术")
2. Note the total count (assume > 10 for pagination)
3. Click page 2 in pagination
4. Wait for results to load

**Expected Results:**
- [ ] Category dropdown remains selected on "技术"
- [ ] Page indicator shows page 2
- [ ] Feed list shows page 2 of filtered results (different feeds from page 1)
- [ ] All feeds on page 2 still have the same category
- [ ] Network request shows `offset=10` (page 2) with `category=技术`
- [ ] Total count remains the same

**Network Verification:**
```
Page 1 Request: /wx/mps?offset=0&limit=10&kw=&category=技术
Page 2 Request: /wx/mps?offset=10&limit=10&kw=&category=技术
Note: category parameter persists, offset changes
```

**Pagination Math Verification:**
- Page 1: offset = 0, limit = 10
- Page 2: offset = 10, limit = 10
- Page 3: offset = 20, limit = 10
- Formula: offset = (page - 1) * pageSize

**Screenshot Evidence:**
- Capture: Page 1 with category filter
- Capture: Page 2 with same category filter
- Capture: Network tab comparing both requests

---

### Scenario 6: Reset Filters
**Objective:** Verify that reset button clears all filters

**Steps:**
1. Apply a category filter (select "技术")
2. Apply a keyword search (enter "测试")
3. Click the "重置" (Reset) button
4. Wait for results to load

**Expected Results:**
- [ ] Category dropdown resets to "全部分类"
- [ ] Search box clears (empty text)
- [ ] Pagination returns to page 1
- [ ] Feed list shows all feeds (unfiltered)
- [ ] Network request shows `category=undefined` or omitted
- [ ] Network request shows `kw=` (empty)
- [ ] Network request shows `offset=0` (page 1)

**Network Verification:**
```
Before Reset: /wx/mps?offset=0&limit=10&kw=测试&category=技术
After Reset:  /wx/mps?offset=0&limit=10&kw=&category=
```

**Frontend State Verification:**
Open browser DevTools Console and check:
```javascript
// These should be true after reset
selectedCategory.value === ''  // or undefined
searchText.value === ''
pagination.current === 1
```

**Screenshot Evidence:**
- Capture: State before reset (filtered)
- Capture: State after reset (all feeds)
- Capture: Network tab showing reset request

---

## Additional Edge Case Tests

### Edge Case 1: No Matching Results
**Steps:**
1. Select a category with no feeds
2. OR select a category + search keyword with no matches

**Expected Results:**
- [ ] Table shows "No data" or empty state
- [ ] Total count shows 0
- [ ] No console errors
- [ ] Network request returns 200 OK with empty list

**Screenshot Evidence:**
- Capture: Empty table state
- Capture: Network response with empty list

---

### Edge Case 2: Very Long Category Names
**Steps:**
1. Create/update a feed with category > 50 characters
2. View in category dropdown
3. Filter by that category

**Expected Results:**
- [ ] Category name displays fully (or truncated with tooltip)
- [ ] Dropdown remains usable
- [ ] Filtering works correctly
- [ ] Network request encodes long URL properly

**Screenshot Evidence:**
- Capture: Dropdown with long category name
- Capture: Filtering works

---

### Edge Case 3: Special Characters in Categories
**Steps:**
1. Create category with special chars: "Test & Demo", "C++/C#", "数据 Science"
2. Filter by these categories

**Expected Results:**
- [ ] Special characters display correctly
- [ ] URL encoding works (& → %26)
- [ ] Backend queries handle special chars
- [ ] SQL injection protection works

**Network Verification:**
```
Request URL should encode special characters:
/wx/mps?category=Test%20%26%20Demo
```

**Screenshot Evidence:**
- Capture: Categories with special characters
- Capture: Network URL encoding

---

### Edge Case 4: Rapid Filter Changes
**Steps:**
1. Quickly change categories multiple times
2. OR type-search rapidly in keyword field

**Expected Results:**
- [ ] No duplicate API calls (debouncing works)
- [ ] Final result matches final selection
- [ ] No race conditions or UI glitches
- [ ] No console errors about cancelled requests

**Verification:**
- [ ] Network tab shows sequential requests (not parallel)
- [ ] Each request completes before next starts
- [ ] UI updates synchronously with request completion

---

## Browser Compatibility Tests

### Test in Multiple Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (if on Mac)
- [ ] Edge (latest)

**Verification:**
- All scenarios above work in each browser
- No browser-specific console errors
- UI renders correctly

---

## Performance Tests

### Large Dataset Performance
**Test with 100+ feeds:**
1. Measure time to load "All Categories"
2. Measure time to filter by category
3. Measure time to search with keyword

**Expected Performance:**
- Initial load: < 2 seconds
- Filter change: < 500ms
- Search response: < 1 second
- No UI freezing or lag

**Metrics to Collect:**
```
Browser DevTools → Network Tab:
- Waiting (TTFB): Should be < 200ms
- Content Download: Should be < 100ms
- Total Time: Should be < 500ms
```

---

## Mobile/Responsive Tests

### Test on Mobile Viewport
**Steps:**
1. Resize browser to mobile width (< 768px)
2. OR use device emulation in DevTools

**Expected Results:**
- [ ] Category dropdown accessible and usable
- [ ] Filter controls stack properly
- [ ] Mobile list view displays correctly
- [ ] Touch interactions work smoothly

**Screenshot Evidence:**
- Capture: Mobile view with category filter
- Capture: Mobile view with filtered results

---

## Console Error Check

**After Each Scenario:**
1. Open browser DevTools Console tab
2. Verify no errors or warnings

**Expected:**
- [ ] No JavaScript errors
- [ ] No 404 or 5xx network errors
- [ ] No Vue/React warnings
- [ ] Clean console log

**Common Issues to Watch For:**
- `undefined is not a function`
- `Cannot read property of undefined`
- Network 500 errors from backend
- CORS errors (if frontend/backend on different ports)

---

## Accessibility Tests

### Keyboard Navigation
**Steps:**
1. Use Tab key to navigate to category dropdown
2. Use arrow keys to select options
3. Use Enter to confirm selection

**Expected Results:**
- [ ] All controls accessible via keyboard
- [ ] Focus indicators visible
- [ ] Screen reader announces options correctly

**Screenshot Evidence:**
- Capture: Keyboard focus on dropdown
- Capture: ARIA labels in DOM inspector

---

## Final Verification Checklist

### Code Quality
- [ ] No TypeScript errors in console
- [ ] No ESLint warnings
- [ ] Code follows project conventions
- [ ] Comments explain complex logic

### Documentation
- [ ] Code is well-commented
- [ ] API documentation updated
- [ ] User guide exists (if applicable)

### Deployment Readiness
- [ ] All tests pass
- [ ] No console errors
- [ ] Performance acceptable
- [ ] Cross-browser compatible
- [ ] Accessible to keyboard users

---

## Bug Report Template

**If any test fails, document with:**

```markdown
### Bug Report: [Title]

**Scenario:** [Which test scenario]

**Steps to Reproduce:**
1.
2.
3.

**Expected Behavior:** [What should happen]

**Actual Behavior:** [What actually happened]

**Screenshots:** [Attach evidence]

**Console Errors:** [Paste errors]

**Network Requests:** [Copy request/response]

**Browser:** [Chrome/Firefox/etc + version]

**Environment:** [Dev/Staging/Production]
```

---

## Test Sign-Off

**Tester Name:** _______________
**Test Date:** _______________
**Browser(s) Tested:** _______________
**Test Environment:** [ ] Dev [ ] Staging [ ] Production

**Overall Result:**
- [ ] ALL TESTS PASSED ✓
- [ ] MINOR ISSUES (documented below)
- [ ] CRITICAL ISSUES (blocking deployment)

**Notes/Comments:**
_________________________________________________
_________________________________________________
_________________________________________________

**Approved for Deployment:** [ ] YES [ ] NO

**Signature:** _______________
