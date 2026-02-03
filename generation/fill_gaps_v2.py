#!/usr/bin/env python3
"""Fill remaining gaps - one API call per subcategory for reliability"""
import json, re, time
from pathlib import Path
import urllib.request

BASE_DIR = Path("/home/ubuntu/hbb")
LISTS_DIR = BASE_DIR / "generation/product_lists"

with open(BASE_DIR / ".secrets") as f:
    API_KEY = f.read().strip()

def call_claude(prompt):
    for attempt in range(3):
        try:
            data = json.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "messages": [{"role": "user", "content": prompt}]}).encode()
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=data, headers={"Content-Type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())["content"][0]["text"]
        except Exception as e:
            print(f"  API error: {e}")
            time.sleep(5)
    return None

# Smaller batches for reliability
GAPS = {
    "perfumes": [
        ("aromatic-fougere", "aromatic-herbal", "aromatic-marine", "aromatic-spicy"),
        ("chypre-floral", "chypre-fruity", "chypre-green", "chypre-leather"),
        ("floral-aldehyde", "floral-aquatic", "floral-green"),
        ("fresh-fruity", "fresh-green", "fresh-ozonic"),
        ("gourmand-chocolate", "gourmand-coffee", "gourmand-sweet", "gourmand-vanilla"),
        ("oriental-amber", "oriental-floral", "oriental-woody"),
        ("woody-dry", "woody-earthy", "woody-mossy", "woody-spicy"),
    ],
    "haircare": [
        ("coily-hair", "fine-hair", "thick-hair", "wavy-hair", "straight-hair", "natural-hair"),
        ("gisou", "john-frieda", "k18"),
        ("hair-growth", "thinning", "scalp-health", "scalp-treatment"),
        ("hair-spray", "styling-cream", "styling-gel", "split-ends"),
    ]
}

for category, batches in GAPS.items():
    with open(LISTS_DIR / f"{category}.json") as f:
        products = json.load(f)
    existing_slugs = {p["slug"] for p in products}
    
    print(f"\n=== {category.upper()} ===")
    
    for batch in batches:
        prompt = f"""List 4 real, popular {category} products for EACH subcategory: {', '.join(batch)}

Return ONLY a JSON array. Each product:
- "brand": brand name
- "name": product name  
- "slug": url-slug (brand-product)
- "subcategories": [target subcategory + others that apply]
{"- " + '"gender": "women"/"men"/"unisex"' if category == "perfumes" else ""}

Keep names simple, no special characters. JSON only, no markdown."""

        resp = call_claude(prompt)
        if resp:
            try:
                m = re.search(r'\[[\s\S]*\]', resp)
                if m:
                    new = json.loads(m.group())
                    added = 0
                    for p in new:
                        if p.get("slug") and p["slug"] not in existing_slugs:
                            products.append(p)
                            existing_slugs.add(p["slug"])
                            added += 1
                    print(f"  {batch}: +{added}")
            except Exception as e:
                print(f"  {batch}: parse error {e}")
        time.sleep(1)
    
    with open(LISTS_DIR / f"{category}.json", 'w') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"  Total: {len(products)}")

print("\nDone!")
