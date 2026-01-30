#!/bin/bash
#
# SCRIPT DE GÉNÉRATION DE FICHES PARFUMS - HelloBeautyBlog
# Version: 2.0
# 
# Ce script génère des fiches parfums complètes dans toutes les langues
# en séparant le front matter YAML (fixe) du contenu (généré par API)
#
# Usage: ./generate_perfume.sh <perfume_slug> [langue]
#        ./generate_perfume.sh boss-alive          # Toutes les langues
#        ./generate_perfume.sh boss-alive fr       # Français uniquement
#

set -e

# ============================================
# CONFIGURATION
# ============================================
API_KEY="${ANTHROPIC_API_KEY:-}"

if [ -z "$API_KEY" ]; then
    error "ANTHROPIC_API_KEY not set. Export it or add to .env file"
fi
MODEL="claude-sonnet-4-5-20250929"
BASE_DIR="/home/ubuntu/hbb"
GEN_DIR="$BASE_DIR/generation"
CONTENT_DIR="$BASE_DIR/content"

# Langues supportées
LANGUAGES=("en" "fr" "de" "es" "it" "pt" "nl" "pl" "tr" "ja" "ko" "zh" "ar" "hi")

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

error() {
    echo "[ERROR] $1" >&2
    exit 1
}

# ============================================
# FONCTION: Générer le front matter YAML
# ============================================
generate_frontmatter() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local DATA_FILE="$GEN_DIR/data/${PERFUME_SLUG}.json"
    
    if [ ! -f "$DATA_FILE" ]; then
        error "Fichier de données non trouvé: $DATA_FILE"
    fi
    
    # Lire les données du parfum
    local BRAND=$(jq -r '.brand' $DATA_FILE)
    local PRODUCT_NAME=$(jq -r '.productName' $DATA_FILE)
    local CONCENTRATION=$(jq -r '.concentration' $DATA_FILE)
    local PRICE=$(jq -r '.price' $DATA_FILE)
    local RATING=$(jq -r '.rating' $DATA_FILE)
    local LONGEVITY_MIN=$(jq -r '.longevity.min' $DATA_FILE)
    local LONGEVITY_MAX=$(jq -r '.longevity.max' $DATA_FILE)
    local SILLAGE_KEY=$(jq -r '.sillage' $DATA_FILE)
    local GENDER_KEY=$(jq -r '.gender' $DATA_FILE)
    
    # Charger les traductions
    local TRANS_FILE="$GEN_DIR/translations/perfume_translations.json"
    local NOTES_FILE="$GEN_DIR/translations/notes_translations.json"
    
    # Obtenir les traductions pour cette langue
    local LONGEVITY_UNIT=$(jq -r ".languages.${LANG}.characteristics.longevity_unit" $TRANS_FILE)
    local SILLAGE=$(jq -r ".languages.${LANG}.characteristics.sillage.${SILLAGE_KEY}" $TRANS_FILE)
    local GENDER=$(jq -r ".languages.${LANG}.gender.${GENDER_KEY}" $TRANS_FILE)
    local CATEGORY=$(jq -r ".languages.${LANG}.categories[0]" $TRANS_FILE)
    
    # Traduire les notes
    local TOP_NOTES=""
    for note in $(jq -r '.topNotes[]' $DATA_FILE); do
        local translated=$(jq -r ".notes.${note}.${LANG}" $NOTES_FILE)
        TOP_NOTES="$TOP_NOTES  - \"$translated\"\n"
    done
    
    local HEART_NOTES=""
    for note in $(jq -r '.heartNotes[]' $DATA_FILE); do
        local translated=$(jq -r ".notes.${note}.${LANG}" $NOTES_FILE)
        HEART_NOTES="$HEART_NOTES  - \"$translated\"\n"
    done
    
    local BASE_NOTES=""
    for note in $(jq -r '.baseNotes[]' $DATA_FILE); do
        local translated=$(jq -r ".notes.${note}.${LANG}" $NOTES_FILE)
        BASE_NOTES="$BASE_NOTES  - \"$translated\"\n"
    done
    
    # Traduire les saisons
    local SEASONS=""
    for season in $(jq -r '.seasons[]' $DATA_FILE); do
        local translated=$(jq -r ".languages.${LANG}.seasons.${season}" $TRANS_FILE)
        SEASONS="$SEASONS  - \"$translated\"\n"
    done
    
    # Traduire les occasions
    local OCCASIONS=""
    for occasion in $(jq -r '.occasions[]' $DATA_FILE); do
        local translated=$(jq -r ".languages.${LANG}.occasions.${occasion}" $TRANS_FILE)
        OCCASIONS="$OCCASIONS  - \"$translated\"\n"
    done
    
    # Obtenir titre et description traduits
    local TITLE=$(jq -r ".titles.${LANG}" $DATA_FILE)
    local DESCRIPTION=$(jq -r ".descriptions.${LANG}" $DATA_FILE)
    local TAGS=$(jq -r ".tags.${LANG} | @json" $DATA_FILE)
    local KEYWORDS=$(jq -r ".keywords.${LANG} | @json" $DATA_FILE)
    
    # Images
    local IMAGES=""
    for img in $(jq -r '.images[]' $DATA_FILE); do
        IMAGES="$IMAGES  - $img\n"
    done
    
    # Générer le YAML
    cat << YAML
---
title: "$TITLE"
slug: "$PERFUME_SLUG"
description: "$DESCRIPTION"
date: $(jq -r '.date' $DATA_FILE)
lastmod: $(date '+%Y-%m-%d')
author: "Emma Collins"
authorSlug: "emma-collins"
categories:
  - "$CATEGORY"
tags: $TAGS
keywords: $KEYWORDS
images:
$(echo -e "$IMAGES")
featured: $(jq -r '.featured' $DATA_FILE)
draft: false
brand: "$BRAND"
productName: "$PRODUCT_NAME"
concentration: "$CONCENTRATION"
gender: "$GENDER"
price: "$PRICE"
rating: $RATING
topNotes:
$(echo -e "$TOP_NOTES")
heartNotes:
$(echo -e "$HEART_NOTES")
baseNotes:
$(echo -e "$BASE_NOTES")
longevity: "${LONGEVITY_MIN}-${LONGEVITY_MAX} ${LONGEVITY_UNIT}"
sillage: "$SILLAGE"
season:
$(echo -e "$SEASONS")
occasion:
$(echo -e "$OCCASIONS")
translationKey: "$PERFUME_SLUG"
---
YAML
}

# ============================================
# FONCTION: Générer le contenu via API
# ============================================
generate_content() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local DATA_FILE="$GEN_DIR/data/${PERFUME_SLUG}.json"
    local BRIEF_FILE="$GEN_DIR/templates/CONTENT_GENERATION_BRIEF.md"
    
    # Obtenir le nom de la langue
    local TRANS_FILE="$GEN_DIR/translations/perfume_translations.json"
    local LANG_NAME=$(jq -r ".languages.${LANG}.name" $TRANS_FILE)
    
    # Lire les données du parfum
    local BRAND=$(jq -r '.brand' $DATA_FILE)
    local PRODUCT_NAME=$(jq -r '.productName' $DATA_FILE)
    local YEAR=$(jq -r '.launchYear' $DATA_FILE)
    local PERFUMER=$(jq -r '.perfumer' $DATA_FILE)
    local FAMILY=$(jq -r '.family' $DATA_FILE)
    local KEY_MESSAGE=$(jq -r '.keyMessage' $DATA_FILE)
    
    # Construire le prompt
    local PROMPT="You are Emma Collins, a professional perfume reviewer for HelloBeautyBlog.com.

CRITICAL INSTRUCTIONS - READ CAREFULLY:

1. Write ONLY the article content in ${LANG_NAME}. 
2. DO NOT include any YAML front matter (no ---).
3. Start directly with the article text.
4. Follow the writing brief below EXACTLY.

WRITING BRIEF:
$(cat $BRIEF_FILE)

PERFUME INFORMATION:
- Brand: ${BRAND}
- Product: ${PRODUCT_NAME}
- Launch Year: ${YEAR}
- Perfumer: ${PERFUMER}
- Fragrance Family: ${FAMILY}
- Key Message: ${KEY_MESSAGE}

PERFUME DATA (use for accurate information):
$(jq '.' $DATA_FILE)

IMPORTANT REMINDERS:
- Write 900-1100 words
- Use natural ${LANG_NAME} expressions and idioms
- Include personal anecdotes
- Vary sentence length
- Avoid AI-detectable phrases
- Express genuine opinions (including minor criticisms)

OUTPUT: Raw article text only. No YAML. No code blocks. Start with the first paragraph."

    # Appel API
    local RESPONSE=$(curl -s --max-time 180 https://api.anthropic.com/v1/messages \
        -H "Content-Type: application/json" \
        -H "x-api-key: $API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d "$(jq -n \
            --arg prompt "$PROMPT" \
            '{
                "model": "'"$MODEL"'",
                "max_tokens": 4096,
                "temperature": 0.85,
                "messages": [{"role": "user", "content": $prompt}]
            }')")
    
    # Extraire le contenu
    local CONTENT=$(echo "$RESPONSE" | jq -r '.content[0].text // empty')
    
    if [ -z "$CONTENT" ]; then
        log "❌ Erreur API pour $LANG"
        echo "$RESPONSE" | jq -r '.error.message // "Unknown error"'
        return 1
    fi
    
    # Nettoyer le contenu (supprimer d'éventuels --- au début)
    CONTENT=$(echo "$CONTENT" | sed '/^---$/d' | sed '/^```/d')
    
    echo "$CONTENT"
}

# ============================================
# FONCTION: Assembler et sauvegarder le fichier
# ============================================
assemble_file() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local OUTPUT_DIR="$CONTENT_DIR/$LANG/perfumes"
    local OUTPUT_FILE="$OUTPUT_DIR/${PERFUME_SLUG}.md"
    
    # Créer le dossier si nécessaire
    mkdir -p "$OUTPUT_DIR"
    
    log "🔄 Génération $PERFUME_SLUG ($LANG)..."
    
    # Générer le front matter
    local FRONTMATTER=$(generate_frontmatter "$PERFUME_SLUG" "$LANG")
    
    # Générer le contenu
    local CONTENT=$(generate_content "$PERFUME_SLUG" "$LANG")
    
    if [ $? -ne 0 ]; then
        log "❌ Échec génération contenu $LANG"
        return 1
    fi
    
    # Assembler le fichier
    echo "$FRONTMATTER" > "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "$CONTENT" >> "$OUTPUT_FILE"
    
    # Vérifier le fichier
    local SIZE=$(wc -c < "$OUTPUT_FILE")
    if [ $SIZE -lt 3000 ]; then
        log "⚠️  Fichier trop petit ($SIZE bytes) - vérifier $OUTPUT_FILE"
        return 1
    fi
    
    log "✅ $PERFUME_SLUG ($LANG) - $SIZE bytes"
    return 0
}

# ============================================
# FONCTION: Valider un fichier généré
# ============================================
validate_file() {
    local FILE=$1
    local ERRORS=0
    
    # Vérifier que le fichier existe
    [ ! -f "$FILE" ] && return 1
    
    # Vérifier les champs obligatoires
    grep -q "^brand:" "$FILE" || ((ERRORS++))
    grep -q "^rating:" "$FILE" || ((ERRORS++))
    grep -q "^translationKey:" "$FILE" || ((ERRORS++))
    grep -qA1 "^topNotes:" "$FILE" | grep -q "^\s*-" || ((ERRORS++))
    grep -qA1 "^season:" "$FILE" | grep -q "^\s*-" || ((ERRORS++))
    grep -qA1 "^occasion:" "$FILE" | grep -q "^\s*-" || ((ERRORS++))
    
    return $ERRORS
}

# ============================================
# MAIN
# ============================================
main() {
    local PERFUME_SLUG=$1
    local TARGET_LANG=$2
    
    if [ -z "$PERFUME_SLUG" ]; then
        error "Usage: $0 <perfume_slug> [langue]"
    fi
    
    log "=========================================="
    log "GÉNÉRATION: $PERFUME_SLUG"
    log "=========================================="
    
    # Déterminer les langues à générer
    local LANGS_TO_GENERATE=()
    if [ -n "$TARGET_LANG" ]; then
        LANGS_TO_GENERATE=("$TARGET_LANG")
    else
        LANGS_TO_GENERATE=("${LANGUAGES[@]}")
    fi
    
    # Compteurs
    local SUCCESS=0
    local FAILED=0
    
    # Générer pour chaque langue
    for lang in "${LANGS_TO_GENERATE[@]}"; do
        if assemble_file "$PERFUME_SLUG" "$lang"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
        
        # Pause entre les appels API
        [ ${#LANGS_TO_GENERATE[@]} -gt 1 ] && sleep 2
    done
    
    log ""
    log "=========================================="
    log "RÉSUMÉ: $SUCCESS succès, $FAILED échecs"
    log "=========================================="
    
    # Validation finale
    log ""
    log "VALIDATION DES FICHIERS:"
    for lang in "${LANGS_TO_GENERATE[@]}"; do
        local file="$CONTENT_DIR/$lang/perfumes/${PERFUME_SLUG}.md"
        if validate_file "$file"; then
            echo "  ✅ $lang"
        else
            echo "  ❌ $lang - ERREURS DÉTECTÉES"
        fi
    done
}

# Exécuter
main "$@"
