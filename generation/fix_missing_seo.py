#!/usr/bin/env python3
"""Fill missing SEO content for perfume subcategories"""
import os, json, re, time, sys
from pathlib import Path

WORKER_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
TOTAL_WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 1

BASE_DIR = Path("/home/ubuntu/hbb")
with open(BASE_DIR / ".secrets") as f:
    API_KEY = f.read().strip()

LANG_NAMES = {
    "en": "English", "fr": "French", "de": "German", "es": "Spanish",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "pl": "Polish",
    "tr": "Turkish", "ja": "Japanese", "ko": "Korean", "zh": "Chinese",
    "ar": "Arabic", "hi": "Hindi"
}

def call_claude(prompt):
    import urllib.request
    for attempt in range(3):
        try:
            data = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=data,
                headers={"Content-Type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())["content"][0]["text"]
        except Exception as e:
            print(f"  [W{WORKER_ID}] API error (attempt {attempt+1}): {e}")
            time.sleep(5 * (attempt + 1))
    return None

# Load missing list
with open("/tmp/missing_seo.json") as f:
    all_missing = json.load(f)

# Split work
my_tasks = [t for i, t in enumerate(all_missing) if i % TOTAL_WORKERS == WORKER_ID]
print(f"[W{WORKER_ID}] {len(my_tasks)} tasks (of {len(all_missing)} total)")

processed = 0
for task in my_tasks:
    lang = task["lang"]
    section = task["section"]
    slug = task["slug"]
    filepath = BASE_DIR / task["path"]
    lang_name = LANG_NAMES[lang]
    
    # Human-readable slug
    display_slug = slug.replace("-", " ").title()
    
    print(f"[W{WORKER_ID}] {lang}/{section}/{slug}...")
    
    prompt = f"""You are a beauty and fragrance expert writing for a premium beauty blog. Generate SEO content for a perfume subcategory page.

Category: Perfumes
Subcategory: {display_slug} (slug: {slug})
Language: {lang_name}

Write ALL content in {lang_name}. Return ONLY valid JSON (no markdown):
{{"seo_title": "50-60 char meta title about {display_slug} perfumes", "intro_title": "Engaging H1 title with one relevant emoji", "intro": "400-500 words expert introduction about {display_slug} fragrances. Cover history, key characteristics, popular notes, when to wear, and who they suit. Use natural paragraphs, not lists.", "faq": [{{"question": "Q1", "answer": "Detailed 80-100 word answer"}}, {{"question": "Q2", "answer": "Detailed 80-100 word answer"}}, {{"question": "Q3", "answer": "Detailed 80-100 word answer"}}, {{"question": "Q4", "answer": "Detailed 80-100 word answer"}}], "seo_bottom": "80-100 word summary for SEO footer"}}"""
    
    resp = call_claude(prompt)
    if not resp:
        print(f"  [W{WORKER_ID}] FAILED: no response")
        continue
    
    try:
        m = re.search(r'\{[\s\S]*\}', resp)
        if not m: raise ValueError("No JSON found")
        seo = json.loads(m.group())
    except Exception as e:
        print(f"  [W{WORKER_ID}] FAILED: parse error: {e}")
        continue
    
    # Read existing file
    with open(filepath) as f:
        content = f.read()
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"  [W{WORKER_ID}] SKIP: bad frontmatter")
        continue
    
    # Build FAQ YAML
    faq_yaml = "\nfaq:\n"
    for item in seo.get("faq", []):
        q = item.get("question", "").replace('"', '\\"')
        a = item.get("answer", "").replace('"', '\\"')
        faq_yaml += f'  - question: "{q}"\n    answer: "{a}"\n'
    
    # Add SEO fields to frontmatter
    fm = parts[1]
    if "seo_title:" not in fm:
        seo_title = seo.get("seo_title", "").replace('"', '\\"')
        fm += f'seo_title: "{seo_title}"\n'
    if "faq:" not in fm:
        fm += faq_yaml
    
    # Build body
    intro_title = seo.get("intro_title", display_slug)
    intro = seo.get("intro", "")
    seo_bottom = seo.get("seo_bottom", "")
    
    body = f"\n## {intro_title}\n\n{intro}\n\n"
    if seo_bottom:
        body += f"---\n\n{seo_bottom}\n"
    
    new_content = f"---{fm}---{body}"
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    processed += 1
    if processed % 10 == 0:
        print(f"  [W{WORKER_ID}] Progress: {processed}/{len(my_tasks)}")

print(f"[W{WORKER_ID}] Done: {processed} processed")
