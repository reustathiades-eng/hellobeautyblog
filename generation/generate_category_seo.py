#!/usr/bin/env python3
"""
Generate SEO content for category pages in all 14 languages using Claude API
"""

import json
import os
import anthropic
from pathlib import Path

# Load API key
API_KEY = open('/home/ubuntu/hbb/.secrets').read().strip()
client = anthropic.Anthropic(api_key=API_KEY)

LANGUAGES = {
    "en": "English",
    "fr": "French", 
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "it": "Italian",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "ar": "Arabic",
    "zh": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
    "hi": "Hindi"
}

CATEGORIES = {
    "perfumes": {
        "name_en": "Perfumes",
        "subcats": {
            "gender": ["Women", "Men", "Unisex"],
            "family": ["Floral", "Oriental", "Woody", "Fresh"],
            "occasion": ["Everyday", "Evening", "Summer", "Winter"]
        }
    },
    "skincare": {
        "name_en": "Skincare", 
        "subcats": {
            "skin_type": ["Oily", "Dry", "Combination", "Sensitive", "Normal"],
            "routine": ["Cleanser", "Toner", "Serum", "Moisturizer", "SPF", "Mask"],
            "concern": ["Anti-Aging", "Acne", "Hydration", "Brightening", "Pores"]
        }
    },
    "makeup": {
        "name_en": "Makeup",
        "subcats": {
            "face": ["Foundation", "Concealer", "Blush", "Highlighter", "Powder"],
            "eyes": ["Mascara", "Eyeliner", "Eyeshadow", "Brows"],
            "lips": ["Lipstick", "Lip Gloss", "Lip Liner"],
            "nails": ["Nail Polish", "Nail Care"]
        }
    },
    "haircare": {
        "name_en": "Haircare",
        "subcats": {
            "hair_type": ["Fine Hair", "Thick Hair", "Curly Hair", "Straight Hair", "Color-Treated"],
            "concern": ["Volume", "Repair", "Hydration", "Dandruff", "Color Protection"]
        }
    }
}

def generate_lang_content(category_key, lang_code, lang_name, existing_en):
    """Generate content for one language using Claude API"""
    
    prompt = f"""Generate SEO content for a {CATEGORIES[category_key]['name_en']} category page in {lang_name}.

Based on this English version:
{json.dumps(existing_en, indent=2)}

Generate the SAME structure but translated and adapted for {lang_name} speakers.
Return ONLY valid JSON with these exact keys:
- intro_title (catchy title, ~8 words)
- intro (SEO paragraph, ~40 words)  
- subcategories (same structure, translate group titles and item names, keep emojis, adapt URLs with localized slugs)
- faq (3 questions/answers relevant to the category)
- seo_title (section title)
- seo_bottom (SEO paragraph, ~40 words)

For URLs, use appropriate localized category slugs:
- Perfumes: en=perfumes, fr=parfums, de=parfum, es=perfumes, it=profumi, pt=perfumes, nl=parfum, pl=perfumy, tr=parfum, ar=عطور, zh=香水, ja=香水, ko=향수, hi=perfumes
- Skincare: en=skincare, fr=soins, de=hautpflege, es=cuidado-piel, it=skincare, pt=skincare, nl=huidverzorging, pl=pielegnacja, tr=cilt-bakimi
- Makeup: en=makeup, fr=maquillage, de=make-up, es=maquillaje, it=trucco, pt=maquiagem, nl=make-up, pl=makijaz, tr=makyaj
- Haircare: en=haircare, fr=cheveux, de=haarpflege, es=cabello, it=capelli, pt=cabelos, nl=haarverzorging, pl=wlosy, tr=sac-bakimi

Return ONLY the JSON object, no markdown, no explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    text = response.content[0].text.strip()
    # Clean potential markdown
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    
    return json.loads(text)

def main():
    data_dir = Path("/home/ubuntu/hbb/data/categories")
    
    for cat_key in CATEGORIES.keys():
        json_file = data_dir / f"{cat_key}.json"
        print(f"\n{'='*50}")
        print(f"Processing {cat_key}...")
        
        # Load existing
        with open(json_file) as f:
            data = json.load(f)
        
        existing_en = data.get("en", {})
        
        # Generate missing languages
        for lang_code, lang_name in LANGUAGES.items():
            if lang_code in data and lang_code not in ["en", "fr"]:
                print(f"  {lang_code}: already exists, skipping")
                continue
            if lang_code in ["en", "fr"]:
                print(f"  {lang_code}: base language, skipping")
                continue
                
            print(f"  {lang_code}: generating {lang_name}...", end=" ", flush=True)
            try:
                data[lang_code] = generate_lang_content(cat_key, lang_code, lang_name, existing_en)
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
        
        # Save
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {json_file}")

if __name__ == "__main__":
    main()
