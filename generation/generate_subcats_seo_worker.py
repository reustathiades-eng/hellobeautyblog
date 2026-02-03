#!/usr/bin/env python3
"""Worker-based SEO generation - pass worker_id (0-3) and total_workers (4) as args"""
import os, json, re, time, sys
from pathlib import Path

WORKER_ID = int(sys.argv[1])
TOTAL_WORKERS = int(sys.argv[2])

BASE_DIR = Path("/home/ubuntu/hbb")
CONTENT_DIR = BASE_DIR / "content"
DATA_DIR = BASE_DIR / "data/subcategories"

with open(BASE_DIR / ".secrets") as f:
    API_KEY = f.read().strip()

LANGS = {
    "en": {"name": "English", "section_skincare": "skincare", "section_makeup": "makeup", "section_haircare": "haircare"},
    "fr": {"name": "French", "section_skincare": "soins", "section_makeup": "maquillage", "section_haircare": "cheveux"},
    "de": {"name": "German", "section_skincare": "hautpflege", "section_makeup": "make-up", "section_haircare": "haarpflege"},
    "es": {"name": "Spanish", "section_skincare": "cuidado-piel", "section_makeup": "maquillaje", "section_haircare": "cabello"},
    "it": {"name": "Italian", "section_skincare": "skincare", "section_makeup": "trucco", "section_haircare": "capelli"},
    "pt": {"name": "Portuguese", "section_skincare": "cuidados-pele", "section_makeup": "maquiagem", "section_haircare": "cabelos"},
    "nl": {"name": "Dutch", "section_skincare": "huidverzorging", "section_makeup": "make-up", "section_haircare": "haarverzorging"},
    "pl": {"name": "Polish", "section_skincare": "pielegnacja", "section_makeup": "makijaz", "section_haircare": "wlosy"},
    "tr": {"name": "Turkish", "section_skincare": "cilt-bakimi", "section_makeup": "makyaj", "section_haircare": "sac-bakimi"},
    "ja": {"name": "Japanese", "section_skincare": "skincare", "section_makeup": "makeup", "section_haircare": "haircare"},
    "ko": {"name": "Korean", "section_skincare": "skincare", "section_makeup": "makeup", "section_haircare": "haircare"},
    "zh": {"name": "Chinese", "section_skincare": "skincare", "section_makeup": "makeup", "section_haircare": "haircare"},
    "ar": {"name": "Arabic", "section_skincare": "skincare", "section_makeup": "makeup", "section_haircare": "haircare"},
    "hi": {"name": "Hindi", "section_skincare": "skincare", "section_makeup": "makeup", "section_haircare": "haircare"},
}

def call_claude(prompt):
    import urllib.request
    for attempt in range(3):
        try:
            data = json.dumps({"model": "claude-sonnet-4-20250514", "max_tokens": 4000, "messages": [{"role": "user", "content": prompt}]}).encode()
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=data, headers={"Content-Type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())["content"][0]["text"]
        except Exception as e:
            print(f"  [W{WORKER_ID}] API error: {e}")
            time.sleep(5 * (attempt + 1))
    return None

def get_subcategories():
    subcats = []
    for json_file in sorted(DATA_DIR.glob("*.json")):
        section = json_file.stem.split("_")[0]
        subcat_type = "_".join(json_file.stem.split("_")[1:])
        with open(json_file) as f:
            data = json.load(f)
        if "en" in data:
            for slug, info in sorted(data["en"].items()):
                subcats.append({"section": section, "type": subcat_type, "slug": slug, "emoji": info.get("emoji", "")})
    return subcats

def generate_seo(section, subcat_type, slug, lang, lang_name):
    prompt = f"""You are a beauty content expert. Generate SEO content for a {section} subcategory page in {lang_name}.
Section: {section}, Type: {subcat_type}, Slug: {slug}

Return ONLY valid JSON:
{{"seo_title": "50-60 char meta title", "intro_title": "H1 title with emoji", "intro": "400-500 words expert introduction about this subcategory", "faq": [{{"question": "Q1", "answer": "A1"}}, {{"question": "Q2", "answer": "A2"}}, {{"question": "Q3", "answer": "A3"}}, {{"question": "Q4", "answer": "A4"}}], "seo_bottom": "80-100 word summary"}}

ALL content in {lang_name}. No markdown, only JSON."""
    resp = call_claude(prompt)
    if resp:
        try:
            m = re.search(r'\{[\s\S]*\}', resp)
            if m: return json.loads(m.group())
        except: pass
    return None

def update_file(filepath, seo):
    with open(filepath, 'r') as f:
        content = f.read()
    if 'seo_title:' in content and len(content) > 500: return False
    parts = content.split('---', 2)
    if len(parts) < 3: return False
    faq_yaml = ""
    for q in seo.get('faq', []):
        faq_yaml += f'  - question: "{q.get("question","").replace(chr(34), chr(39))}"\n    answer: "{q.get("answer","").replace(chr(34), chr(39))}"\n'
    new_fm = f"""{parts[1]}
seo_title: "{seo.get('seo_title','').replace(chr(34), chr(39))}"
intro_title: "{seo.get('intro_title','').replace(chr(34), chr(39))}"
seo_bottom: "{seo.get('seo_bottom','').replace(chr(34), chr(39))}"
faq:
{faq_yaml}"""
    with open(filepath, 'w') as f:
        f.write(f"---{new_fm}---\n\n{seo.get('intro', '')}\n")
    return True

def load_progress():
    """Shared progress file with file locking"""
    pf = BASE_DIR / "generation/subcats_seo_progress.json"
    if pf.exists():
        try:
            with open(pf) as f: return set(json.load(f))
        except: return set()
    return set()

def save_progress(done):
    pf = BASE_DIR / "generation/subcats_seo_progress.json"
    # Use temp file + rename for atomic write
    tmp = pf.with_suffix('.tmp')
    with open(tmp, 'w') as f: json.dump(list(done), f)
    os.rename(tmp, pf)

def main():
    subcats = get_subcategories()
    # Build full task list
    tasks = []
    for sc in subcats:
        for lang, lc in LANGS.items():
            tasks.append((sc, lang, lc))
    
    # Split by worker: each worker takes every Nth task
    my_tasks = [t for i, t in enumerate(tasks) if i % TOTAL_WORKERS == WORKER_ID]
    
    print(f"[W{WORKER_ID}] Starting: {len(my_tasks)} tasks (of {len(tasks)} total)")
    
    processed = 0
    for sc, lang, lc in my_tasks:
        key = f"{sc['section']}:{sc['slug']}:{lang}"
        
        # Check shared progress (reload periodically)
        if processed % 5 == 0:
            done = load_progress()
        if key in done:
            continue
        
        section_slug = lc.get(f"section_{sc['section']}", sc['section'])
        fp = CONTENT_DIR / lang / section_slug / sc['slug'] / "_index.md"
        if not fp.exists(): continue
        
        print(f"[W{WORKER_ID}] {lang}/{section_slug}/{sc['slug']}")
        seo = generate_seo(sc['section'], sc['type'], sc['slug'], lang, lc['name'])
        
        if seo and update_file(fp, seo):
            processed += 1
            done = load_progress()
            done.add(key)
            save_progress(done)
        
        time.sleep(0.5)
    
    print(f"[W{WORKER_ID}] Done: {processed} processed")

if __name__ == "__main__":
    main()
