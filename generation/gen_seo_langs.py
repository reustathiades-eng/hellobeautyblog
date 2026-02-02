#!/usr/bin/env python3
import json
import subprocess
import time
import os

API_KEY = open('/home/ubuntu/hbb/.secrets').read().strip()
DATA_DIR = '/home/ubuntu/hbb/data/categories'

LANGS = [
    ("de", "German", "parfum", "hautpflege", "make-up", "haarpflege"),
    ("es", "Spanish", "perfumes", "cuidado-piel", "maquillaje", "cabello"),
    ("it", "Italian", "profumi", "skincare", "trucco", "capelli"),
    ("pt", "Portuguese", "perfumes", "skincare", "maquiagem", "cabelos"),
    ("nl", "Dutch", "parfum", "huidverzorging", "make-up", "haarverzorging"),
    ("pl", "Polish", "perfumy", "pielegnacja", "makijaz", "wlosy"),
    ("tr", "Turkish", "parfum", "cilt-bakimi", "makyaj", "sac-bakimi"),
]

def call_api(prompt):
    cmd = [
        'curl', '-s', 'https://api.anthropic.com/v1/messages',
        '-H', 'Content-Type: application/json',
        '-H', f'x-api-key: {API_KEY}',
        '-H', 'anthropic-version: 2023-06-01',
        '-d', json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        })
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    response = json.loads(result.stdout)
    text = response['content'][0]['text']
    # Clean markdown
    if text.startswith('```'):
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    return json.loads(text.strip())

def generate_perfumes(lang, lang_name, slug):
    prompt = f"""Generate {lang_name} SEO for PERFUMES category. Return ONLY valid JSON:
{{"intro_title":"8 words in {lang_name}","intro":"40 words in {lang_name}","subcategories":{{"gender":{{"title":"translated","items":[{{"name":"Women trans","emoji":"👩","url":"/{lang}/{slug}/?filter=women"}},{{"name":"Men trans","emoji":"👨","url":"/{lang}/{slug}/?filter=men"}},{{"name":"Unisex trans","emoji":"⚧️","url":"/{lang}/{slug}/?filter=unisex"}}]}},"family":{{"title":"translated","items":[{{"name":"Floral trans","emoji":"🌸","url":"/{lang}/{slug}/?family=floral"}},{{"name":"Oriental trans","emoji":"🌙","url":"/{lang}/{slug}/?family=oriental"}},{{"name":"Woody trans","emoji":"🌲","url":"/{lang}/{slug}/?family=woody"}},{{"name":"Fresh trans","emoji":"🍃","url":"/{lang}/{slug}/?family=fresh"}}]}},"occasion":{{"title":"translated","items":[{{"name":"Everyday trans","emoji":"☀️","url":"/{lang}/{slug}/?occasion=everyday"}},{{"name":"Evening trans","emoji":"🌃","url":"/{lang}/{slug}/?occasion=evening"}},{{"name":"Summer trans","emoji":"🏖️","url":"/{lang}/{slug}/?occasion=summer"}},{{"name":"Winter trans","emoji":"❄️","url":"/{lang}/{slug}/?occasion=winter"}}]}}}},"faq":[{{"question":"Q1 in {lang_name}","answer":"A1 in {lang_name}"}},{{"question":"Q2 in {lang_name}","answer":"A2 in {lang_name}"}},{{"question":"Q3 in {lang_name}","answer":"A3 in {lang_name}"}}],"seo_title":"in {lang_name}","seo_bottom":"40 words in {lang_name}"}}"""
    return call_api(prompt)

# Main
for lang, lang_name, perf_slug, skin_slug, make_slug, hair_slug in LANGS:
    print(f"\n=== {lang} ({lang_name}) ===")
    
    # Perfumes
    print(f"  Generating perfumes...", end=" ", flush=True)
    try:
        with open(f'{DATA_DIR}/perfumes.json', 'r') as f:
            data = json.load(f)
        if lang not in data:
            data[lang] = generate_perfumes(lang, lang_name, perf_slug)
            with open(f'{DATA_DIR}/perfumes.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("OK")
        else:
            print("exists")
        time.sleep(2)
    except Exception as e:
        print(f"ERROR: {e}")

print("\nDone!")
