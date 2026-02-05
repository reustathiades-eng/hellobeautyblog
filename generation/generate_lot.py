#!/usr/bin/env python3
"""
Generate product articles from a lot.json file.
For each product:
  1. Download images → convert to WebP
  2. Generate EN article via Claude API (using category-specific brief)
  3. Translate to 13 other languages via Claude API
  4. Update status in image manager
  
Usage: python3 generate_lot.py [lot.json] [--skip-images] [--lang=fr,de] [--product=slug]
"""

import json, os, sys, time, urllib.request, urllib.error, re, subprocess, hashlib
from pathlib import Path
from datetime import datetime

# ===== CONFIG =====
BASE = Path("/home/ubuntu/hbb")
SECRETS = BASE / ".secrets"
PROMPTS = BASE / "generation" / "prompts"
CONTENT = BASE / "content"
STATIC_IMG = BASE / "static" / "images"
IMG_MANAGER_DATA = BASE / "generation" / "image_manager" / "data.json"
LOG_DIR = Path("/tmp")
MODEL = "claude-sonnet-4-5-20250929"
MAX_RETRIES = 3

ALL_LANGS = ["en","fr","de","es","it","pt","nl","pl","tr","ja","ko","zh","ar","hi"]
TRANSLATE_LANGS = [l for l in ALL_LANGS if l != "en"]

# Language display names
LANG_NAMES = {
    "fr": "French", "de": "German", "es": "Spanish", "it": "Italian",
    "pt": "Portuguese", "nl": "Dutch", "pl": "Polish", "tr": "Turkish",
    "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "ar": "Arabic", "hi": "Hindi"
}

# Category folder mapping per language
CAT_FOLDERS = {
    "en": {"perfumes": "perfumes", "skincare": "skincare", "makeup": "makeup", "haircare": "haircare"},
    "fr": {"perfumes": "parfums", "skincare": "soins", "makeup": "maquillage", "haircare": "cheveux"},
    "de": {"perfumes": "parfum", "skincare": "hautpflege", "makeup": "make-up", "haircare": "haarpflege"},
    "es": {"perfumes": "perfumes", "skincare": "cuidado-piel", "makeup": "maquillaje", "haircare": "cabello"},
    "it": {"perfumes": "profumi", "skincare": "skincare", "makeup": "trucco", "haircare": "capelli"},
    "pt": {"perfumes": "perfumes", "skincare": "cuidados-pele", "makeup": "maquiagem", "haircare": "cabelos"},
    "nl": {"perfumes": "parfum", "skincare": "huidverzorging", "makeup": "make-up", "haircare": "haarverzorging"},
    "pl": {"perfumes": "perfumy", "skincare": "pielegnacja", "makeup": "makijaz", "haircare": "wlosy"},
    "tr": {"perfumes": "parfum", "skincare": "cilt-bakimi", "makeup": "makyaj", "haircare": "sac-bakimi"},
    "ja": {"perfumes": "perfumes", "skincare": "skincare", "makeup": "makeup", "haircare": "haircare"},
    "ko": {"perfumes": "perfumes", "skincare": "skincare", "makeup": "makeup", "haircare": "haircare"},
    "zh": {"perfumes": "perfumes", "skincare": "skincare", "makeup": "makeup", "haircare": "haircare"},
    "ar": {"perfumes": "perfumes", "skincare": "skincare", "makeup": "makeup", "haircare": "haircare"},
    "hi": {"perfumes": "perfumes", "skincare": "skincare", "makeup": "makeup", "haircare": "haircare"},
}

# Category display names per language (for frontmatter)
CAT_DISPLAY = {
    "fr": {"Perfumes": "Parfums", "Skincare": "Soins", "Makeup": "Maquillage", "Haircare": "Cheveux"},
    "de": {"Perfumes": "Parfum", "Skincare": "Hautpflege", "Makeup": "Make-up", "Haircare": "Haarpflege"},
    "es": {"Perfumes": "Perfumes", "Skincare": "Cuidado de Piel", "Makeup": "Maquillaje", "Haircare": "Cabello"},
    "it": {"Perfumes": "Profumi", "Skincare": "Skincare", "Makeup": "Trucco", "Haircare": "Capelli"},
    "pt": {"Perfumes": "Perfumes", "Skincare": "Cuidados com a Pele", "Makeup": "Maquiagem", "Haircare": "Cabelos"},
    "nl": {"Perfumes": "Parfum", "Skincare": "Huidverzorging", "Makeup": "Make-up", "Haircare": "Haarverzorging"},
    "pl": {"Perfumes": "Perfumy", "Skincare": "Pielęgnacja", "Makeup": "Makijaż", "Haircare": "Włosy"},
    "tr": {"Perfumes": "Parfüm", "Skincare": "Cilt Bakımı", "Makeup": "Makyaj", "Haircare": "Saç Bakımı"},
    "ja": {"Perfumes": "香水", "Skincare": "スキンケア", "Makeup": "メイクアップ", "Haircare": "ヘアケア"},
    "ko": {"Perfumes": "향수", "Skincare": "스킨케어", "Makeup": "메이크업", "Haircare": "헤어케어"},
    "zh": {"Perfumes": "香水", "Skincare": "护肤", "Makeup": "彩妆", "Haircare": "护发"},
    "ar": {"Perfumes": "عطور", "Skincare": "العناية بالبشرة", "Makeup": "مكياج", "Haircare": "العناية بالشعر"},
    "hi": {"Perfumes": "परफ्यूम", "Skincare": "स्किनकेयर", "Makeup": "मेकअप", "Haircare": "हेयरकेयर"},
}

# Author per category
AUTHORS = {
    "perfumes": ("Sophie Laurent", "sophie-laurent"),
    "skincare": ("Emma Chen", "emma-chen"),
    "makeup": ("Isabella Romano", "isabella-romano"),
    "haircare": ("Olivia Taylor", "olivia-taylor"),
}

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)

def get_api_key():
    with open(SECRETS) as f:
        content = f.read().strip()
    # Support both "ANTHROPIC_API_KEY=sk-..." and raw "sk-..." formats
    if "=" in content:
        for line in content.split("\n"):
            if "ANTHROPIC_API_KEY" in line:
                return line.strip().split("=", 1)[1]
    if content.startswith("sk-"):
        return content
    raise ValueError("API key not found in .secrets")

API_KEY = get_api_key()

# ===== IMAGE HANDLING =====
def download_and_convert_images(product):
    """Download images and convert to WebP. Returns list of image paths."""
    slug = product["slug"]
    category = product["category"]
    images = product.get("images", [])
    
    img_dir = STATIC_IMG / category
    img_dir.mkdir(parents=True, exist_ok=True)
    
    result_paths = []
    for i, url in enumerate(images):
        if not url:
            continue
        
        suffix = "" if i == 0 else f"-{i+1}"
        webp_name = f"{slug}{suffix}.webp"
        webp_path = img_dir / webp_name
        
        if webp_path.exists():
            log(f"  Image exists: {webp_name}")
            result_paths.append(f"/images/{category}/{webp_name}")
            continue
        
        try:
            log(f"  Downloading image {i+1}: {url[:80]}...")
            tmp_path = f"/tmp/img_{slug}_{i}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(tmp_path, "wb") as f:
                    f.write(resp.read())
            
            # Convert to WebP
            subprocess.run(
                ["convert", tmp_path, "-resize", "800x800>", "-quality", "82", str(webp_path)],
                check=True, capture_output=True
            )
            os.remove(tmp_path)
            result_paths.append(f"/images/{category}/{webp_name}")
            log(f"  ✅ {webp_name}")
        except Exception as e:
            log(f"  ❌ Image {i+1} failed: {e}")
    
    return result_paths

# ===== API CALLS =====
def call_claude(prompt, max_tokens=8000):
    """Call Claude API with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            payload = json.dumps({
                "model": MODEL,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()
            
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
            
            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text += block["text"]
            return text
            
        except urllib.error.HTTPError as e:
            body = e.read().decode() if hasattr(e, 'read') else ''
            log(f"  API error (attempt {attempt+1}): {e.code} {body[:200]}")
            if e.code == 429:
                wait = 30 * (attempt + 1)
                log(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code >= 500:
                time.sleep(10 * (attempt + 1))
            else:
                raise
        except Exception as e:
            log(f"  API error (attempt {attempt+1}): {e}")
            time.sleep(10 * (attempt + 1))
    
    raise Exception(f"API call failed after {MAX_RETRIES} attempts")

# ===== CONTENT GENERATION =====
def clean_response(text):
    """Clean API response: remove code fences, fix common YAML issues."""
    # Remove markdown code fences
    text = re.sub(r'^```(?:yaml|markdown|md)?\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()
    
    # Ensure starts with ---
    if not text.startswith("---"):
        idx = text.find("---")
        if idx >= 0:
            text = text[idx:]
    
    return text

def fix_yaml_quotes(content):
    """Ensure tags and keywords have quoted values in YAML arrays."""
    def quote_inline_array(match):
        key = match.group(1)
        values = match.group(2)
        items = [i.strip().strip('"').strip("'") for i in values.split(',')]
        quoted = ', '.join(f'"{i}"' for i in items if i)
        return f"{key}: [{quoted}]"
    
    content = re.sub(r'^(tags): \[([^\]]+)\]', quote_inline_array, content, flags=re.MULTILINE)
    content = re.sub(r'^(keywords): \[([^\]]+)\]', quote_inline_array, content, flags=re.MULTILINE)
    return content

def inject_images(content, image_paths):
    """Replace empty images array with actual image paths."""
    if not image_paths:
        return content
    
    # Check if images are already present (non-empty)
    # This prevents duplication if Claude already added them
    existing_images = re.search(r'^images:\s*\n\s*-\s*"', content, flags=re.MULTILINE)
    if existing_images:
        # Images already present, don't inject again
        return content
    
    img_yaml = "images:\n" + "\n".join(f'  - "{p}"' for p in image_paths)
    
    # Replace empty arrays or empty images: declarations
    content = re.sub(r'^images:\s*\[\s*\]', img_yaml, content, flags=re.MULTILINE)
    content = re.sub(r'^images:\s*$', img_yaml, content, flags=re.MULTILINE)
    
    return content
def generate_en_article(product, image_paths):
    """Generate English article using category-specific brief."""
    category = product["category"]
    brief_file = PROMPTS / f"{category}.txt"
    
    with open(brief_file) as f:
        brief = f.read()
    
    # Fill in product data
    prompt = brief.replace("{brand}", product["brand"])
    prompt = prompt.replace("{name}", product["name"])
    prompt = prompt.replace("{slug}", product["slug"])
    prompt = prompt.replace("{subcategories}", ", ".join(product.get("subcategories", [])))
    if "gender" in product:
        prompt = prompt.replace("{gender}", product["gender"])
    
    # Add images info
    if image_paths:
        prompt += f"\n\n=== IMAGES ===\nUse these image paths in the frontmatter images array:\n"
        for p in image_paths:
            prompt += f"  - \"{p}\"\n"
        prompt += "Put the swatch/product image FIRST.\n"
    
    log(f"  Generating EN article...")
    response = call_claude(prompt, max_tokens=8000)
    content = clean_response(response)
    content = fix_yaml_quotes(content)
    
    if image_paths:
        content = inject_images(content, image_paths)
    
    return content

def translate_article(en_content, target_lang, category):
    """Translate EN article to target language."""
    with open(PROMPTS / "translate.txt") as f:
        brief = f.read()
    
    # Fill in language-specific data
    lang_name = LANG_NAMES[target_lang]
    cat_display = CAT_DISPLAY.get(target_lang, {})
    
    prompt = brief.replace("{target_language}", lang_name)
    prompt = prompt.replace("{perfumes_cat}", cat_display.get("Perfumes", "Perfumes"))
    prompt = prompt.replace("{skincare_cat}", cat_display.get("Skincare", "Skincare"))
    prompt = prompt.replace("{makeup_cat}", cat_display.get("Makeup", "Makeup"))
    prompt = prompt.replace("{haircare_cat}", cat_display.get("Haircare", "Haircare"))
    prompt = prompt.replace("{english_article_content}", en_content)
    
    log(f"  Translating to {target_lang} ({lang_name})...")
    response = call_claude(prompt, max_tokens=10000)
    content = clean_response(response)
    content = fix_yaml_quotes(content)
    
    return content

def save_article(content, lang, category, slug):
    """Save article to the correct content directory."""
    cat_folder = CAT_FOLDERS.get(lang, {}).get(category, category)
    out_dir = CONTENT / lang / cat_folder
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / f"{slug}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    log(f"  ✅ Saved: {out_file.relative_to(BASE)}")
    return out_file

# ===== STATUS TRACKING =====
def update_manager_status(slug, status, generated_langs=None):
    """Update product status in the image manager data file."""
    try:
        if IMG_MANAGER_DATA.exists():
            with open(IMG_MANAGER_DATA) as f:
                data = json.load(f)
        else:
            data = {"products": {}, "published": []}
        
        if slug not in data["products"]:
            data["products"][slug] = {"images": [], "status": "pending", "generated_langs": []}
        
        data["products"][slug]["status"] = status
        if generated_langs:
            data["products"][slug]["generated_langs"] = generated_langs
        
        if status == "published" and slug not in data["published"]:
            data["published"].append(slug)
        
        with open(IMG_MANAGER_DATA, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"  ⚠️ Could not update manager: {e}")

# ===== MAIN =====
def process_product(product, target_langs=None, skip_images=False):
    """Process a single product: images → EN → translations."""
    slug = product["slug"]
    category = product["category"]
    
    log(f"{'='*60}")
    log(f"🔸 {product['brand']} — {product['name']} ({category})")
    log(f"  Slug: {slug}")
    log(f"  Subcategories: {', '.join(product.get('subcategories', []))}")
    
    # Step 1: Images
    image_paths = []
    if not skip_images:
        image_paths = download_and_convert_images(product)
        log(f"  Images: {len(image_paths)} ready")
    
    # Step 2: Generate EN
    en_file = CONTENT / "en" / CAT_FOLDERS["en"][category] / f"{slug}.md"
    if en_file.exists():
        log(f"  EN article already exists, reading...")
        with open(en_file) as f:
            en_content = f.read()
        # Update images if we have new ones
        if image_paths and "images: []" in en_content:
            en_content = inject_images(en_content, image_paths)
            save_article(en_content, "en", category, slug)
    else:
        update_manager_status(slug, "generating", ["en"])
        en_content = generate_en_article(product, image_paths)
        save_article(en_content, "en", category, slug)
    
    generated_langs = ["en"]
    
    # Step 3: Translate
    langs_to_do = target_langs or TRANSLATE_LANGS
    for lang in langs_to_do:
        lang_file = CONTENT / lang / CAT_FOLDERS[lang][category] / f"{slug}.md"
        if lang_file.exists():
            log(f"  {lang} already exists, skipping")
            generated_langs.append(lang)
            continue
        
        try:
            translated = translate_article(en_content, lang, category)
            save_article(translated, lang, category, slug)
            generated_langs.append(lang)
            update_manager_status(slug, "generating", generated_langs)
            
            # Brief pause between API calls
            time.sleep(2)
        except Exception as e:
            log(f"  ❌ {lang} FAILED: {e}")
    
    # Step 4: Update final status
    if set(generated_langs) >= set(ALL_LANGS):
        update_manager_status(slug, "published", generated_langs)
        log(f"  🎉 PUBLISHED — all 14 languages")
    else:
        missing = set(ALL_LANGS) - set(generated_langs)
        update_manager_status(slug, "error", generated_langs)
        log(f"  ⚠️ Partial — missing: {', '.join(sorted(missing))}")
    
    return generated_langs

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate HBB product articles from lot.json")
    parser.add_argument("lot_file", nargs="?", default="lot.json", help="Path to lot.json")
    parser.add_argument("--skip-images", action="store_true", help="Skip image download")
    parser.add_argument("--lang", type=str, help="Comma-separated langs to generate (e.g. fr,de)")
    parser.add_argument("--product", type=str, help="Process only this product slug")
    parser.add_argument("--en-only", action="store_true", help="Generate EN only, no translations")
    args = parser.parse_args()
    
    # Load lot
    lot_path = Path(args.lot_file)
    if not lot_path.is_absolute():
        lot_path = BASE / "generation" / lot_path
    
    with open(lot_path) as f:
        lot = json.load(f)
    
    log(f"📦 Loaded lot: {len(lot)} products")
    
    # Filter by product if specified
    if args.product:
        lot = [p for p in lot if p["slug"] == args.product]
        if not lot:
            log(f"❌ Product '{args.product}' not found in lot")
            sys.exit(1)
    
    # Determine target languages
    target_langs = None
    if args.en_only:
        target_langs = []
    elif args.lang:
        target_langs = [l.strip() for l in args.lang.split(",")]
    
    # Process
    start = time.time()
    results = {"success": 0, "partial": 0, "failed": 0}
    
    for i, product in enumerate(lot):
        log(f"\n[{i+1}/{len(lot)}]")
        try:
            langs = process_product(product, target_langs, args.skip_images)
            if len(langs) == 14:
                results["success"] += 1
            else:
                results["partial"] += 1
        except Exception as e:
            log(f"  💀 FATAL: {e}")
            results["failed"] += 1
            update_manager_status(product["slug"], "error")
    
    elapsed = time.time() - start
    log(f"\n{'='*60}")
    log(f"✅ Done in {elapsed/60:.1f} min")
    log(f"   Success (14/14): {results['success']}")
    log(f"   Partial:         {results['partial']}")
    log(f"   Failed:          {results['failed']}")

if __name__ == "__main__":
    main()
