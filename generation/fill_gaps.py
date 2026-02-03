#!/usr/bin/env python3
"""Fill subcategory gaps with targeted product generation"""
import json, re, time, os
from pathlib import Path
import urllib.request

BASE_DIR = Path("/home/ubuntu/hbb")
LISTS_DIR = BASE_DIR / "generation/product_lists"

with open(BASE_DIR / ".secrets") as f:
    API_KEY = f.read().strip()

def call_claude(prompt):
    for attempt in range(3):
        try:
            data = json.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 4000, "messages": [{"role": "user", "content": prompt}]}).encode()
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=data, headers={"Content-Type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())["content"][0]["text"]
        except Exception as e:
            print(f"  API error: {e}")
            time.sleep(5)
    return None

# Real gaps to fill (excluding perfume capitalized duplicates)
GAPS = {
    "perfumes": [
        "aromatic-fougere", "aromatic-herbal", "aromatic-marine", "aromatic-spicy",
        "chypre-floral", "chypre-fruity", "chypre-green", "chypre-leather",
        "floral-aldehyde", "floral-aquatic", "floral-green",
        "fresh-fruity", "fresh-green", "fresh-ozonic",
        "gourmand-chocolate", "gourmand-coffee", "gourmand-sweet", "gourmand-vanilla",
        "oriental-amber", "oriental-floral", "oriental-woody",
        "woody-dry", "woody-earthy", "woody-mossy", "woody-spicy"
    ],
    "skincare": [
        "ceramides", "clinique", "dark-circles", "glow-recipe", "lancome",
        "neutrogena", "salicylic-acid", "tatcha", "vichy"
    ],
    "makeup": [
        "dry-skin", "eye-primer", "nail-polish", "nails", "oily-skin", "satin", "sensitive-skin"
    ],
    "haircare": [
        "coily-hair", "fine-hair", "gisou", "hair-growth", "hair-spray",
        "john-frieda", "k18", "natural-hair", "scalp-health", "scalp-treatment",
        "split-ends", "straight-hair", "styling-cream", "styling-gel",
        "thick-hair", "thinning", "wavy-hair"
    ]
}

for category, gap_slugs in GAPS.items():
    if not gap_slugs:
        continue
    
    with open(LISTS_DIR / f"{category}.json") as f:
        products = json.load(f)
    existing_slugs = {p["slug"] for p in products}
    
    print(f"\n{'='*50}")
    print(f"FILLING {category.upper()}: {len(gap_slugs)} gaps")
    print(f"{'='*50}")
    
    # Batch gaps together for efficiency
    prompt = f"""I need 4 popular {category} products for EACH of these subcategories. Products should be real, well-known items.

Subcategories to fill:
{json.dumps(gap_slugs)}

Existing product slugs to EXCLUDE: {json.dumps(list(existing_slugs)[:100])}

Return a JSON array of products. Each must have:
- "brand": brand name
- "name": product name
- "slug": URL slug (brand-product format)
- "subcategories": array of ALL relevant subcategory slugs (include the target gap subcategory + any other applicable ones)
{"- " + chr(34) + "gender" + chr(34) + ": " + chr(34) + "women" + chr(34) + "/" + chr(34) + "men" + chr(34) + "/" + chr(34) + "unisex" + chr(34) if category == "perfumes" else ""}

For perfumes, subcategories include: women/men/unisex, floral/oriental/woody/fresh/aromatic/chypre/gourmand, subfamily slugs, and occasion slugs (everyday/evening/romantic/office/summer/winter/wedding/sport/travel).

Return ONLY the JSON array."""

    resp = call_claude(prompt)
    if resp:
        try:
            m = re.search(r'\[[\s\S]*\]', resp)
            if m:
                new_products = json.loads(m.group())
                added = 0
                for p in new_products:
                    if p.get("slug") and p["slug"] not in existing_slugs:
                        products.append(p)
                        existing_slugs.add(p["slug"])
                        added += 1
                print(f"  Added {added} new products")
        except Exception as e:
            print(f"  Parse error: {e}")
    
    with open(LISTS_DIR / f"{category}.json", 'w') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"  Total {category}: {len(products)}")
    time.sleep(2)

print("\n✅ Gap filling complete!")
