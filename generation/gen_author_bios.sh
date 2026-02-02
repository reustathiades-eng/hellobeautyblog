#!/bin/bash
set -euo pipefail
cd /home/ubuntu/hbb
API_KEY=$(cat .secrets | tr -d "\n\r ")
log() { echo "[$(date +%H:%M:%S)] $*"; }

LANGS=(en fr de es it pt nl pl tr ja ko zh ar hi)
LNAMES=(English French German Spanish Italian Portuguese Dutch Polish Turkish Japanese Korean Chinese Arabic Hindi)

SLUGS=(sophie-laurent emma-chen isabella-romano olivia-taylor)
NAMES=("Sophie Laurent" "Emma Chen" "Isabella Romano" "Olivia Taylor")
ROLES=("Perfume Expert" "Skincare Specialist" "Makeup Artist" "Haircare Expert")
SPECS=(perfumes skincare makeup haircare)
STARTS=(2014 2016 2011 2015)
BGS=(
"French, Paris/Grasse. ISIPCA graduate. Trained with master perfumers in Grasse. Evaluator at Guerlain. Expert: raw materials, olfactory families, niche/designer fragrances, fragrance history, seasonal scents, perfume layering, collection curation."
"Korean-American, Seoul then NYC. MSc Cosmetic Science Univ Cincinnati. Society of Cosmetic Chemists certified. R&D at K-beauty brand. Expert: ingredients science, skin barrier, anti-aging, K-beauty, sensitive skin, SPF, clean beauty."
"Italian, Milan. Accademia del Lusso graduate. 15yr pro MUA. Backstage Milan/Paris Fashion Weeks. Italian fashion magazines. Expert: color theory, bridal, editorial/runway, contouring, clean beauty makeup, inclusive shades."
"British, London. IAT Certified Trichologist. Vidal Sassoon Academy graduate. Consulted for pro haircare brands. Trade magazine author. Expert: scalp health, curly hair CGM, hair repair, color care, clean formulations, heat styling."
)

DONE=0; ERRORS=0
for si in 0 1 2 3; do
  slug="${SLUGS[$si]}"; name="${NAMES[$si]}"; role="${ROLES[$si]}"
  spec="${SPECS[$si]}"; start="${STARTS[$si]}"; bg="${BGS[$si]}"
  
  for li in "${!LANGS[@]}"; do
    lang="${LANGS[$li]}"; lname="${LNAMES[$li]}"
    target="content/${lang}/authors/${slug}.md"
    
    [ -f "$target" ] && [ "$(wc -c < "$target")" -gt 1500 ] && { log "SKIP $slug/$lang"; ((DONE++)); continue; }
    
    log "GEN $slug/$lang..."
    
    PROMPT="Write a complete author bio page for hellobeautyblog.com in ${lname}.

AUTHOR: $name | ROLE: $role | SPECIALTY: $spec | BACKGROUND: $bg

Return ONLY this (no code fences):

---
title: \"$name\"
translationKey: \"$slug\"
role: \"[translated role]\"
image: \"/images/authors/$slug.webp\"
specialty: \"$spec\"
career_start: $start
authorSlug: \"$slug\"
tagline: \"[compelling tagline ~15 words in $lname]\"
specialties:
  - \"[6 specialties in $lname]\"
credentials:
  - \"[4 credentials in $lname]\"
---

## [Engaging H2 in $lname]

[3-4 paragraphs, 400-500 words, warm/personal SEO bio in $lname. Mention hellobeautyblog.com. Use $spec keywords. No AI phrases.]

## [Philosophy H2 in $lname]

[1-2 paragraphs, 150-200 words, their approach to $spec]"

    JSONPAYLOAD=$(python3 -c "
import json
print(json.dumps({'model':'claude-sonnet-4-5-20250514','max_tokens':2000,'messages':[{'role':'user','content':'''$PROMPT'''}]}))
")
    
    RESP=$(curl -s --max-time 120 https://api.anthropic.com/v1/messages \
      -H "x-api-key: $API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d "$JSONPAYLOAD")

    TEXT=$(echo "$RESP" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin); t=d['content'][0]['text'].strip()
  if t.startswith('\`\`\`'): t=t.split('\n',1)[1]
  if t.endswith('\`\`\`'): t=t.rsplit('\`\`\`',1)[0]
  print(t.strip())
except Exception as e: print(f'ERR:{e}',file=sys.stderr); sys.exit(1)
" 2>/tmp/author_err.txt)

    if [ $? -ne 0 ] || [ -z "$TEXT" ]; then
      log "❌ $slug/$lang: $(cat /tmp/author_err.txt)"
      ((ERRORS++)); continue
    fi

    mkdir -p "$(dirname "$target")"
    echo "$TEXT" > "$target"
    ((DONE++))
    log "✅ $slug/$lang ($(wc -c < "$target")B) done:$DONE"
    sleep 3
  done
done

log "=== DONE: $DONE ok, $ERRORS errors ==="
cd /home/ubuntu/hbb
git add content/*/authors/
git commit -m "feat: complete SEO author bios (4x14 langs)" || true
git push origin main || true
log "=== PUSHED ==="
