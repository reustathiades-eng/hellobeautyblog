#!/usr/bin/env python3
"""
HelloBeautyBlog — Veille Nouveautés Sephora FR
Scrape les derniers produits Sephora, compare avec nos listes,
identifie les nouveautés exploitables pour HBB.

Usage:
  python3 sephora_watch.py              # Run complet
  python3 sephora_watch.py --dry-run    # Affiche sans sauvegarder
"""

import requests
import re
import json
import html as htmlmod
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

# === CONFIG ===
BASE_DIR = Path("/home/ubuntu/hbb")
PRODUCT_LISTS_DIR = BASE_DIR / "generation" / "product_lists"
VEILLE_DIR = BASE_DIR / "veille"
RESULTS_DIR = VEILLE_DIR / "results"
KNOWN_PRODUCTS_FILE = VEILLE_DIR / "known_sephora_pids.json"
ACCEPTED_BRANDS_FILE = VEILLE_DIR / "accepted_brands.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
    'Accept': 'text/html',
    'Accept-Language': 'fr-FR,fr;q=0.9'
}

# Sephora FR Nouveautés category IDs (NC = New Category)
SEPHORA_CATEGORIES = {
    'perfumes': {'cgid': 'NC301', 'label': 'Nouveautés Parfum'},
    'makeup':   {'cgid': 'NC302', 'label': 'Nouveautés Maquillage'},
    'skincare': {'cgid': 'NC303', 'label': 'Nouveautés Soin Visage'},
    'skincare_body': {'cgid': 'NC304', 'label': 'Nouveautés Corps & Bain'},
    'haircare': {'cgid': 'NC307', 'label': 'Nouveautés Cheveux'},
}

SEPHORA_BASE_URL = (
    "https://www.sephora.fr/on/demandware.store/"
    "Sites-Sephora_FR-Site/fr_FR/Search-Show"
)

PAGES_PER_CATEGORY = 2  # 2 pages max (120 products) — covers all nouveautés × 60 = 180 produits par catégorie
PAGE_SIZE = 60


def load_accepted_brands():
    """Load accepted brands from veille/accepted_brands.json (per-category, lowercase).
    Returns dict: {category: set(brand_lower)} + flat set for backward compat."""
    if ACCEPTED_BRANDS_FILE.exists():
        with open(ACCEPTED_BRANDS_FILE) as f:
            data = json.load(f)
        per_cat = {}
        all_brands = set()
        for cat in ['perfumes', 'skincare', 'makeup', 'haircare']:
            cat_brands = set(b.lower() for b in data.get(cat, []))
            per_cat[cat] = cat_brands
            all_brands |= cat_brands
        return per_cat, all_brands
    # Fallback: load from product lists
    print("⚠️  accepted_brands.json non trouvé, fallback sur product_lists")
    brands = set()
    for cat in ['perfumes', 'skincare', 'makeup', 'haircare']:
        filepath = PRODUCT_LISTS_DIR / f"{cat}.json"
        if filepath.exists():
            with open(filepath) as f:
                for p in json.load(f):
                    b = p.get('brand', '').strip()
                    if b:
                        brands.add(b.lower())
    return {}, brands


def load_hbb_slugs():
    """Load all existing product slugs."""
    slugs = set()
    for cat in ['perfumes', 'skincare', 'makeup', 'haircare']:
        filepath = PRODUCT_LISTS_DIR / f"{cat}.json"
        if filepath.exists():
            with open(filepath) as f:
                for p in json.load(f):
                    s = p.get('slug', '').strip()
                    if s:
                        slugs.add(s.lower())
    return slugs


def load_known_pids():
    """Load previously seen Sephora PIDs to detect truly new products."""
    if KNOWN_PRODUCTS_FILE.exists():
        with open(KNOWN_PRODUCTS_FILE) as f:
            return set(json.load(f))
    return set()


def save_known_pids(pids):
    """Save known PIDs for next run comparison."""
    with open(KNOWN_PRODUCTS_FILE, 'w') as f:
        json.dump(sorted(pids), f)


def fetch_sephora_category(cgid, pages=PAGES_PER_CATEGORY):
    """Fetch newest products from a Sephora FR category."""
    products = []
    product_urls_map = {}  # pid_lower -> full URL
    for page in range(pages):
        start = page * PAGE_SIZE
        url = (
            f"{SEPHORA_BASE_URL}?cgid={cgid}"
            f"&srule=newest&format=ajax&sz={PAGE_SIZE}&start={start}"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                print(f"  ⚠️  Page {page}: HTTP {r.status_code}")
                continue

            raw_products = re.findall(
                r'data-tcproduct="({[^"]+})"', r.text
            )
            for raw in raw_products:
                try:
                    decoded = htmlmod.unescape(raw)
                    p = json.loads(decoded)
                    products.append(p)
                except (json.JSONDecodeError, Exception):
                    continue

            print(f"  Page {page}: {len(raw_products)} produits")

            # Also capture product URLs (contain correct PID casing)
            page_urls = re.findall(r'href="(https://www\.sephora\.fr/p/[^"]+)"', r.text)
            for u in page_urls:
                if u not in product_urls_map:
                    # Extract PID from URL (last segment before .html)
                    pid_match = re.search(r'-([A-Za-z0-9]+)\.html', u)
                    if pid_match:
                        product_urls_map[pid_match.group(1).lower()] = u

            sleep(0.5)  # Polite delay

        except requests.RequestException as e:
            print(f"  ❌ Page {page}: {e}")
            continue

    return products, product_urls_map


def normalize_brand(brand_str):
    """Normalize brand name for comparison."""
    return brand_str.lower().strip()


def generate_slug(brand, name):
    """Generate a slug from brand + product name."""
    import unicodedata
    text = f"{brand} {name}".lower().strip()
    # Remove accents
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Keep only alphanum and spaces, then replace spaces with hyphens
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text


def get_product_image_urls(product_url):
    """Fetch carousel images (full-size) from a Sephora product page.
    Returns list of image URLs in display order (swatch first, then product photos)."""
    if not product_url:
        return []
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return []
        zoom_imgs = re.findall(r'data-zoom-image="([^"]+)"', r.text)
        seen = set()
        carousel = []
        for img in zoom_imgs:
            clean = htmlmod.unescape(img)
            base = clean.split('?')[0]
            if 'media_' not in base and '/content/' not in base:
                continue
            if base not in seen:
                seen.add(base)
                if not base.startswith('http'):
                    base = 'https://media.sephora.eu' + base
                carousel.append(base)
        return carousel
    except Exception as e:
        print(f"  ⚠️  Image fetch error: {e}")
        return []


def classify_product(sephora_product, source_category=None):
    """Extract structured info from a Sephora product dict."""
    brand = sephora_product.get('product_trademark', '').strip()
    raw_name = sephora_product.get('product_pid_name', '').strip()
    price = sephora_product.get('product_price_ati', '')
    pid = sephora_product.get('product_pid', '')
    sku = sephora_product.get('product_sku', '')
    target = sephora_product.get('product_target', '')
    nature = sephora_product.get('product_nature', '')
    section = sephora_product.get('product_section', '')
    url = sephora_product.get('product_url_page', '')
    breadcrumb = sephora_product.get('product_breadcrumb_label', '')
    instock = sephora_product.get('product_instock', '') == 'y'

    # Clean name: remove " - description" suffix for slug
    name_parts = raw_name.split(' - ')
    clean_name = name_parts[0].strip() if name_parts else raw_name
    description = ' - '.join(name_parts[1:]).strip() if len(name_parts) > 1 else ''

    # Determine gender
    gender = 'unisex'
    target_lower = target.lower()
    if target_lower in ('femme', 'women', 'woman'):
        gender = 'women'
    elif target_lower in ('homme', 'men', 'man'):
        gender = 'men'
    elif target_lower == 'mixte':
        gender = 'unisex'

    # Map to HBB category — source category from fetch is most reliable
    hbb_category = source_category or 'unknown'
    # Normalize skincare_body → skincare
    if hbb_category == 'skincare_body':
        hbb_category = 'skincare'
    return {
        'brand': brand.title(),
        'brand_raw': brand,
        'name': clean_name,
        'full_name': raw_name,
        'description': description,
        'slug': generate_slug(brand, clean_name),
        'price_eur': price,
        'gender': gender,
        'nature': nature,
        'hbb_category': hbb_category,
        'sephora_pid': pid,
        'sephora_sku': sku,
        'sephora_url': url,
        'breadcrumb': breadcrumb,
        'in_stock': instock,
        'detected_at': datetime.now(timezone.utc).isoformat(),
    }


def is_real_product(product):
    """Filter out coffrets, duos, minis, combos, tools, and non-product items."""
    name_lower = product['full_name'].lower()
    nature_lower = product['nature'].lower()
    bc_lower = product.get('breadcrumb', '').lower()
    
    # Skip coffrets, sets, duos, minis, combos, accessories
    skip_keywords = [
        'coffret', 'coffrets', 'set ', 'duo ', 'trio ',
        'mini ', 'travel', 'format voyage', 'routine',
        'kit ', 'collection ', 'bestsellers',
        'combo ', 'combo ', 'essentiels ', 'popular set',
        'rituel ',
    ]
    skip_natures = ['coffrets', 'sets', 'miniatures', 'accessoires',
                    'fer a lisser', 'fer a boucler', 'seche-cheveux']
    
    
    for kw in skip_keywords:
        if kw in name_lower:
            return False
    for sn in skip_natures:
        if sn in nature_lower:
            return False
    
    # Skip products with unknown category (unclassifiable)
    if product.get('hbb_category') == 'unknown':
        return False
    
    return True


def run_veille(dry_run=False, fetch_images_in_dry_run=False):
    """Main veille function."""
    print(f"{'='*60}")
    print(f"🔍 HelloBeautyBlog — Veille Sephora FR")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Load reference data
    brands_per_cat, hbb_brands = load_accepted_brands()
    hbb_slugs = load_hbb_slugs()
    known_pids = load_known_pids()

    print(f"📊 Référence HBB: {len(hbb_brands)} marques acceptées, {len(hbb_slugs)} produits existants")
    if brands_per_cat:
        for cat, bs in sorted(brands_per_cat.items()):
            print(f"   {cat}: {len(bs)} marques")
    print(f"📊 PIDs Sephora déjà vus: {len(known_pids)}")
    print()

    # Fetch all categories
    all_sephora = []
    all_product_urls = {}  # pid_lower -> sephora URL
    for cat_key, cat_info in SEPHORA_CATEGORIES.items():
        print(f"📡 Fetch {cat_info['label']} ({cat_info['cgid']})...")
        products, urls_map = fetch_sephora_category(cat_info['cgid'])
        # Tag with our category
        for p in products:
            p['_hbb_cat'] = cat_key
        all_sephora.extend(products)
        all_product_urls.update(urls_map)
        print(f"  → {len(products)} produits récupérés\n")

    print(f"📦 Total Sephora brut: {len(all_sephora)} produits\n")

    # Process and classify
    classified = []
    seen_pids = set()
    for sp in all_sephora:
        product = classify_product(sp, source_category=sp.get("_hbb_cat"))
        pid = product['sephora_pid']
        # Attach page URL for image fetching later
        product['sephora_page_url'] = all_product_urls.get(pid.lower(), '')

        # Deduplicate
        if pid in seen_pids:
            continue
        seen_pids.add(pid)

        # Filter real products (not coffrets/sets)
        if not is_real_product(product):
            continue

        # Match our brands (category-aware if available)
        brand_lower = normalize_brand(product['brand_raw'])
        cat = product['hbb_category']
        if brands_per_cat and cat in brands_per_cat:
            if brand_lower not in brands_per_cat[cat]:
                continue
        elif brand_lower not in hbb_brands:
            continue

        classified.append(product)

    print(f"✅ Après filtrage (vrais produits, nos marques): {len(classified)}")

    # Identify truly new (not in our slugs AND not seen before)
    new_products = []
    existing_on_sephora = []
    for p in classified:
        slug = p['slug']
        pid = p['sephora_pid']

        # Check if slug already exists in HBB
        slug_exists = any(
            slug.startswith(existing) or existing.startswith(slug)
            for existing in hbb_slugs
        )

        if not slug_exists:
            p['is_new_to_hbb'] = True
            p['first_seen'] = pid not in known_pids
            new_products.append(p)
        else:
            existing_on_sephora.append(p)

    # Sort new products by brand
    new_products.sort(key=lambda x: (x['hbb_category'], x['brand']))

    print(f"🆕 Nouveaux pour HBB: {len(new_products)}")
    print(f"📌 Déjà dans HBB: {len(existing_on_sephora)}")
    print()

    # Fetch carousel images for new products
    if new_products and (not dry_run or fetch_images_in_dry_run):
        print(f"\n🖼️  Récupération images pour {len(new_products)} nouveautés...")
        for i, p in enumerate(new_products):
            page_url = p.get('sephora_page_url', '')
            if page_url:
                images = get_product_image_urls(page_url)
                p['sephora_images'] = images
                status = f"{len(images)} imgs" if images else "0 imgs"
                print(f"  [{i+1}/{len(new_products)}] {p['brand']}: {status}")
                sleep(0.3)
            else:
                p['sephora_images'] = []
                print(f"  [{i+1}/{len(new_products)}] {p['brand']}: pas d'URL page")
        imgs_total = sum(len(p.get('sephora_images', [])) for p in new_products)
        print(f"  ✅ {imgs_total} images récupérées au total\n")
    elif new_products and dry_run and not fetch_images_in_dry_run:
        print(f"\n🖼️  Dry-run: images non récupérées (utiliser --with-images pour tester)")
        for p in new_products:
            p['sephora_images'] = []

    # Display results
    if new_products:
        print(f"{'='*60}")
        print(f"🆕 NOUVEAUTÉS DÉTECTÉES ({len(new_products)} produits)")
        print(f"{'='*60}\n")

        by_category = {}
        for p in new_products:
            cat = p['hbb_category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(p)

        for cat, prods in sorted(by_category.items()):
            print(f"--- {cat.upper()} ({len(prods)}) ---")
            for p in prods:
                star = "⭐" if p['first_seen'] else "  "
                print(f"  {star} {p['brand']:25s} | {p['name'][:45]:45s} | {p['price_eur']:>7s}€ | {p['gender']}")
            print()

    # Save results
    if not dry_run:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save today's results
        today = datetime.now().strftime('%Y-%m-%d')
        result_file = RESULTS_DIR / f"veille_{today}.json"
        result_data = {
            'date': today,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'stats': {
                'sephora_total': len(all_sephora),
                'filtered': len(classified),
                'new_for_hbb': len(new_products),
                'already_in_hbb': len(existing_on_sephora),
            },
            'new_products': new_products,
        }
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Résultats sauvegardés: {result_file}")

        # Update known PIDs
        all_current_pids = known_pids | seen_pids
        save_known_pids(all_current_pids)
        print(f"💾 PIDs mis à jour: {len(all_current_pids)} total")

        # Save latest results as a stable reference
        latest_file = VEILLE_DIR / "latest_new_products.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(new_products, f, ensure_ascii=False, indent=2)
        print(f"💾 Dernières nouveautés: {latest_file}")

    else:
        print("🔸 Dry-run — rien sauvegardé")

    print(f"\n{'='*60}")
    print(f"✅ Veille terminée")
    print(f"{'='*60}")

    return new_products


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    with_images = '--with-images' in sys.argv
    run_veille(dry_run=dry_run, fetch_images_in_dry_run=with_images)
