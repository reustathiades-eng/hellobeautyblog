#!/usr/bin/env python3
"""Step 1: Generate lists of most popular products per category via Claude API"""
import json, re, time, os, sys
from pathlib import Path
import urllib.request

BASE_DIR = Path("/home/ubuntu/hbb")
OUTPUT_DIR = BASE_DIR / "generation/product_lists"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / ".secrets") as f:
    API_KEY = f.read().strip()

EXISTING_PERFUMES = [
    "1-million", "acqua-di-gio", "black-opium", "bleu-de-chanel",
    "boss-alive", "chanel-no5", "coco-mademoiselle", "dior-sauvage",
    "good-girl", "guerlain-shalimar", "jadore", "la-vie-est-belle", "miss-dior"
]

def call_claude(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            data = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 8000,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=data,
                headers={"Content-Type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"}
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode())["content"][0]["text"]
        except Exception as e:
            print(f"  API error ({attempt+1}): {e}")
            time.sleep(5 * (attempt + 1))
    return None

def generate_batch(category, batch_num, batch_size, total_target, existing_slugs, extra_context=""):
    start = (batch_num - 1) * batch_size + 1
    end = min(batch_num * batch_size, total_target)
    
    exclude_text = ""
    # Load already generated products to exclude
    outfile = OUTPUT_DIR / f"{category}.json"
    already = []
    if outfile.exists():
        with open(outfile) as f:
            already = json.load(f)
        exclude_slugs = [p["slug"] for p in already] + existing_slugs
        if exclude_slugs:
            exclude_text = f"\n\nEXCLUDE these products (already in database): {', '.join(exclude_slugs[-100:])}"
            if len(exclude_slugs) > 100:
                exclude_text += f"\n... and {len(exclude_slugs)-100} more already generated."
    
    prompts = {
        "perfumes": f"""List {batch_size} of the world's most popular and iconic PERFUMES/FRAGRANCES (products #{start}-{end} of {total_target}).
Include a diverse mix of:
- Luxury brands (Chanel, Dior, Tom Ford, Creed, etc.)
- Designer brands (Versace, Prada, Dolce & Gabbana, etc.)
- Celebrity fragrances
- Niche brands (Maison Francis Kurkdjian, Byredo, Le Labo, etc.)
- Both men's and women's fragrances, plus unisex
- Classic bestsellers AND recent popular launches (2020-2025)
- Various price ranges (affordable to luxury)
{exclude_text}""",

        "skincare": f"""List {batch_size} of the world's most popular SKINCARE products (products #{start}-{end} of {total_target}).
Include a diverse mix of:
- Cleansers, toners, serums, moisturizers, eye creams, sunscreens, masks, oils, exfoliators
- Brands: CeraVe, The Ordinary, La Roche-Posay, Estée Lauder, SK-II, Drunk Elephant, etc.
- K-beauty (COSRX, Laneige, Sulwhasoo), J-beauty (Shiseido, SK-II)
- Various skin concerns: anti-aging, acne, hydration, dark spots, sensitive skin
- Various price ranges
{exclude_text}""",

        "makeup": f"""List {batch_size} of the world's most popular MAKEUP products (products #{start}-{end} of {total_target}).
Include a diverse mix of:
- Foundations, concealers, powders, blushes, bronzers, highlighters
- Eyeshadow palettes, eyeliners, mascaras, eyebrow products
- Lipsticks, lip glosses, lip liners
- Brands: MAC, NARS, Charlotte Tilbury, Fenty Beauty, Rare Beauty, Urban Decay, Too Faced, etc.
- K-beauty makeup, drugstore favorites
- Various price ranges
{exclude_text}""",

        "haircare": f"""List {batch_size} of the world's most popular HAIRCARE products (products #{start}-{end} of {total_target}).
Include a diverse mix of:
- Shampoos, conditioners, hair masks, oils, serums, treatments, styling products
- Brands: Olaplex, Kérastase, Moroccanoil, Dyson, ghd, Redken, Pantene, etc.
- Products for different hair types: straight, wavy, curly, coily, fine, thick
- Hair concerns: damage repair, color protection, frizz, hair loss, dandruff
- Various price ranges
{exclude_text}"""
    }
    
    prompt = f"""{prompts[category]}

{extra_context}

Return ONLY a valid JSON array. Each product must have:
- "brand": brand name
- "name": product name (without brand)
- "slug": URL-friendly slug (lowercase, hyphens, no accents) — format: brand-product e.g. "chanel-chance-eau-tendre"
- "gender": "women" / "men" / "unisex" (for perfumes only)
- "subcategories": array of relevant subcategory slugs this product belongs to

For perfumes subcategories, use these exact slugs:
- gender: women, men, unisex
- family: floral, oriental, woody, fresh, aromatic, chypre, gourmand
- subfamily: floral-fruity, floral-white, floral-powdery, oriental-spicy, oriental-vanilla, woody-aromatic, fresh-citrus, fresh-aquatic, etc.
- occasion: everyday, evening, romantic, office, summer, winter, wedding, sport, travel

For skincare subcategories: cleanser, toner, serum, moisturizer, eye-cream, sunscreen, mask, exfoliator, oil, mist, spot-treatment, essence, dry, oily, combination, sensitive, normal, anti-aging, acne, dark-spots, redness, hydration, pores, wrinkles, dullness, etc.

For makeup subcategories: foundation, concealer, powder, blush, bronzer, highlighter, eyeshadow, eyeliner, mascara, eyebrow, lipstick, lip-gloss, lip-liner, nail-polish, primer, setting-spray, contour, etc.

For haircare subcategories: shampoo, conditioner, hair-mask, hair-oil, hair-serum, styling, dry-shampoo, leave-in, heat-protectant, straight, wavy, curly, coily, fine, color-protection, damage-repair, hair-loss, dandruff, frizz, etc.

Return ONLY the JSON array, no explanation."""

    print(f"  Generating batch {batch_num} ({start}-{end})...")
    resp = call_claude(prompt)
    if not resp:
        return []
    
    try:
        m = re.search(r'\[[\s\S]*\]', resp)
        if m:
            products = json.loads(m.group())
            print(f"  Got {len(products)} products")
            return products
    except Exception as e:
        print(f"  Parse error: {e}")
    return []

def generate_category(category, target, existing_slugs=[], batch_size=50):
    outfile = OUTPUT_DIR / f"{category}.json"
    
    if outfile.exists():
        with open(outfile) as f:
            all_products = json.load(f)
        print(f"Resuming {category}: {len(all_products)} already generated")
    else:
        all_products = []
    
    # Calculate remaining
    remaining = target - len(all_products)
    if remaining <= 0:
        print(f"{category}: already at target ({len(all_products)}/{target})")
        return
    
    batches_needed = (remaining + batch_size - 1) // batch_size
    current_batch = len(all_products) // batch_size + 1
    
    print(f"\n{'='*50}")
    print(f"GENERATING {category.upper()}: {remaining} remaining (target: {target})")
    print(f"{'='*50}")
    
    for i in range(batches_needed):
        batch = generate_batch(category, current_batch + i, batch_size, target, existing_slugs)
        
        if batch:
            # Deduplicate by slug
            existing = {p["slug"] for p in all_products}
            new_products = [p for p in batch if p.get("slug") and p["slug"] not in existing and p["slug"] not in existing_slugs]
            all_products.extend(new_products)
            
            # Save after each batch
            with open(outfile, 'w') as f:
                json.dump(all_products, f, indent=2, ensure_ascii=False)
            
            print(f"  Total {category}: {len(all_products)}/{target}")
        
        time.sleep(2)
    
    print(f"\n✅ {category}: {len(all_products)} products generated")

def main():
    cat = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if cat in ("perfumes", "all"):
        generate_category("perfumes", 500, EXISTING_PERFUMES)
    if cat in ("skincare", "all"):
        generate_category("skincare", 200)
    if cat in ("makeup", "all"):
        generate_category("makeup", 500)
    if cat in ("haircare", "all"):
        generate_category("haircare", 200)
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    for cat in ["perfumes", "skincare", "makeup", "haircare"]:
        f = OUTPUT_DIR / f"{cat}.json"
        if f.exists():
            with open(f) as fh:
                data = json.load(fh)
            print(f"  {cat}: {len(data)} products")

if __name__ == "__main__":
    main()
