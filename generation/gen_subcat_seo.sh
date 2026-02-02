#!/bin/bash
# ============================================================
# HelloBeautyBlog — Subcategory SEO Content Generator
# Generates intro, FAQ, SEO bottom for all perfume subcategories
# across 14 languages via Claude API
# ============================================================
# Usage:
#   ./gen_subcat_seo.sh                  # Full run (all types, all langs)
#   ./gen_subcat_seo.sh test             # Test mode (1 subcat, EN only)
#   ./gen_subcat_seo.sh gender           # Single type, all langs
#   ./gen_subcat_seo.sh gender en        # Single type, single lang
#   ./gen_subcat_seo.sh status           # Show progress
#   ./gen_subcat_seo.sh resume           # Resume from where it stopped
# ============================================================

set -euo pipefail

# --- CONFIG ---
HBB_DIR="/home/ubuntu/hbb"
API_KEY=$(cat "$HBB_DIR/.secrets" | tr -d '[:space:]')
MODEL="claude-sonnet-4-20250514"
MAX_TOKENS=1500
OUTPUT_DIR="$HBB_DIR/data/subcategories"
LOG_FILE="/tmp/gen_subcat_seo.log"
PROGRESS_FILE="/tmp/gen_subcat_progress.txt"
ERRORS_FILE="/tmp/gen_subcat_errors.txt"
RATE_LIMIT_DELAY=4  # seconds between API calls
MAX_RETRIES=3

# --- LANGUAGES ---
declare -A LANG_NAMES=(
    [en]="English" [fr]="French" [de]="German" [es]="Spanish"
    [pt]="Portuguese" [it]="Italian" [nl]="Dutch" [pl]="Polish"
    [tr]="Turkish" [ar]="Arabic" [zh]="Chinese Simplified"
    [ja]="Japanese" [ko]="Korean" [hi]="Hindi"
)
LANGS=(en fr de es pt it nl pl tr ar zh ja ko hi)

# --- SUBCATEGORIES DEFINITION ---
# Format: type|value|display_name
GENDER_SUBCATS=(
    "Women|Women's Perfumes"
    "Men|Men's Perfumes"
    "Unisex|Unisex Perfumes"
)

FAMILY_SUBCATS=(
    "floral|Floral Perfumes"
    "oriental|Oriental Perfumes"
    "woody|Woody Perfumes"
    "fresh|Fresh Perfumes"
    "gourmand|Gourmand Perfumes"
    "aromatic|Aromatic Perfumes"
    "chypre|Chypre Perfumes"
)

OCCASION_SUBCATS=(
    "Evening|Evening Perfumes"
    "Everyday|Everyday Perfumes"
    "Office|Office Perfumes"
    "Romantic|Romantic Perfumes"
    "Sport|Sport Perfumes"
    "Summer|Summer Perfumes"
    "Travel|Travel Perfumes"
    "Wedding|Wedding Perfumes"
    "Winter|Winter Perfumes"
)

SUBFAMILY_SUBCATS=(
    "aromatic-fougere|Aromatic Fougère"
    "aromatic-herbal|Aromatic Herbal"
    "aromatic-marine|Aromatic Marine"
    "aromatic-spicy|Aromatic Spicy"
    "chypre-floral|Chypre Floral"
    "chypre-fruity|Chypre Fruity"
    "chypre-green|Chypre Green"
    "chypre-leather|Chypre Leather"
    "floral-aldehyde|Floral Aldehyde"
    "floral-aquatic|Floral Aquatic"
    "floral-fruity|Floral Fruity"
    "floral-green|Floral Green"
    "floral-powdery|Floral Powdery"
    "floral-white|White Floral"
    "fresh-aquatic|Fresh Aquatic"
    "fresh-citrus|Fresh Citrus"
    "fresh-fruity|Fresh Fruity"
    "fresh-green|Fresh Green"
    "fresh-ozonic|Fresh Ozonic"
    "gourmand-chocolate|Gourmand Chocolate"
    "gourmand-coffee|Gourmand Coffee"
    "gourmand-sweet|Gourmand Sweet"
    "gourmand-vanilla|Gourmand Vanilla"
    "oriental-amber|Oriental Amber"
    "oriental-floral|Oriental Floral"
    "oriental-spicy|Oriental Spicy"
    "oriental-vanilla|Oriental Vanilla"
    "oriental-woody|Oriental Woody"
    "woody-aromatic|Woody Aromatic"
    "woody-dry|Woody Dry"
    "woody-earthy|Woody Earthy"
    "woody-mossy|Woody Mossy"
    "woody-spicy|Woody Spicy"
)

# --- FUNCTIONS ---

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

is_done() {
    local key="$1"
    grep -qF "$key" "$PROGRESS_FILE" 2>/dev/null
}

mark_done() {
    local key="$1"
    echo "$key" >> "$PROGRESS_FILE"
}

mark_error() {
    local key="$1"
    local msg="$2"
    echo "[$(date '+%H:%M:%S')] FAIL $key: $msg" >> "$ERRORS_FILE"
}

get_subcat_array() {
    local type="$1"
    case "$type" in
        gender)    echo "GENDER_SUBCATS" ;;
        family)    echo "FAMILY_SUBCATS" ;;
        occasion)  echo "OCCASION_SUBCATS" ;;
        subfamily) echo "SUBFAMILY_SUBCATS" ;;
    esac
}

build_prompt() {
    local type="$1"      # gender, family, subfamily, occasion
    local value="$2"     # e.g. "Women", "floral", "floral-fruity"
    local display="$3"   # e.g. "Women's Perfumes", "Floral Fruity"
    local langcode="$4"
    local langname="$5"

    local type_context=""
    case "$type" in
        gender)
            type_context="This is a GENDER-based subcategory page for $display. The page lists all perfumes designed for the ${value} audience."
            ;;
        family)
            type_context="This is an OLFACTORY FAMILY subcategory page for $display. The $value family is one of the main classifications in perfumery. Explain what defines this family (key ingredients, character, mood)."
            ;;
        subfamily)
            type_context="This is a FRAGRANCE SUBFAMILY page for $display. This is a more specific sub-classification within perfumery. Explain what makes this subfamily unique, its typical notes and accords, and who it appeals to."
            ;;
        occasion)
            type_context="This is an OCCASION-based subcategory page for $display. This page groups perfumes that are ideal for ${value} occasions. Explain what makes a perfume suitable for this occasion."
            ;;
    esac

    cat << PROMPT
You are a professional SEO copywriter for Hello Beauty Blog, a luxury beauty website. Generate SEO content in ${langname} for a perfume subcategory page.

SUBCATEGORY: ${display}
TYPE: ${type} (value: ${value})
CONTEXT: ${type_context}

Return ONLY valid JSON with these exact keys:
{
  "intro_title": "An engaging title (6-10 words) in ${langname} for the intro section",
  "intro": "A compelling, informative paragraph (60-80 words) in ${langname}. Be specific about this subcategory. Include relevant perfumery terms and keywords naturally.",
  "faq": [
    {"question": "Q1 in ${langname}", "answer": "A1 (30-50 words) in ${langname}"},
    {"question": "Q2 in ${langname}", "answer": "A2 (30-50 words) in ${langname}"},
    {"question": "Q3 in ${langname}", "answer": "A3 (30-50 words) in ${langname}"}
  ],
  "seo_title": "A short title (4-8 words) in ${langname} for the bottom SEO section",
  "seo_bottom": "An SEO-optimized paragraph (50-70 words) in ${langname} about Hello Beauty Blog's expertise in this specific subcategory."
}

CRITICAL RULES:
- Return ONLY the JSON object, no markdown, no backticks, no explanation
- All text must be in ${langname}
- Content must be specific to ${display}, not generic perfume content
- FAQ questions must be relevant to this exact subcategory
- Use natural, engaging language adapted for ${langname} speakers
- Include relevant keywords for SEO without keyword stuffing
PROMPT
}

call_api() {
    local prompt="$1"
    local attempt=0
    local response=""
    local text=""

    while [ $attempt -lt $MAX_RETRIES ]; do
        attempt=$((attempt + 1))

        response=$(curl -s --max-time 60 \
            -H "Content-Type: application/json" \
            -H "x-api-key: $API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -d "$(python3 -c "
import json, sys
prompt = sys.stdin.read()
print(json.dumps({
    'model': '$MODEL',
    'max_tokens': $MAX_TOKENS,
    'messages': [{'role': 'user', 'content': prompt}]
}))
" <<< "$prompt")" \
            "https://api.anthropic.com/v1/messages" 2>/dev/null)

        # Check for rate limit
        if echo "$response" | grep -q '"type":"error"'; then
            local error_type=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error',{}).get('type',''))" 2>/dev/null)
            if [ "$error_type" = "rate_limit_error" ] || [ "$error_type" = "overloaded_error" ]; then
                local wait_time=$((attempt * 15))
                log "  Rate limited (attempt $attempt), waiting ${wait_time}s..."
                sleep $wait_time
                continue
            fi
            log "  API error: $error_type (attempt $attempt)"
            sleep 5
            continue
        fi

        # Extract text
        text=$(echo "$response" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d['content'][0]['text'])
except Exception as e:
    print('', file=sys.stderr)
" 2>/dev/null)

        if [ -n "$text" ]; then
            # Clean markdown wrappers if present
            text=$(echo "$text" | sed 's/^```json//g' | sed 's/^```//g' | sed 's/```$//g' | sed '/^$/d')
            
            # Validate JSON
            if echo "$text" | python3 -c "
import sys, json
d = json.load(sys.stdin)
required = ['intro_title', 'intro', 'faq', 'seo_title', 'seo_bottom']
for k in required:
    assert k in d, f'Missing key: {k}'
assert len(d['faq']) == 3, 'Need exactly 3 FAQ items'
for item in d['faq']:
    assert 'question' in item and 'answer' in item, 'FAQ item missing q/a'
" 2>/dev/null; then
                echo "$text"
                return 0
            else
                log "  JSON validation failed (attempt $attempt)"
            fi
        else
            log "  Empty response (attempt $attempt)"
        fi

        sleep $((attempt * 5))
    done

    return 1
}

merge_into_json() {
    local json_file="$1"
    local lang="$2"
    local value="$3"
    local content="$4"

    python3 << PYEOF
import json, os

json_file = "$json_file"
lang = "$lang"
value = '''$value'''
content = '''$content'''

# Load existing or create new
if os.path.exists(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
else:
    data = {}

# Ensure lang key exists
if lang not in data:
    data[lang] = {}

# Parse and merge content
try:
    parsed = json.loads(content)
    data[lang][value] = parsed
except json.JSONDecodeError as e:
    print(f"ERROR parsing JSON: {e}")
    exit(1)

# Write back (sorted keys for consistency)
with open(json_file, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=False)

print("OK")
PYEOF
}

process_type() {
    local type="$1"
    local filter_lang="${2:-}"  # optional: process only this lang
    
    local json_file="$OUTPUT_DIR/perfumes_${type}.json"
    local arr_name=$(get_subcat_array "$type")
    
    # Get array reference
    local -n subcats="$arr_name"
    local total=${#subcats[@]}
    local lang_count=${#LANGS[@]}
    
    if [ -n "$filter_lang" ]; then
        lang_count=1
    fi
    
    local grand_total=$((total * lang_count))
    local done_count=0
    local skip_count=0
    local fail_count=0
    
    log "=== Processing $type: $total subcats × $lang_count langs = $grand_total entries ==="
    
    for entry in "${subcats[@]}"; do
        local value="${entry%%|*}"
        local display="${entry#*|}"
        
        for lang in "${LANGS[@]}"; do
            # Apply lang filter if set
            if [ -n "$filter_lang" ] && [ "$lang" != "$filter_lang" ]; then
                continue
            fi
            
            local key="${type}|${value}|${lang}"
            
            # Skip if already done
            if is_done "$key"; then
                skip_count=$((skip_count + 1))
                continue
            fi
            
            local langname="${LANG_NAMES[$lang]}"
            log "  [$type] $value / $lang ($langname) ..."
            
            local prompt=$(build_prompt "$type" "$value" "$display" "$lang" "$langname")
            local result=$(call_api "$prompt")
            
            if [ -n "$result" ]; then
                local merge_result=$(merge_into_json "$json_file" "$lang" "$value" "$result")
                if [ "$merge_result" = "OK" ]; then
                    mark_done "$key"
                    done_count=$((done_count + 1))
                    log "  ✓ $value/$lang OK (done: $done_count, skip: $skip_count)"
                else
                    fail_count=$((fail_count + 1))
                    mark_error "$key" "merge failed"
                    log "  ✗ $value/$lang MERGE FAILED"
                fi
            else
                fail_count=$((fail_count + 1))
                mark_error "$key" "API call failed after $MAX_RETRIES retries"
                log "  ✗ $value/$lang API FAILED"
            fi
            
            sleep $RATE_LIMIT_DELAY
        done
    done
    
    log "=== $type DONE: +$done_count new, $skip_count skipped, $fail_count failed ==="
}

show_status() {
    echo "============================================"
    echo "  Subcategory SEO Generation — Status"
    echo "============================================"
    
    local total=$((3*14 + 7*14 + 33*14 + 9*14))  # 728
    local done=0
    if [ -f "$PROGRESS_FILE" ]; then
        done=$(wc -l < "$PROGRESS_FILE")
    fi
    local errors=0
    if [ -f "$ERRORS_FILE" ]; then
        errors=$(wc -l < "$ERRORS_FILE")
    fi
    local pct=0
    if [ $total -gt 0 ]; then
        pct=$((done * 100 / total))
    fi
    
    echo ""
    echo "  Progress: $done / $total ($pct%)"
    echo "  Errors:   $errors"
    echo ""
    
    # Per type breakdown
    for type in gender family subfamily occasion; do
        local type_done=$(grep -c "^${type}|" "$PROGRESS_FILE" 2>/dev/null || echo 0)
        local type_total=0
        case $type in
            gender) type_total=$((3*14)) ;;
            family) type_total=$((7*14)) ;;
            subfamily) type_total=$((33*14)) ;;
            occasion) type_total=$((9*14)) ;;
        esac
        printf "  %-12s %3d / %3d\n" "$type:" "$type_done" "$type_total"
    done
    
    echo ""
    
    # JSON file sizes
    echo "  JSON files:"
    for type in gender family subfamily occasion; do
        local f="$OUTPUT_DIR/perfumes_${type}.json"
        if [ -f "$f" ]; then
            local size=$(du -h "$f" | cut -f1)
            local langs=$(python3 -c "import json; d=json.load(open('$f')); print(len(d))" 2>/dev/null || echo "?")
            printf "    perfumes_%-12s %6s  (%s langs)\n" "${type}.json" "$size" "$langs"
        else
            printf "    perfumes_%-12s (not created yet)\n" "${type}.json"
        fi
    done
    
    echo ""
    
    if [ -f "$ERRORS_FILE" ] && [ -s "$ERRORS_FILE" ]; then
        echo "  Last 5 errors:"
        tail -5 "$ERRORS_FILE" | sed 's/^/    /'
    fi
    
    echo "============================================"
}

# --- MAIN ---

mkdir -p "$OUTPUT_DIR"
touch "$PROGRESS_FILE" "$ERRORS_FILE"

case "${1:-full}" in
    test)
        log "========== TEST MODE =========="
        log "Generating 1 subcategory (gender/Women/en) to verify..."
        
        prompt=$(build_prompt "gender" "Women" "Women's Perfumes" "en" "English")
        log "Prompt length: $(echo "$prompt" | wc -c) chars"
        
        result=$(call_api "$prompt")
        if [ -n "$result" ]; then
            log "✓ API call successful"
            log "Response:"
            echo "$result" | python3 -m json.tool 2>/dev/null | tee -a "$LOG_FILE"
            
            # Save to file
            merge_result=$(merge_into_json "$OUTPUT_DIR/perfumes_gender.json" "en" "Women" "$result")
            log "Merge result: $merge_result"
            
            log ""
            log "Test file: $OUTPUT_DIR/perfumes_gender.json"
            log "========== TEST COMPLETE =========="
        else
            log "✗ API call FAILED"
            log "Check $LOG_FILE for details"
            exit 1
        fi
        ;;
    
    status)
        show_status
        ;;
    
    resume|full)
        log "=========================================="
        log "  FULL GENERATION RUN ($(date))"
        log "  Mode: ${1:-full}"
        log "=========================================="
        
        START_TIME=$(date +%s)
        
        for type in gender family occasion subfamily; do
            process_type "$type"
        done
        
        END_TIME=$(date +%s)
        ELAPSED=$(( (END_TIME - START_TIME) / 60 ))
        
        log ""
        log "=========================================="
        log "  GENERATION COMPLETE in ${ELAPSED} minutes"
        log "=========================================="
        show_status
        
        # Auto-commit if we generated anything new
        cd "$HBB_DIR"
        if git diff --quiet data/subcategories/ 2>/dev/null; then
            log "No changes to commit"
        else
            git add data/subcategories/
            git commit -m "feat(seo): generate subcategory SEO content for perfumes"
            git push origin main
            log "✓ Committed and pushed to GitHub"
        fi
        ;;
    
    gender|family|subfamily|occasion)
        type="$1"
        filter_lang="${2:-}"
        log "=========================================="
        log "  GENERATING: $type ${filter_lang:-(all langs)}"
        log "=========================================="
        process_type "$type" "$filter_lang"
        show_status
        ;;
    
    *)
        echo "Usage: $0 [test|full|resume|status|gender|family|subfamily|occasion] [lang]"
        echo ""
        echo "Commands:"
        echo "  test               Test with 1 subcategory (Women/EN)"
        echo "  full               Full run (all 52 subcats × 14 langs)"
        echo "  resume             Resume from last progress"
        echo "  status             Show current progress"
        echo "  gender [lang]      Generate gender subcategories"
        echo "  family [lang]      Generate family subcategories"
        echo "  subfamily [lang]   Generate subfamily subcategories"
        echo "  occasion [lang]    Generate occasion subcategories"
        exit 0
        ;;
esac
