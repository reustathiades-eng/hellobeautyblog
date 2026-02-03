import json, os
os.chdir("/home/ubuntu/hbb")

SECTIONS = {"skincare": "skincare", "makeup": "makeup", "haircare": "haircare"}

def slugify_title(slug):
    return slug.replace("-", " ").title()

created = 0
for section in SECTIONS:
    for filename in os.listdir("data/subcategories"):
        if filename.startswith(f"{section}_") and filename.endswith(".json"):
            subcat_type = filename.replace(f"{section}_", "").replace(".json", "")
            with open(f"data/subcategories/{filename}") as f:
                data = json.load(f)
            for slug, info in data.get("en", {}).items():
                emoji = info.get("emoji", "📦")
                dir_path = f"content/en/{section}/{slug}"
                os.makedirs(dir_path, exist_ok=True)
                title = slugify_title(slug)
                content = f'''---
title: "{title}"
description: "Discover the best {title.lower()} products. Expert reviews and guides."
emoji: "{emoji}"
subcategory_type: "{subcat_type}"
subcategory_value: "{slug}"
translationKey: "{section}-{slug}"
url: "/en/{section}/{slug}/"
---
'''
                with open(f"{dir_path}/_index.md", "w") as f:
                    f.write(content)
                created += 1
print(f"Created {created} pages")
