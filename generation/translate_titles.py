#!/usr/bin/env python3
"""Translate title and description of subcategory pages across all languages."""
import os, sys, json, time, re, subprocess, glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/ubuntu/hbb"
SECRETS = open(f"{BASE}/.secrets").read().strip()
LANGS = ["fr","de","es","it","pt","nl","pl","tr","ja","ko","zh","ar","hi"]

LANG_NAMES = {
    "fr":"French","de":"German","es":"Spanish","it":"Italian","pt":"Portuguese",
    "nl":"Dutch","pl":"Polish","tr":"Turkish","ja":"Japanese","ko":"Korean",
    "zh":"Chinese Simplified","ar":"Arabic","hi":"Hindi"
}

SECTION_NAMES = {
    "fr": {"soins":"Skincare","cheveux":"Haircare","maquillage":"Makeup","parfums":"Perfumes"},
    "de": {"hautpflege":"Skincare","haarpflege":"Haircare","make-up":"Makeup","parfum":"Perfumes"},
    "es": {"cuidado-piel":"Skincare","cabello":"Haircare","maquillaje":"Makeup","perfumes":"Perfumes"},
    "it": {"skincare":"Skincare","capelli":"Haircare","trucco":"Makeup","profumi":"Perfumes"},
    "pt": {"cuidados-pele":"Skincare","cabelos":"Haircare","maquiagem":"Makeup","perfumes":"Perfumes"},
    "nl": {"huidverzorging":"Skincare","haarverzorging":"Haircare","makeup":"Makeup","parfum":"Perfumes"},
    "pl": {"pielegnacja":"Skincare","wlosy":"Haircare","makijaz":"Makeup","perfumy":"Perfumes"},
    "tr": {"cilt-bakimi":"Skincare","sac-bakimi":"Haircare","makyaj":"Makeup","parfum":"Perfumes"},
    "ja": {"skincare":"Skincare","haircare":"Haircare","makeup":"Makeup","perfumes":"Perfumes"},
    "ko": {"skincare":"Skincare","haircare":"Haircare","makeup":"Makeup","perfumes":"Perfumes"},
    "zh": {"skincare":"Skincare","haircare":"Haircare","makeup":"Makeup","perfumes":"Perfumes"},
    "ar": {"skincare":"Skincare","haircare":"Haircare","makeup":"Makeup","perfumes":"Perfumes"},
    "hi": {"skincare":"Skincare","haircare":"Haircare","makeup":"Makeup","perfumes":"Perfumes"},
}

def find_pages_to_translate():
    """Find all pages with English title/description."""
    tasks = []
    for lang in LANGS:
        lang_dir = Path(BASE) / "content" / lang
        for section_dir in lang_dir.iterdir():
            if not section_dir.is_dir() or section_dir.name.startswith('.'):
                continue
            for subcat_dir in section_dir.iterdir():
                if not subcat_dir.is_dir():
                    continue
                index_file = subcat_dir / "_index.md"
                if not index_file.exists():
                    continue
                content = index_file.read_text()
                if 'description: "Discover the best' in content:
                    slug = subcat_dir.name
                    section = section_dir.name
                    category = SECTION_NAMES.get(lang, {}).get(section, section)
                    tasks.append({
                        "file": str(index_file),
                        "lang": lang,
                        "slug": slug,
                        "section": section,
                        "category": category,
                        "content": content
                    })
    return tasks

def call_api(prompt, max_retries=3):
    """Call Claude API."""
    import urllib.request
    for attempt in range(max_retries):
        try:
            data = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": SECRETS,
                    "anthropic-version": "2023-06-01"
                }
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                return result["content"][0]["text"].strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

def translate_batch(batch):
    """Translate a batch of slugs for one language."""
    lang = batch[0]["lang"]
    lang_name = LANG_NAMES[lang]
    
    slugs_info = []
    for task in batch:
        slugs_info.append(f"- {task['slug']} (category: {task['category']})")
    
    prompt = f"""Translate these beauty product subcategory names into {lang_name}. 
For each slug, provide a natural, SEO-friendly title and a short description (max 120 chars).

Slugs:
{chr(10).join(slugs_info)}

Respond ONLY with a JSON object mapping slug to {{"title": "...", "description": "..."}}.
Example: {{"oily": {{"title": "Peau Grasse", "description": "Découvrez les meilleurs produits pour peau grasse."}}}}

IMPORTANT: 
- Titles should be natural in {lang_name}, not literal translations
- Descriptions should be compelling and relevant to beauty/cosmetics
- Brand names (CeraVe, Clinique, etc.) stay unchanged in titles
- For ingredient names, use the common {lang_name} term
- JSON only, no markdown, no explanation"""

    result = call_api(prompt)
    if not result:
        return []
    
    try:
        # Clean potential markdown
        result = result.strip()
        if result.startswith("{") is False: result = result[result.index("{"):]
        if "}" in result: result = result[:result.rindex("}")+1]
        translations = json.loads(result)
    except Exception as e:
        print(f"  JSON parse error: {e}", flush=True)
        print(f"  Raw: {result[:200]}", flush=True)
        return []
    
    updated = []
    for task in batch:
        slug = task["slug"]
        if slug in translations:
            t = translations[slug]
            new_title = t.get("title", "")
            new_desc = t.get("description", "")
            if new_title and new_desc:
                content = task["content"]
                # Replace title
                content = re.sub(
                    r'^title: ".*"',
                    f'title: "{new_title}"',
                    content, count=1, flags=re.MULTILINE
                )
                # Replace description
                content = re.sub(
                    r'^description: "Discover the best.*"',
                    f'description: "{new_desc}"',
                    content, count=1, flags=re.MULTILINE
                )
                Path(task["file"]).write_text(content)
                updated.append(f"{task['lang']}/{task['section']}/{slug}")
    return updated

def worker(worker_id, tasks):
    """Process tasks in batches of ~15 per API call."""
    results = []
    # Group by language
    by_lang = {}
    for t in tasks:
        by_lang.setdefault(t["lang"], []).append(t)
    
    for lang, lang_tasks in by_lang.items():
        # Process in batches of 15
        for i in range(0, len(lang_tasks), 10):
            batch = lang_tasks[i:i+10]
            updated = translate_batch(batch)
            results.extend(updated)
            print(f"[Worker {worker_id}] {lang}: translated {len(updated)}/{len(batch)} ({i+len(batch)}/{len(lang_tasks)})", flush=True)
            time.sleep(0.5)
    
    return results

def main():
    tasks = find_pages_to_translate()
    print(f"Found {len(tasks)} pages to translate across {len(LANGS)} languages")
    
    # Split tasks across 4 workers
    n_workers = 4
    worker_tasks = [[] for _ in range(n_workers)]
    for i, task in enumerate(tasks):
        worker_tasks[i % n_workers].append(task)
    
    all_results = []
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = {}
        for wid in range(n_workers):
            f = executor.submit(worker, wid, worker_tasks[wid])
            futures[f] = wid
        
        for f in as_completed(futures):
            wid = futures[f]
            try:
                results = f.result()
                all_results.extend(results)
                print(f"[Worker {wid}] DONE: {len(results)} translated", flush=True)
            except Exception as e:
                print(f"[Worker {wid}] ERROR: {e}", flush=True)
    
    print(f"\nTotal translated: {len(all_results)}/{len(tasks)}")
    
    # Auto commit
    os.chdir(BASE)
    os.system('git add content/ && git commit -m "feat: translate subcategory titles/descriptions across 13 languages" && git push origin main')

if __name__ == "__main__":
    main()
