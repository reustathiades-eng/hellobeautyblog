#!/usr/bin/env python3
"""Translate Fenty article to FR, DE, ES, ZH using translate.txt brief"""
import json, os, sys, time, urllib.request, re

os.chdir("/home/ubuntu/hbb")
API_KEY = open(".secrets").read().strip()

# Read the translate brief
with open("generation/prompts/translate.txt", "r") as f:
    TRANSLATE_BRIEF = f.read()

# Read the EN source
EN_FILE = "content/en/makeup/fenty-beauty-pro-filtr-soft-matte-longwear-foundation.md"
with open(EN_FILE, "r") as f:
    EN_CONTENT = f.read()

LANGS = {
    "fr": {
        "name": "French",
        "dir": "content/fr/maquillage",
        "categories": {"Perfumes": "Parfums", "Skincare": "Soins", "Makeup": "Maquillage", "Haircare": "Cheveux"},
    },
    "de": {
        "name": "German",
        "dir": "content/de/make-up",
        "categories": {"Perfumes": "Parfum", "Skincare": "Hautpflege", "Makeup": "Make-up", "Haircare": "Haarpflege"},
    },
    "es": {
        "name": "Spanish",
        "dir": "content/es/maquillaje",
        "categories": {"Perfumes": "Perfumes", "Skincare": "Cuidado de Piel", "Makeup": "Maquillaje", "Haircare": "Cabello"},
    },
    "zh": {
        "name": "Chinese",
        "dir": "content/zh/makeup",
        "categories": {"Perfumes": "香水", "Skincare": "护肤", "Makeup": "彩妆", "Haircare": "护发"},
    },
}

def clean_frontmatter(content):
    """Remove duplicate YAML keys in frontmatter"""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    fm_lines = parts[1].strip().split("\n")
    seen = {}
    cleaned = []
    skip_indent = False
    for line in fm_lines:
        if line and not line[0].isspace() and ":" in line:
            key = line.split(":")[0].strip()
            if key in seen:
                skip_indent = True
                continue
            seen[key] = True
            skip_indent = False
        elif skip_indent and line and line[0].isspace():
            continue
        else:
            skip_indent = False
        cleaned.append(line)
    return "---\n" + "\n".join(cleaned) + "\n---" + parts[2]

def fix_yaml_quotes(content):
    """Ensure tags and keywords have quoted values"""
    def quote_inline_array(match):
        key = match.group(1)
        values = match.group(2)
        items = [i.strip() for i in values.split(',')]
        quoted = ', '.join(
            f'"{i.strip().strip(chr(34))}"' for i in items
        )
        return f"{key}: [{quoted}]"
    content = re.sub(r"^(tags): \[([^\]]+)\]", quote_inline_array, content, flags=re.MULTILINE)
    content = re.sub(r"^(keywords): \[([^\]]+)\]", quote_inline_array, content, flags=re.MULTILINE)
    return content

def call_api(prompt, max_tokens=12000):
    payload = json.dumps({
        "model": "claude-sonnet-4-5-20250929",
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
    text = data["content"][0]["text"].strip()
    if text.startswith("```"): text = text.split("\n", 1)[1]
    if text.endswith("```"): text = text.rsplit("```", 1)[0].strip()
    usage = data.get("usage", {})
    return text, usage

for lang, info in LANGS.items():
    if lang == "fr": continue  # already done
    print(f"\n{'='*60}")
    print(f"[TRANSLATE] Fenty → {info['name']} ({lang})")
    print(f"{'='*60}")
    
    start = time.time()
    
    # Build prompt from translate brief
    prompt = TRANSLATE_BRIEF
    prompt = prompt.replace("{target_language}", info["name"])
    prompt = prompt.replace("{perfumes_cat}", info["categories"]["Perfumes"])
    prompt = prompt.replace("{skincare_cat}", info["categories"]["Skincare"])
    prompt = prompt.replace("{makeup_cat}", info["categories"]["Makeup"])
    prompt = prompt.replace("{haircare_cat}", info["categories"]["Haircare"])
    
    # Append the source article
    prompt += f"\n\n=== ENGLISH SOURCE ARTICLE ===\n{EN_CONTENT}"
    
    try:
        text, usage = call_api(prompt)
        elapsed = time.time() - start
        
        # Clean up
        if not text.startswith("---"):
            text = "---\n" + text
        text = clean_frontmatter(text)
        text = fix_yaml_quotes(text)
        
        # Verify translationKey preserved
        key = "fenty-beauty-pro-filtr-soft-matte-longwear-foundation"
        if f'translationKey: "{key}"' not in text and f"translationKey: '{key}'" not in text:
            # Insert it
            text = text.replace("---\n", f'---\ntranslationKey: "{key}"\n', 1)
            print(f"  ⚠️  translationKey was missing, re-inserted")
        
        # Extract slug for filename
        slug_match = re.search(r'slug:\s*["\']?([^"\'"\n]+)', text)
        if slug_match:
            filename = slug_match.group(1).strip() + ".md"
        else:
            filename = f"fenty-beauty-pro-filtr-{lang}.md"
        
        # Save
        os.makedirs(info["dir"], exist_ok=True)
        target = os.path.join(info["dir"], filename)
        with open(target, "w", encoding="utf-8") as f:
            f.write(text)
        
        # Stats
        parts = text.split("---", 2)
        body = parts[2] if len(parts) >= 3 else ""
        words = len(body.split())
        h2 = body.count("\n## ")
        h3 = body.count("\n### ")
        
        print(f"  ✅ {elapsed:.1f}s | Words: {words} | H2: {h2} | H3: {h3}")
        print(f"     Tokens: {usage.get('input_tokens','?')} in / {usage.get('output_tokens','?')} out")
        print(f"     Saved: {target}")
        
        # Check tags quoting
        if re.search(r'^tags: \[[^\]]*[^"]\w', text, re.MULTILINE):
            print(f"  ⚠️  Unquoted tags detected (auto-fixed)")
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ Error after {elapsed:.1f}s: {e}")

print(f"\n{'='*60}")
print("DONE")
print(f"{'='*60}")
