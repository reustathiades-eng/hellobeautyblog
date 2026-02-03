#!/usr/bin/env python3
"""Test generation: 1 product per category in EN only"""
import json, os, sys, time, re

os.chdir("/home/ubuntu/hbb")
API_KEY = open(".secrets").read().strip()

PRODUCTS = [
    {
        "category": "perfumes",
        "brand": "Tom Ford",
        "name": "Black Orchid",
        "slug": "tom-ford-black-orchid",
        "gender": "Unisex",
        "subcategories": ["Unisex", "oriental", "Romantic", "Winter", "Evening", "oriental-spicy"]
    },
    {
        "category": "skincare",
        "brand": "The Ordinary",
        "name": "Niacinamide 10% + Zinc 1%",
        "slug": "the-ordinary-niacinamide-10-zinc-1",
        "subcategories": ["serum", "oily", "combination", "pores", "acne", "niacinamide", "the-ordinary"]
    },
    {
        "category": "makeup",
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Soft Matte Longwear Foundation",
        "slug": "fenty-beauty-pro-filtr-soft-matte-longwear-foundation",
        "subcategories": ["matte", "fenty-beauty", "full-coverage", "face", "foundation"]
    },
    {
        "category": "haircare",
        "brand": "Olaplex",
        "name": "No. 3 Hair Perfector",
        "slug": "olaplex-no-3-hair-perfector",
        "subcategories": ["wavy-hair", "serum", "color-protection", "straight-hair", "repair", "curly-hair", "olaplex"]
    }
]

def clean_frontmatter(content):
    """Remove duplicate YAML keys in frontmatter"""
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    
    fm_lines = parts[1].strip().split("\n")
    seen_keys = {}
    clean_lines = []
    skip_block = False
    current_key = None
    
    for line in fm_lines:
        # Check if it's a top-level key (no leading whitespace, has colon)
        if line and not line.startswith(" ") and not line.startswith("\t") and ":" in line:
            key = line.split(":")[0].strip()
            if key in seen_keys:
                # Duplicate - skip this key and any indented lines after it
                skip_block = True
                current_key = key
                continue
            else:
                seen_keys[key] = True
                skip_block = False
                current_key = key
                clean_lines.append(line)
        elif skip_block and line.startswith((" ", "\t", "  -")):
            # Indented line belonging to skipped duplicate key
            continue
        else:
            skip_block = False
            clean_lines.append(line)
    
    return "---\n" + "\n".join(clean_lines) + "\n---" + parts[2]


def fix_yaml_quotes(content):
    """Ensure tags and keywords have quoted values"""
    import re
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

def generate_article(product, max_retries=2):
    cat = product["category"]
    slug = product["slug"]
    
    with open(f"generation/prompts/{cat}.txt", "r") as f:
        prompt_template = f.read()
    
    prompt = prompt_template.replace("{brand}", product["brand"])
    prompt = prompt.replace("{name}", product["name"])
    prompt = prompt.replace("{slug}", product["slug"])
    prompt = prompt.replace("{subcategories}", json.dumps(product.get("subcategories", [])))
    if "gender" in product:
        prompt = prompt.replace("{gender}", product["gender"])
    
    print(f"\n{'='*60}")
    print(f"[GEN] {cat.upper()}: {product['brand']} - {product['name']}")
    print(f"{'='*60}")
    
    payload = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    import urllib.request
    
    for attempt in range(max_retries + 1):
        start = time.time()
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01"
                }
            )
            resp = urllib.request.urlopen(req, timeout=180)
            data = json.loads(resp.read().decode())
            elapsed = time.time() - start
            
            content = data["content"][0]["text"]
            
            # Clean code fences
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            content = content.strip()
            
            if not content.startswith("---"):
                content = "---\n" + content
            
            # Deduplicate frontmatter
            content = clean_frontmatter(content)
            content = fix_yaml_quotes(content)
            
            # Save
            output_path = f"content/en/{cat}/{slug}.md"
            with open(output_path, "w") as f:
                f.write(content)
            
            # Stats
            parts = content.split("---", 2)
            article_text = parts[2] if len(parts) >= 3 else ""
            word_count = len(article_text.split())
            h2_count = article_text.count("\n## ")
            h3_count = article_text.count("\n### ")
            has_faq = "faq" in article_text.lower() or "frequently asked" in article_text.lower()
            
            usage = data.get("usage", {})
            
            print(f"[OK] Generated in {elapsed:.1f}s (attempt {attempt+1})")
            print(f"     Words: {word_count} | H2: {h2_count} | H3: {h3_count} | FAQ: {'✅' if has_faq else '❌'}")
            print(f"     Tokens: {usage.get('input_tokens', '?')} in / {usage.get('output_tokens', '?')} out")
            print(f"     Saved: {output_path}")
            
            # Validate H3 requirement - retry if 0 H3
            if h3_count == 0 and attempt < max_retries:
                print(f"     ⚠️  No H3 headings! Auto-retrying...")
                wait = 10 * (attempt + 1)
                time.sleep(wait)
                continue
            elif h3_count == 0:
                print(f"     ⚠️  WARNING: No H3 headings after all retries!")
            
            # Check tags/keywords quoting
            import re as regex_check
            unquoted_tags = regex_check.findall(r'^tags: \[([^\]]+)\]', article_text, regex_check.MULTILINE)
            for match in unquoted_tags:
                items = [i.strip() for i in match.split(',')]
                unquoted = [i for i in items if not (i.startswith('"') and i.endswith('"'))]
                if unquoted:
                    print(f"     ⚠️  Unquoted tags detected: {unquoted[:3]}... Auto-fixing!")
                    # Auto-fix: quote all tag values
                    fixed_items = ', '.join(f'"{i.strip().strip(chr(34))}"' for i in items)
                    article_text = article_text.replace(f"tags: [{match}]", f"tags: [{fixed_items}]")
            
            unquoted_kw = regex_check.findall(r'^keywords: \[([^\]]+)\]', article_text, regex_check.MULTILINE)
            for match in unquoted_kw:
                items = [i.strip() for i in match.split(',')]
                unquoted = [i for i in items if not (i.startswith('"') and i.endswith('"'))]
                if unquoted:
                    print(f"     ⚠️  Unquoted keywords detected! Auto-fixing!")
                    fixed_items = ', '.join(f'"{i.strip().strip(chr(34))}"' for i in items)
                    article_text = article_text.replace(f"keywords: [{match}]", f"keywords: [{fixed_items}]")
            
            return True
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"[RETRY {attempt+1}/{max_retries+1}] {e} (after {elapsed:.1f}s)")
            if attempt < max_retries:
                wait = 10 * (attempt + 1)
                print(f"     Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"[FAIL] {cat}/{slug}: All retries exhausted")
                return False

results = {}
for product in PRODUCTS:
    ok = generate_article(product)
    results[product["category"]] = "✅" if ok else "❌"
    time.sleep(3)

print(f"\n{'='*60}")
print("RESULTS:")
for cat, status in results.items():
    print(f"  {status} {cat}")
print(f"{'='*60}")
