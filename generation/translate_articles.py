#!/usr/bin/env python3
"""
Translate EN articles to 13 other languages via Claude API.
Usage: python3 translate_articles.py skincare|makeup|haircare|blog
"""
import json, os, sys, time, urllib.request, re

os.chdir("/home/ubuntu/hbb")
API_KEY = open(".secrets").read().strip()

SECTION = sys.argv[1] if len(sys.argv) > 1 else "skincare"

LANGS = {
    "fr": ("French", {"skincare":"soins","makeup":"maquillage","haircare":"cheveux","blog":"blog"}),
    "de": ("German", {"skincare":"hautpflege","makeup":"make-up","haircare":"haarpflege","blog":"blog"}),
    "es": ("Spanish", {"skincare":"cuidado-piel","makeup":"maquillaje","haircare":"cabello","blog":"blog"}),
    "it": ("Italian", {"skincare":"skincare","makeup":"trucco","haircare":"capelli","blog":"blog"}),
    "pt": ("Portuguese", {"skincare":"cuidados-pele","makeup":"maquiagem","haircare":"cabelos","blog":"blog"}),
    "nl": ("Dutch", {"skincare":"huidverzorging","makeup":"make-up","haircare":"haarverzorging","blog":"blog"}),
    "pl": ("Polish", {"skincare":"pielegnacja","makeup":"makijaz","haircare":"wlosy","blog":"blog"}),
    "tr": ("Turkish", {"skincare":"cilt-bakimi","makeup":"makyaj","haircare":"sac-bakimi","blog":"blog"}),
    "ja": ("Japanese", {"skincare":"skincare","makeup":"makeup","haircare":"haircare","blog":"blog"}),
    "ko": ("Korean", {"skincare":"skincare","makeup":"makeup","haircare":"haircare","blog":"blog"}),
    "zh": ("Chinese", {"skincare":"skincare","makeup":"makeup","haircare":"haircare","blog":"blog"}),
    "ar": ("Arabic", {"skincare":"skincare","makeup":"makeup","haircare":"haircare","blog":"blog"}),
    "hi": ("Hindi", {"skincare":"skincare","makeup":"makeup","haircare":"haircare","blog":"blog"}),
}

def call_api(prompt):
    payload = json.dumps({
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 3000,
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    text = data["content"][0]["text"].strip()
    if text.startswith("```"): text = text.split("\n", 1)[1]
    if text.endswith("```"): text = text.rsplit("```", 1)[0].strip()
    return text

# Find EN articles without translations
en_dir = f"content/en/{SECTION}"
articles = []
for f in sorted(os.listdir(en_dir)):
    if f == "_index.md" or not f.endswith(".md"):
        continue
    path = os.path.join(en_dir, f)
    content = open(path, encoding="utf-8").read()
    key_match = re.search(r'translationKey:\s*"([^"]+)"', content)
    if not key_match:
        print(f"WARN: no translationKey in {f}, skip")
        continue
    key = key_match.group(1)
    
    # Check if already translated in all langs
    missing = []
    for lang in LANGS:
        lang_dir = LANGS[lang][1].get(SECTION, SECTION)
        found = False
        search_dir = f"content/{lang}/{lang_dir}"
        if os.path.isdir(search_dir):
            for lf in os.listdir(search_dir):
                if lf.endswith(".md"):
                    lc = open(os.path.join(search_dir, lf), encoding="utf-8").read()
                    if f'translationKey: "{key}"' in lc:
                        found = True
                        break
        if not found:
            missing.append(lang)
    
    if missing:
        articles.append({"file": f, "path": path, "key": key, "content": content, "missing": missing})

if not articles:
    print(f"✅ All {SECTION} articles already translated!")
    sys.exit(0)

total = sum(len(a["missing"]) for a in articles)
print(f"=== {SECTION.upper()}: {len(articles)} articles, {total} translations needed ===")
for a in articles:
    print(f"  {a['key']}: {len(a['missing'])} langs missing")

done = 0
errors = 0

for article in articles:
    en_content = article["content"]
    key = article["key"]
    
    for lang in article["missing"]:
        lang_name, dirs = LANGS[lang]
        lang_dir = dirs.get(SECTION, SECTION)
        
        print(f"[{done+1}/{total}] {key}/{lang} ({lang_name})...", flush=True)
        
        prompt = f"""Translate this beauty blog article to {lang_name}. 

RULES:
1. Return the COMPLETE file: YAML frontmatter + markdown content
2. Translate title, description, tags, keywords, categories to {lang_name}
3. Keep these fields UNCHANGED: translationKey, author, authorSlug, date, lastmod, images, brand, productName, rating, all note fields
4. Create a NEW slug appropriate for {lang_name} (URL-friendly, no accents)
5. Translate ALL markdown content naturally - not word-for-word, adapt idioms
6. Write like a native {lang_name} beauty blogger, warm and personal tone
7. No AI phrases like "it is worth noting" or "in conclusion"
8. Return ONLY the file content, no code fences, no explanation

ORIGINAL EN FILE:
{en_content}"""

        try:
            text = call_api(prompt)
            
            # Verify it has frontmatter
            if not text.startswith("---"):
                print(f"  ❌ No frontmatter, skip", flush=True)
                errors += 1
                time.sleep(2)
                continue
            
            # Verify translationKey is preserved
            if f'translationKey: "{key}"' not in text:
                text = re.sub(
                    r'(title:.*\n)',
                    f'\\1translationKey: "{key}"\n',
                    text, count=1
                )
            
            # Extract slug for filename
            slug_match = re.search(r'slug:\s*"([^"]+)"', text)
            if slug_match:
                filename = slug_match.group(1) + ".md"
            else:
                filename = article["file"]
            
            target_dir = f"content/{lang}/{lang_dir}"
            os.makedirs(target_dir, exist_ok=True)
            target = os.path.join(target_dir, filename)
            
            with open(target, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            
            done += 1
            size = os.path.getsize(target)
            print(f"  ✅ {key}/{lang} ({size}B) [{done}/{total}]", flush=True)
            
        except Exception as e:
            print(f"  ❌ {key}/{lang}: {e}", flush=True)
            errors += 1
        
        time.sleep(3)

print(f"\n=== DONE {SECTION}: {done}/{total} ok, {errors} errors ===")

# Git commit
os.system(f'cd /home/ubuntu/hbb && git add content/ && git commit -m "feat: translate {SECTION} articles to 13 languages ({done} pages)" && git push origin main')
print("=== PUSHED ===")
