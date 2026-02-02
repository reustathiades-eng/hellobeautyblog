#!/usr/bin/env python3
import json, os, subprocess, time, sys

os.chdir("/home/ubuntu/hbb")
API_KEY = open(".secrets").read().strip()

LANGS = [
    ("en","English"),("fr","French"),("de","German"),("es","Spanish"),
    ("it","Italian"),("pt","Portuguese"),("nl","Dutch"),("pl","Polish"),
    ("tr","Turkish"),("ja","Japanese"),("ko","Korean"),("zh","Chinese"),
    ("ar","Arabic"),("hi","Hindi")
]

AUTHORS = [
    {
        "slug": "sophie-laurent",
        "name": "Sophie Laurent",
        "role": "Perfume Expert",
        "spec": "perfumes",
        "start": 2014,
        "bg": "French, Paris/Grasse. ISIPCA graduate. Trained with master perfumers. Evaluator at Guerlain. Expert: raw materials, olfactory families, niche/designer fragrances, fragrance history, seasonal scents, perfume layering."
    },
    {
        "slug": "emma-chen",
        "name": "Emma Chen",
        "role": "Skincare Specialist",
        "spec": "skincare",
        "start": 2016,
        "bg": "Korean-American, Seoul then NYC. MSc Cosmetic Science. Society of Cosmetic Chemists certified. R&D at K-beauty brand. Expert: ingredients science, skin barrier, anti-aging, K-beauty, sensitive skin, SPF, clean beauty."
    },
    {
        "slug": "isabella-romano",
        "name": "Isabella Romano",
        "role": "Makeup Artist",
        "spec": "makeup",
        "start": 2011,
        "bg": "Italian, Milan. Accademia del Lusso graduate. 15yr pro MUA. Backstage Milan/Paris Fashion Weeks. Italian fashion magazines. Expert: color theory, bridal, editorial/runway, contouring, clean beauty makeup, inclusive shades."
    },
    {
        "slug": "olivia-taylor",
        "name": "Olivia Taylor",
        "role": "Haircare Expert",
        "spec": "haircare",
        "start": 2015,
        "bg": "British, London. IAT Certified Trichologist. Vidal Sassoon Academy graduate. Consulted for pro haircare brands. Expert: scalp health, curly hair CGM, hair repair, color care, clean formulations, heat styling."
    }
]

done = 0
errors = 0

for author in AUTHORS:
    slug = author["slug"]
    for lang, lname in LANGS:
        target = f"content/{lang}/authors/{slug}.md"
        if os.path.exists(target) and os.path.getsize(target) > 1500:
            print(f"[SKIP] {slug}/{lang}")
            done += 1
            continue

        print(f"[GEN] {slug}/{lang} ({lname})...", flush=True)

        prompt = f"""Write a complete author bio page for hellobeautyblog.com in {lname}.

AUTHOR: {author['name']} | ROLE: {author['role']} | SPECIALTY: {author['spec']}
BACKGROUND: {author['bg']}

Return ONLY this structure (no code fences, no explanation):

---
title: "{author['name']}"
translationKey: "{slug}"
role: "[role translated to {lname}]"
image: "/images/authors/{slug}.webp"
specialty: "{author['spec']}"
career_start: {author['start']}
authorSlug: "{slug}"
tagline: "[compelling one-line tagline in {lname}, ~15 words]"
specialties:
  - "[specialty 1 in {lname}]"
  - "[specialty 2]"
  - "[specialty 3]"
  - "[specialty 4]"
  - "[specialty 5]"
  - "[specialty 6]"
credentials:
  - "[credential 1 in {lname}]"
  - "[credential 2]"
  - "[credential 3]"
  - "[credential 4]"
---

## [Engaging H2 title in {lname}]

[3-4 paragraphs, 400-500 words, warm personal SEO-optimized bio in {lname}. Mention hellobeautyblog.com naturally. Use {author['spec']} keywords for SEO. No AI-sounding phrases like 'delve into' or 'it is worth noting'.]

## [Philosophy/approach H2 in {lname}]

[1-2 paragraphs, 150-200 words about their approach to {author['spec']}]"""

        payload = json.dumps({
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        })

        import urllib.request
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload.encode(),
            headers={
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            text = data["content"][0]["text"].strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0].strip()

            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            done += 1
            size = os.path.getsize(target)
            print(f"  ✅ {slug}/{lang} ({size}B) done:{done}", flush=True)
        except Exception as e:
            print(f"  ❌ {slug}/{lang}: {e}", flush=True)
            errors += 1

        time.sleep(3)

print(f"\n=== DONE: {done} ok, {errors} errors ===", flush=True)

# Git commit
os.system('cd /home/ubuntu/hbb && git add content/*/authors/ && git commit -m "feat: complete SEO author bios 4x14 langs" && git push origin main')
print("=== PUSHED ===")
