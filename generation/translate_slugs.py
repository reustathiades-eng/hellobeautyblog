#!/usr/bin/env python3
"""Translate subcategory URL slugs across all languages."""
import os, sys, json, time, re, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/ubuntu/hbb"
API_KEY = open(f"{BASE}/.secrets").read().strip()
LANGS = ["fr","de","es","it","pt","nl","pl","tr","ja","ko","zh","ar","hi"]

LANG_NAMES = {
    "fr":"French","de":"German","es":"Spanish","it":"Italian","pt":"Portuguese",
    "nl":"Dutch","pl":"Polish","tr":"Turkish","ja":"Japanese","ko":"Korean",
    "zh":"Chinese Simplified","ar":"Arabic","hi":"Hindi"
}

# Map lang -> section folder name -> category key
SECTION_MAP = {
    "fr": {"soins":"skincare","cheveux":"haircare","maquillage":"makeup"},
    "de": {"hautpflege":"skincare","haarpflege":"haircare","make-up":"makeup"},
    "es": {"cuidado-piel":"skincare","cabello":"haircare","maquillaje":"makeup"},
    "it": {"skincare":"skincare","capelli":"haircare","trucco":"makeup"},
    "pt": {"cuidados-pele":"skincare","cabelos":"haircare","maquiagem":"makeup"},
    "nl": {"huidverzorging":"skincare","haarverzorging":"haircare","makeup":"makeup"},
    "pl": {"pielegnacja":"skincare","wlosy":"haircare","makijaz":"makeup"},
    "tr": {"cilt-bakimi":"skincare","sac-bakimi":"haircare","makyaj":"makeup"},
    "ja": {"skincare":"skincare","haircare":"haircare","makeup":"makeup"},
    "ko": {"skincare":"skincare","haircare":"haircare","makeup":"makeup"},
    "zh": {"skincare":"skincare","haircare":"haircare","makeup":"makeup"},
    "ar": {"skincare":"skincare","haircare":"haircare","makeup":"makeup"},
    "hi": {"skincare":"skincare","haircare":"haircare","makeup":"makeup"},
}

def call_api(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            data = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                text = result["content"][0]["text"].strip()
                if "{" in text:
                    text = text[text.index("{"):text.rindex("}")+1]
                return json.loads(text)
        except Exception as e:
            print(f"  API error (attempt {attempt+1}): {e}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None

def get_all_english_slugs():
    """Get all EN subcategory slugs grouped by category."""
    slugs = {"skincare": [], "haircare": [], "makeup": []}
    for cat in slugs:
        cat_dir = Path(BASE) / "content" / "en" / cat
        for d in sorted(cat_dir.iterdir()):
            if d.is_dir() and (d / "_index.md").exists():
                slugs[cat].append(d.name)
    return slugs

def translate_slugs_for_lang(lang, en_slugs):
    """Translate all slugs for one language."""
    lang_name = LANG_NAMES[lang]
    all_slugs = []
    for cat, sluglist in en_slugs.items():
        for s in sluglist:
            all_slugs.append(f"{s} ({cat})")
    
    prompt = f"""Translate these beauty subcategory URL slugs into {lang_name} for a beauty blog.

Rules:
- Output must be URL-safe slugs (lowercase, hyphens, no accents/special chars)
- Brand names stay unchanged: cerave, clinique, drunk-elephant, estee-lauder, glow-recipe, kiehls, la-roche-posay, lancome, maybelline, neutrogena, olay, paulas-choice, sk-ii, tatcha, the-ordinary, vichy, redken, olaplex, kerastase, moroccanoil, pantene, tresemme, loreal, nyx, mac, fenty, charlotte-tilbury, urban-decay, too-faced, benefit, bobbi-brown, nars
- Chemical/ingredient names that are internationally recognized can stay: retinol, niacinamide, ceramides, peptides, glycolic-acid, hyaluronic-acid, salicylic-acid, keratin, biotin
- Common beauty terms should be translated naturally
- For Japanese/Korean/Chinese/Arabic/Hindi: use romanized slugs (e.g. "hadanayami" not "肌悩み")

Slugs to translate:
{chr(10).join(all_slugs)}

Respond with a JSON object mapping English slug to translated slug.
Example: {{"anti-aging": "anti-age", "dry": "seche", "brightening": "eclat"}}
JSON only, no markdown."""

    return call_api(prompt)

def apply_translations(lang, translations, en_slugs):
    """Apply slug translations: update url in _index.md and JSON data."""
    updated = 0
    section_map = SECTION_MAP[lang]
    
    for section_folder, cat_key in section_map.items():
        cat_dir = Path(BASE) / "content" / lang / section_folder
        if not cat_dir.exists():
            continue
        
        for subcat_dir in cat_dir.iterdir():
            if not subcat_dir.is_dir():
                continue
            index_file = subcat_dir / "_index.md"
            if not index_file.exists():
                continue
            
            en_slug = subcat_dir.name
            new_slug = translations.get(en_slug, en_slug)
            
            if new_slug == en_slug:
                continue
            
            content = index_file.read_text()
            old_url = f"/{lang}/{section_folder}/{en_slug}/"
            new_url = f"/{lang}/{section_folder}/{new_slug}/"
            
            content = content.replace(f'url: "{old_url}"', f'url: "{new_url}"')
            index_file.write_text(content)
            updated += 1
    
    # Update JSON data files
    for section_folder, cat_key in section_map.items():
        json_file = Path(BASE) / "data" / "categories" / f"{cat_key}.json"
        if not json_file.exists():
            continue
        data = json.loads(json_file.read_text())
        if lang not in data:
            continue
        
        changed = False
        for group in data[lang].get("subcategories", {}).values():
            for item in group.get("items", []):
                url = item.get("url", "")
                for en_slug, new_slug in translations.items():
                    if en_slug == new_slug:
                        continue
                    old_path = f"/{lang}/{section_folder}/{en_slug}/"
                    new_path = f"/{lang}/{section_folder}/{new_slug}/"
                    if url == old_path:
                        item["url"] = new_path
                        changed = True
        
        # Also check language-specific JSON files (e.g., soins.json for FR)
        lang_json = Path(BASE) / "data" / "categories" / f"{section_folder}.json"
        if lang_json.exists() and lang_json != json_file:
            ldata = json.loads(lang_json.read_text())
            if lang in ldata:
                for group in ldata[lang].get("subcategories", {}).values():
                    for item in group.get("items", []):
                        url = item.get("url", "")
                        for en_slug, new_slug in translations.items():
                            if en_slug == new_slug:
                                continue
                            old_path = f"/{lang}/{section_folder}/{en_slug}/"
                            new_path = f"/{lang}/{section_folder}/{new_slug}/"
                            if url == old_path:
                                item["url"] = new_path
                                changed = True
                lang_json.write_text(json.dumps(ldata, ensure_ascii=False, indent=2))
        
        if changed:
            json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    return updated

def worker(worker_id, langs, en_slugs):
    results = []
    for lang in langs:
        print(f"[Worker {worker_id}] Translating slugs for {lang}...", flush=True)
        translations = translate_slugs_for_lang(lang, en_slugs)
        if not translations:
            print(f"[Worker {worker_id}] {lang}: API FAILED", flush=True)
            continue
        
        # Count translations that actually change
        changed = sum(1 for k, v in translations.items() if k != v)
        print(f"[Worker {worker_id}] {lang}: {changed} slugs to change, applying...", flush=True)
        
        updated = apply_translations(lang, translations, en_slugs)
        print(f"[Worker {worker_id}] {lang}: {updated} files updated", flush=True)
        results.append((lang, updated))
    return results

def main():
    en_slugs = get_all_english_slugs()
    total_en = sum(len(v) for v in en_slugs.values())
    print(f"Found {total_en} EN slugs across {len(en_slugs)} categories")
    for cat, slugs in en_slugs.items():
        print(f"  {cat}: {len(slugs)} slugs")
    
    n_workers = 4
    lang_groups = [[] for _ in range(n_workers)]
    for i, lang in enumerate(LANGS):
        lang_groups[i % n_workers].append(lang)
    
    all_results = []
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = {}
        for wid in range(n_workers):
            f = executor.submit(worker, wid, lang_groups[wid], en_slugs)
            futures[f] = wid
        
        for f in as_completed(futures):
            try:
                results = f.result()
                all_results.extend(results)
            except Exception as e:
                print(f"Worker error: {e}", flush=True)
    
    total_updated = sum(u for _, u in all_results)
    print(f"\nTotal: {total_updated} files updated across {len(all_results)} languages")
    
    # Commit
    os.chdir(BASE)
    os.system('git add content/ data/ && git commit -m "feat: translate subcategory URL slugs across 13 languages" && git push origin main')

if __name__ == "__main__":
    main()
