#!/usr/bin/env python3
"""Fix subcategory coverage: auto-map brands/ingredients, then fill gaps"""
import json, os, re, time
from pathlib import Path
from collections import defaultdict
import urllib.request

BASE_DIR = Path("/home/ubuntu/hbb")
LISTS_DIR = BASE_DIR / "generation/product_lists"
DATA_DIR = BASE_DIR / "data/subcategories"

with open(BASE_DIR / ".secrets") as f:
    API_KEY = f.read().strip()

# Brand slug mapping
BRAND_MAP = {
    "perfumes": {},  # perfumes don't have brand subcats
    "skincare": {
        "cerave": ["cerave"], "CeraVe": ["cerave"],
        "clinique": ["clinique"], "Clinique": ["clinique"],
        "the ordinary": ["the-ordinary"], "The Ordinary": ["the-ordinary"],
        "drunk elephant": ["drunk-elephant"], "Drunk Elephant": ["drunk-elephant"],
        "estée lauder": ["estee-lauder"], "Estee Lauder": ["estee-lauder"], "Estée Lauder": ["estee-lauder"],
        "glow recipe": ["glow-recipe"], "Glow Recipe": ["glow-recipe"],
        "kiehl's": ["kiehls"], "Kiehls": ["kiehls"], "Kiehl's": ["kiehls"],
        "la roche-posay": ["la-roche-posay"], "La Roche-Posay": ["la-roche-posay"],
        "lancôme": ["lancome"], "Lancome": ["lancome"], "Lancôme": ["lancome"],
        "neutrogena": ["neutrogena"], "Neutrogena": ["neutrogena"],
        "olay": ["olay"], "Olay": ["olay"],
        "paula's choice": ["paulas-choice"], "Paula's Choice": ["paulas-choice"],
        "sk-ii": ["sk-ii"], "SK-II": ["sk-ii"],
        "tatcha": ["tatcha"], "Tatcha": ["tatcha"],
        "vichy": ["vichy"], "Vichy": ["vichy"],
    },
    "makeup": {
        "bobbi brown": ["bobbi-brown"], "Bobbi Brown": ["bobbi-brown"],
        "chanel": ["chanel-beauty"], "Chanel": ["chanel-beauty"],
        "charlotte tilbury": ["charlotte-tilbury"], "Charlotte Tilbury": ["charlotte-tilbury"],
        "dior": ["dior-beauty"], "Dior": ["dior-beauty"],
        "e.l.f.": ["elf"], "e.l.f": ["elf"], "E.L.F.": ["elf"], "elf": ["elf"],
        "fenty beauty": ["fenty-beauty"], "Fenty Beauty": ["fenty-beauty"],
        "huda beauty": ["huda-beauty"], "Huda Beauty": ["huda-beauty"],
        "mac": ["mac"], "MAC": ["mac"],
        "maybelline": ["maybelline"], "Maybelline": ["maybelline"],
        "nars": ["nars"], "NARS": ["nars"],
        "nyx": ["nyx"], "NYX": ["nyx"],
        "rare beauty": ["rare-beauty"], "Rare Beauty": ["rare-beauty"],
        "tarte": ["tarte"], "Tarte": ["tarte"],
        "too faced": ["too-faced"], "Too Faced": ["too-faced"],
        "urban decay": ["urban-decay"], "Urban Decay": ["urban-decay"],
    },
    "haircare": {
        "aveda": ["aveda"], "Aveda": ["aveda"],
        "briogeo": ["briogeo"], "Briogeo": ["briogeo"],
        "bumble and bumble": ["bumble-and-bumble"], "Bumble and Bumble": ["bumble-and-bumble"],
        "garnier": ["garnier"], "Garnier": ["garnier"],
        "gisou": ["gisou"], "Gisou": ["gisou"],
        "john frieda": ["john-frieda"], "John Frieda": ["john-frieda"],
        "k18": ["k18"], "K18": ["k18"],
        "kérastase": ["kerastase"], "Kerastase": ["kerastase"], "Kérastase": ["kerastase"],
        "living proof": ["living-proof"], "Living Proof": ["living-proof"],
        "l'oréal professionnel": ["loreal-professionnel"], "L'Oreal Professionnel": ["loreal-professionnel"],
        "moroccanoil": ["moroccanoil"], "Moroccanoil": ["moroccanoil"],
        "olaplex": ["olaplex"], "Olaplex": ["olaplex"],
        "pantene": ["pantene"], "Pantene": ["pantene"],
        "redken": ["redken"], "Redken": ["redken"],
        "tresemmé": ["tresemme"], "TRESemme": ["tresemme"], "TRESemmé": ["tresemme"],
    }
}

# Ingredient/concern keyword mapping for skincare
SKINCARE_KEYWORDS = {
    "vitamin c": ["vitamin-c"], "vitamin C": ["vitamin-c"],
    "niacinamide": ["niacinamide"],
    "salicylic acid": ["salicylic-acid"], "salicylic": ["salicylic-acid"],
    "glycolic acid": ["glycolic-acid"], "glycolic": ["glycolic-acid"],
    "peptide": ["peptides"], "peptides": ["peptides"],
    "ceramide": ["ceramides"], "ceramides": ["ceramides"],
    "dark circle": ["dark-circles"], "under eye": ["dark-circles"],
    "firm": ["firmness"], "firming": ["firmness"],
    "mature": ["mature"], "anti-aging": ["mature"],
}

# Makeup keyword mapping
MAKEUP_KEYWORDS = {
    "eyebrow": ["brows"], "brow": ["brows"],
    "eye primer": ["eye-primer"],
    "false lash": ["false-lashes"], "false eyelash": ["false-lashes"],
    "nail": ["nails"], "nail polish": ["nail-polish", "nails"],
    "lip": ["lips"], "lipstick": ["lips", "lipstick"], "lip gloss": ["lips", "lip-gloss"],
    "eye": ["eyes"], "eyeshadow": ["eyes", "eyeshadow"], "eyeliner": ["eyes", "eyeliner"],
    "mascara": ["eyes", "mascara"],
    "foundation": ["face", "foundation"], "concealer": ["face", "concealer"],
    "blush": ["face", "blush"], "bronzer": ["face", "bronzer"],
    "dry skin": ["dry-skin"], "oily skin": ["oily-skin"], "sensitive skin": ["sensitive-skin"],
    "satin": ["satin"],
}

# Haircare keyword mapping  
HAIRCARE_KEYWORDS = {
    "curly": ["curly-hair"], "curl": ["curly-hair"],
    "straight": ["straight-hair"], "straighten": ["straight-hair"],
    "wavy": ["wavy-hair"], "wave": ["wavy-hair"],
    "fine hair": ["fine-hair"], "thin hair": ["fine-hair"],
    "thick hair": ["thick-hair"],
    "coily": ["coily-hair"], "coil": ["coily-hair"],
    "natural hair": ["natural-hair"],
    "color": ["color-treated"], "colour": ["color-treated"],
    "repair": ["repair"], "damage": ["repair"],
    "split end": ["split-ends"],
    "scalp": ["scalp-health", "scalp-treatment"],
    "hair growth": ["hair-growth"], "hair loss": ["thinning", "hair-growth"],
    "thinning": ["thinning"],
    "shine": ["shine"],
    "heat protect": ["heat-protection"], "thermal": ["heat-protection"],
    "hair spray": ["hair-spray"], "hairspray": ["hair-spray"],
    "styling cream": ["styling-cream"],
    "styling gel": ["styling-gel"], "hair gel": ["styling-gel"],
    "serum": ["serum"],
    "dry shampoo": ["dry-shampoo"],
}

# Perfume case fix (subcats have both cases)
PERFUME_CASE_FIX = {
    "Women": "women", "Men": "men", "Unisex": "unisex",
    "Evening": "evening", "Everyday": "everyday", "Office": "office",
    "Romantic": "romantic", "Sport": "sport", "Summer": "summer",
    "Travel": "travel", "Wedding": "wedding", "Winter": "winter",
}

def enrich_subcategories(category, products):
    """Add brand and keyword-based subcategories to products"""
    brand_map = BRAND_MAP.get(category, {})
    
    if category == "skincare":
        keywords = SKINCARE_KEYWORDS
    elif category == "makeup":
        keywords = MAKEUP_KEYWORDS
    elif category == "haircare":
        keywords = HAIRCARE_KEYWORDS
    else:
        keywords = {}
    
    for p in products:
        existing = set(p.get("subcategories", []))
        brand = p.get("brand", "")
        name = p.get("name", "")
        full_text = f"{brand} {name}".lower()
        
        # Add brand subcategories
        for brand_key, slugs in brand_map.items():
            if brand_key.lower() == brand.lower():
                existing.update(slugs)
        
        # Add keyword-based subcategories
        for keyword, slugs in keywords.items():
            if keyword.lower() in full_text:
                existing.update(slugs)
        
        # Fix perfume case
        if category == "perfumes":
            fixed = set()
            for s in existing:
                fixed.add(PERFUME_CASE_FIX.get(s, s))
            existing = fixed
        
        p["subcategories"] = list(existing)
    
    return products

def main():
    # Step 1: Enrich existing products
    for cat in ['perfumes', 'skincare', 'makeup', 'haircare']:
        f = LISTS_DIR / f"{cat}.json"
        with open(f) as fh:
            products = json.load(fh)
        
        products = enrich_subcategories(cat, products)
        
        with open(f, 'w') as fh:
            json.dump(products, fh, indent=2, ensure_ascii=False)
        
        print(f"✅ Enriched {cat}: {len(products)} products")
    
    # Step 2: Check coverage
    all_subcats = {}
    for fname in os.listdir(DATA_DIR):
        if fname.endswith('.json'):
            section = fname.split('_')[0]
            with open(f'{DATA_DIR}/{fname}') as f:
                data = json.load(f)
            if 'en' in data:
                for slug in data['en']:
                    all_subcats[f"{section}:{slug}"] = section
    
    # Add perfume subcats from content
    perf_dir = BASE_DIR / "content/en/perfumes"
    for d in os.listdir(perf_dir):
        p = perf_dir / d
        if p.is_dir() and (p / "_index.md").exists():
            all_subcats[f"perfumes:{d}"] = "perfumes"
    
    subcat_counts = defaultdict(int)
    for cat in ['perfumes', 'skincare', 'makeup', 'haircare']:
        with open(LISTS_DIR / f"{cat}.json") as f:
            products = json.load(f)
        for p in products:
            for sc in p.get('subcategories', []):
                subcat_counts[f"{cat}:{sc}"] += 1
    
    gaps = []
    for key, section in sorted(all_subcats.items()):
        count = subcat_counts.get(key, 0)
        if count < 3:
            gaps.append((key, count, section))
    
    print(f"\n=== AFTER ENRICHMENT ===")
    print(f"Total subcategories: {len(all_subcats)}")
    print(f"Gaps (< 3 products): {len(gaps)}")
    
    if gaps:
        print(f"\nRemaining gaps:")
        for key, count, section in gaps:
            print(f"  {key}: {count}")
    
    # Save gaps for API fill
    with open(LISTS_DIR / "gaps.json", 'w') as f:
        json.dump(gaps, f, indent=2)

if __name__ == "__main__":
    main()
