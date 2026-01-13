import re

# Read the file
with open('web_ui/src/router/index.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
if 'import QueueMonitor' not in content:
    content = content.replace(
        "import NovelReader from '../views/NovelReader.vue'",
        "import NovelReader from '../views/NovelReader.vue'\nimport QueueMonitor from '../views/QueueMonitor.vue'"
    )

# Add route before the closing bracket of children array
route_config = """      {
        path: 'queue',
        name: 'QueueMonitor',
        component: QueueMonitor,
        meta: {
          requiresAuth: true,
          permissions: ['admin']
        }
      },"""

# Find the position to insert (after the last route in children, before the closing ])
if "path: 'queue'" not in content:
    # Insert before the closing ] of children array
    pattern = r"(permissions: \['tag:edit'\]\s+}\s+},)\s+(\])"
    replacement = r"\1\n" + route_config + r"\n    \2"
    content = re.sub(pattern, replacement, content)

# Write back
with open('web_ui/src/router/index.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print('Router file updated successfully')
