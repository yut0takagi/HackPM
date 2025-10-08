#!/usr/bin/env python3
import yaml
import re

body = """---
template_type: feature
user_story: <script>alert('xss')</script>As a user, I want "safety"
---"""

yaml_frontmatter_pattern = re.compile(
    r'^---\s*\n(.*?)\n---\s*(?:\n(.*))?', 
    re.DOTALL | re.MULTILINE
)

print("Testing YAML parsing...")
print(f"Body: {repr(body)}")

match = yaml_frontmatter_pattern.match(body.strip())
if match:
    yaml_content = match.group(1)
    print(f"YAML content: {repr(yaml_content)}")
    
    try:
        yaml_data = yaml.safe_load(yaml_content)
        print(f"Parsed YAML: {yaml_data}")
        print(f"User story: {yaml_data.get('user_story')}")
    except Exception as e:
        print(f"YAML parse error: {e}")
else:
    print("No YAML frontmatter match found")