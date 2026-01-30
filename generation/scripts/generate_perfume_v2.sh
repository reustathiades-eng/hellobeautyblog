#!/bin/bash
#
# SCRIPT DE GÉNÉRATION ROBUSTE V2.0 - HelloBeautyBlog
# 
# Fonctionnalités:
# - Retry automatique (3 tentatives)
# - Timeout configurable (120s)
# - Validation automatique
# - Logs détaillés
# - Mode batch (continue si erreur)
# - Vérification préalable des données
# - Rapport final
#
# Usage: 
#   ./generate_perfume_v2.sh <perfume_slug>           # Toutes les langues
#   ./generate_perfume_v2.sh <perfume_slug> fr        # Une seule langue
#   ./generate_perfume_v2.sh <perfume_slug> --dry-run # Vérification sans génération
#

set -o pipefail

# ============================================
# CONFIGURATION
# ============================================
API_KEY="${ANTHROPIC_API_KEY:-}"
MODEL="claude-sonnet-4-5-20250929"
BASE_DIR="/home/ubuntu/hbb"
GEN_DIR="$BASE_DIR/generation"
CONTENT_DIR="$BASE_DIR/content"
LOG_DIR="$GEN_DIR/logs"

# Paramètres de robustesse
MAX_RETRIES=3
TIMEOUT=120
PAUSE_BETWEEN_LANGS=3
PAUSE_BETWEEN_RETRIES=5
MIN_FILE_SIZE=3000

# Langues supportées
LANGUAGES=("en" "fr" "de" "es" "it" "pt" "nl" "pl" "tr" "ja" "ko" "zh" "ar" "hi")

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# INITIALISATION
# ============================================
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="$LOG_DIR/generation_${TIMESTAMP}.log"

# ============================================
# FONCTIONS DE LOG
# ============================================
log() {
    local MSG="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$MSG" | tee -a "$LOG_FILE"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    log "${BLUE}ℹ️  $1${NC}"
}

# ============================================
# VÉRIFICATION PRÉALABLE
# ============================================
check_prerequisites() {
    local PERFUME_SLUG=$1
    local ERRORS=0
    
    log_info "Vérification des prérequis pour $PERFUME_SLUG..."
    
    # Vérifier la clé API
    if [ -z "$API_KEY" ]; then
        log_error "ANTHROPIC_API_KEY non définie"
        echo "  → Exécutez: export ANTHROPIC_API_KEY='votre-clé'"
        ((ERRORS++))
    else
        log_success "Clé API présente"
    fi
    
    # Vérifier le fichier de données
    local DATA_FILE="$GEN_DIR/data/${PERFUME_SLUG}.json"
    if [ ! -f "$DATA_FILE" ]; then
        log_error "Fichier de données non trouvé: $DATA_FILE"
        ((ERRORS++))
    else
        log_success "Fichier de données trouvé"
        
        # Vérifier la structure JSON
        if ! jq empty "$DATA_FILE" 2>/dev/null; then
            log_error "JSON invalide dans $DATA_FILE"
            ((ERRORS++))
        else
            log_success "JSON valide"
        fi
    fi
    
    # Vérifier les fichiers de traduction
    if [ ! -f "$GEN_DIR/translations/perfume_translations.json" ]; then
        log_error "Fichier perfume_translations.json manquant"
        ((ERRORS++))
    else
        log_success "Traductions UI présentes"
    fi
    
    if [ ! -f "$GEN_DIR/translations/notes_translations.json" ]; then
        log_error "Fichier notes_translations.json manquant"
        ((ERRORS++))
    else
        log_success "Traductions notes présentes"
    fi
    
    # Vérifier que toutes les notes existent dans les traductions
    if [ -f "$DATA_FILE" ] && [ -f "$GEN_DIR/translations/notes_translations.json" ]; then
        local MISSING_NOTES=""
        for note in $(jq -r '.topNotes[], .heartNotes[], .baseNotes[]' "$DATA_FILE" 2>/dev/null); do
            if ! jq -e ".notes.\"$note\"" "$GEN_DIR/translations/notes_translations.json" >/dev/null 2>&1; then
                MISSING_NOTES="$MISSING_NOTES $note"
            fi
        done
        
        if [ -n "$MISSING_NOTES" ]; then
            log_error "Notes manquantes dans les traductions:$MISSING_NOTES"
            ((ERRORS++))
        else
            log_success "Toutes les notes sont traduites"
        fi
    fi
    
    # Vérifier le brief de génération
    if [ ! -f "$GEN_DIR/templates/CONTENT_GENERATION_BRIEF.md" ]; then
        log_error "Brief de génération manquant"
        ((ERRORS++))
    else
        log_success "Brief de génération présent"
    fi
    
    return $ERRORS
}

# ============================================
# GÉNÉRATION DU FRONT MATTER (LOCAL)
# ============================================
generate_frontmatter() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local DATA_FILE="$GEN_DIR/data/${PERFUME_SLUG}.json"
    local TRANS_FILE="$GEN_DIR/translations/perfume_translations.json"
    local NOTES_FILE="$GEN_DIR/translations/notes_translations.json"
    
    # Lire les données de base
    local BRAND=$(jq -r '.brand' "$DATA_FILE")
    local PRODUCT_NAME=$(jq -r '.productName' "$DATA_FILE")
    local CONCENTRATION=$(jq -r '.concentration' "$DATA_FILE")
    local PRICE=$(jq -r '.price' "$DATA_FILE")
    local RATING=$(jq -r '.rating' "$DATA_FILE")
    local DATE=$(jq -r '.date' "$DATA_FILE")
    local FEATURED=$(jq -r '.featured' "$DATA_FILE")
    local LONGEVITY_MIN=$(jq -r '.longevity.min' "$DATA_FILE")
    local LONGEVITY_MAX=$(jq -r '.longevity.max' "$DATA_FILE")
    local SILLAGE_KEY=$(jq -r '.sillage' "$DATA_FILE")
    local GENDER_KEY=$(jq -r '.gender' "$DATA_FILE")
    
    # Traductions
    local LONGEVITY_UNIT=$(jq -r ".languages.${LANG}.characteristics.longevity_unit" "$TRANS_FILE")
    local SILLAGE=$(jq -r ".languages.${LANG}.characteristics.sillage.${SILLAGE_KEY}" "$TRANS_FILE")
    local GENDER=$(jq -r ".languages.${LANG}.gender.${GENDER_KEY}" "$TRANS_FILE")
    local CATEGORY=$(jq -r ".languages.${LANG}.categories[0]" "$TRANS_FILE")
    
    # Titres et descriptions traduits
    local TITLE=$(jq -r ".titles.${LANG}" "$DATA_FILE")
    local DESCRIPTION=$(jq -r ".descriptions.${LANG}" "$DATA_FILE")
    
    # Tags et keywords (format JSON array)
    local TAGS=$(jq -c ".tags.${LANG}" "$DATA_FILE")
    local KEYWORDS=$(jq -c ".keywords.${LANG}" "$DATA_FILE")
    
    # Images
    local IMAGES=""
    while IFS= read -r img; do
        IMAGES="${IMAGES}  - ${img}\n"
    done < <(jq -r '.images[]' "$DATA_FILE")
    
    # Notes traduites
    local TOP_NOTES=""
    while IFS= read -r note; do
        local translated=$(jq -r ".notes.\"${note}\".${LANG}" "$NOTES_FILE")
        TOP_NOTES="${TOP_NOTES}  - \"${translated}\"\n"
    done < <(jq -r '.topNotes[]' "$DATA_FILE")
    
    local HEART_NOTES=""
    while IFS= read -r note; do
        local translated=$(jq -r ".notes.\"${note}\".${LANG}" "$NOTES_FILE")
        HEART_NOTES="${HEART_NOTES}  - \"${translated}\"\n"
    done < <(jq -r '.heartNotes[]' "$DATA_FILE")
    
    local BASE_NOTES=""
    while IFS= read -r note; do
        local translated=$(jq -r ".notes.\"${note}\".${LANG}" "$NOTES_FILE")
        BASE_NOTES="${BASE_NOTES}  - \"${translated}\"\n"
    done < <(jq -r '.baseNotes[]' "$DATA_FILE")
    
    # Saisons traduites
    local SEASONS=""
    while IFS= read -r season; do
        local translated=$(jq -r ".languages.${LANG}.seasons.${season}" "$TRANS_FILE")
        SEASONS="${SEASONS}  - \"${translated}\"\n"
    done < <(jq -r '.seasons[]' "$DATA_FILE")
    
    # Occasions traduites
    local OCCASIONS=""
    while IFS= read -r occasion; do
        local translated=$(jq -r ".languages.${LANG}.occasions.${occasion}" "$TRANS_FILE")
        OCCASIONS="${OCCASIONS}  - \"${translated}\"\n"
    done < <(jq -r '.occasions[]' "$DATA_FILE")
    
    # Générer le YAML
    cat << YAML
---
title: "$TITLE"
slug: "$PERFUME_SLUG"
description: "$DESCRIPTION"
date: $DATE
lastmod: $(date '+%Y-%m-%d')
author: "Emma Collins"
authorSlug: "emma-collins"
categories:
  - "$CATEGORY"
tags: $TAGS
keywords: $KEYWORDS
images:
$(echo -e "$IMAGES")
featured: $FEATURED
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
# GÉNÉRATION DU CONTENU (API AVEC RETRY)
# ============================================
generate_content_with_retry() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local ATTEMPT=1
    local CONTENT=""
    
    while [ $ATTEMPT -le $MAX_RETRIES ]; do
        log_info "Tentative $ATTEMPT/$MAX_RETRIES pour $LANG..."
        
        CONTENT=$(generate_content "$PERFUME_SLUG" "$LANG")
        local EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ] && [ -n "$CONTENT" ] && [ ${#CONTENT} -gt 500 ]; then
            echo "$CONTENT"
            return 0
        fi
        
        log_warning "Tentative $ATTEMPT échouée pour $LANG"
        ((ATTEMPT++))
        
        if [ $ATTEMPT -le $MAX_RETRIES ]; then
            log_info "Pause de ${PAUSE_BETWEEN_RETRIES}s avant retry..."
            sleep $PAUSE_BETWEEN_RETRIES
        fi
    done
    
    log_error "Échec après $MAX_RETRIES tentatives pour $LANG"
    return 1
}

generate_content() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local DATA_FILE="$GEN_DIR/data/${PERFUME_SLUG}.json"
    local BRIEF_FILE="$GEN_DIR/templates/CONTENT_GENERATION_BRIEF.md"
    local TRANS_FILE="$GEN_DIR/translations/perfume_translations.json"
    
    # Obtenir le nom de la langue
    local LANG_NAME=$(jq -r ".languages.${LANG}.name" "$TRANS_FILE")
    
    # Lire les données du parfum
    local BRAND=$(jq -r '.brand' "$DATA_FILE")
    local PRODUCT_NAME=$(jq -r '.productName' "$DATA_FILE")
    local YEAR=$(jq -r '.launchYear' "$DATA_FILE")
    local PERFUMER=$(jq -r '.perfumer' "$DATA_FILE")
    local FAMILY=$(jq -r '.family' "$DATA_FILE")
    local KEY_MESSAGE=$(jq -r '.keyMessage' "$DATA_FILE")
    
    # Construire le prompt
    local PROMPT="You are Emma Collins, a professional perfume reviewer for HelloBeautyBlog.com.

CRITICAL INSTRUCTIONS - READ CAREFULLY:

1. Write ONLY the article content in ${LANG_NAME}. 
2. DO NOT include any YAML front matter (no ---).
3. Start directly with the article text.
4. Follow the writing brief below EXACTLY.

WRITING BRIEF:
$(cat "$BRIEF_FILE")

PERFUME INFORMATION:
- Brand: ${BRAND}
- Product: ${PRODUCT_NAME}
- Launch Year: ${YEAR}
- Perfumer: ${PERFUMER}
- Fragrance Family: ${FAMILY}
- Key Message: ${KEY_MESSAGE}

PERFUME DATA (use for accurate information):
$(jq '.' "$DATA_FILE")

IMPORTANT REMINDERS:
- Write 900-1100 words
- Use natural ${LANG_NAME} expressions and idioms
- Include personal anecdotes
- Vary sentence length
- Avoid AI-detectable phrases
- Express genuine opinions (including minor criticisms)

OUTPUT: Raw article text only. No YAML. No code blocks. Start with the first paragraph."

    # Créer le payload JSON
    local PAYLOAD=$(jq -n \
        --arg prompt "$PROMPT" \
        --arg model "$MODEL" \
        '{
            "model": $model,
            "max_tokens": 4096,
            "temperature": 0.85,
            "messages": [{"role": "user", "content": $prompt}]
        }')
    
    # Appel API avec timeout
    local RESPONSE=$(curl -s --max-time $TIMEOUT \
        -H "Content-Type: application/json" \
        -H "x-api-key: $API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d "$PAYLOAD" \
        https://api.anthropic.com/v1/messages 2>&1)
    
    # Vérifier les erreurs curl
    if [ $? -ne 0 ]; then
        echo "CURL_ERROR: $RESPONSE" >&2
        return 1
    fi
    
    # Vérifier les erreurs API
    local ERROR=$(echo "$RESPONSE" | jq -r '.error.message // empty')
    if [ -n "$ERROR" ]; then
        echo "API_ERROR: $ERROR" >&2
        return 1
    fi
    
    # Extraire le contenu
    local CONTENT=$(echo "$RESPONSE" | jq -r '.content[0].text // empty')
    
    if [ -z "$CONTENT" ]; then
        echo "EMPTY_CONTENT" >&2
        return 1
    fi
    
    # Nettoyer le contenu (supprimer d'éventuels --- ou ``` au début)
    CONTENT=$(echo "$CONTENT" | sed '/^---$/d' | sed '/^```/d' | sed 's/^```markdown//' | sed 's/^```$//')
    
    echo "$CONTENT"
    return 0
}

# ============================================
# VALIDATION D'UN FICHIER
# ============================================
validate_file() {
    local FILE=$1
    local ERRORS=0
    
    # Vérifier l'existence
    if [ ! -f "$FILE" ]; then
        echo "FILE_NOT_FOUND"
        return 1
    fi
    
    # Vérifier la taille minimale
    local SIZE=$(wc -c < "$FILE")
    if [ $SIZE -lt $MIN_FILE_SIZE ]; then
        echo "TOO_SMALL:$SIZE"
        return 1
    fi
    
    # Vérifier les champs obligatoires
    local MISSING=""
    
    grep -q "^brand:" "$FILE" || MISSING="$MISSING brand"
    grep -q "^rating:" "$FILE" || MISSING="$MISSING rating"
    grep -q "^translationKey:" "$FILE" || MISSING="$MISSING translationKey"
    grep -q "^longevity:" "$FILE" || MISSING="$MISSING longevity"
    grep -q "^sillage:" "$FILE" || MISSING="$MISSING sillage"
    
    # Vérifier les listes YAML
    local TOP=$(grep -A5 "^topNotes:" "$FILE" | grep -c "^  -")
    local HEART=$(grep -A5 "^heartNotes:" "$FILE" | grep -c "^  -")
    local BASE=$(grep -A5 "^baseNotes:" "$FILE" | grep -c "^  -")
    local SEASON=$(grep -A5 "^season:" "$FILE" | grep -c "^  -")
    local OCCASION=$(grep -A5 "^occasion:" "$FILE" | grep -c "^  -")
    
    [ $TOP -eq 0 ] && MISSING="$MISSING topNotes"
    [ $HEART -eq 0 ] && MISSING="$MISSING heartNotes"
    [ $BASE -eq 0 ] && MISSING="$MISSING baseNotes"
    [ $SEASON -eq 0 ] && MISSING="$MISSING season"
    [ $OCCASION -eq 0 ] && MISSING="$MISSING occasion"
    
    if [ -n "$MISSING" ]; then
        echo "MISSING:$MISSING"
        return 1
    fi
    
    echo "OK:$SIZE:top=$TOP,heart=$HEART,base=$BASE,season=$SEASON,occasion=$OCCASION"
    return 0
}

# ============================================
# ASSEMBLAGE ET SAUVEGARDE
# ============================================
assemble_and_save() {
    local PERFUME_SLUG=$1
    local LANG=$2
    local OUTPUT_DIR="$CONTENT_DIR/$LANG/perfumes"
    local OUTPUT_FILE="$OUTPUT_DIR/${PERFUME_SLUG}.md"
    
    # Créer le dossier si nécessaire
    mkdir -p "$OUTPUT_DIR"
    
    log "Génération $PERFUME_SLUG ($LANG)..."
    
    # Générer le front matter (local, pas d'erreur possible)
    local FRONTMATTER=$(generate_frontmatter "$PERFUME_SLUG" "$LANG")
    
    # Générer le contenu (avec retry)
    local CONTENT=$(generate_content_with_retry "$PERFUME_SLUG" "$LANG")
    
    if [ $? -ne 0 ] || [ -z "$CONTENT" ]; then
        log_error "Échec génération contenu pour $LANG"
        return 1
    fi
    
    # Assembler le fichier
    echo "$FRONTMATTER" > "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "$CONTENT" >> "$OUTPUT_FILE"
    
    # Valider le fichier
    local VALIDATION=$(validate_file "$OUTPUT_FILE")
    local VAL_STATUS=$?
    
    if [ $VAL_STATUS -eq 0 ]; then
        local SIZE=$(echo "$VALIDATION" | cut -d: -f2)
        log_success "$PERFUME_SLUG ($LANG) - $SIZE bytes - VALIDÉ"
        return 0
    else
        log_error "$PERFUME_SLUG ($LANG) - Validation échouée: $VALIDATION"
        # Garder le fichier pour inspection
        mv "$OUTPUT_FILE" "${OUTPUT_FILE}.failed"
        return 1
    fi
}

# ============================================
# RAPPORT FINAL
# ============================================
generate_report() {
    local PERFUME_SLUG=$1
    shift
    local RESULTS=("$@")
    
    echo ""
    echo "=============================================="
    echo "           RAPPORT DE GÉNÉRATION"
    echo "=============================================="
    echo "Parfum: $PERFUME_SLUG"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Log: $LOG_FILE"
    echo "----------------------------------------------"
    
    local SUCCESS=0
    local FAILED=0
    
    for result in "${RESULTS[@]}"; do
        local LANG=$(echo "$result" | cut -d: -f1)
        local STATUS=$(echo "$result" | cut -d: -f2)
        local DETAILS=$(echo "$result" | cut -d: -f3-)
        
        if [ "$STATUS" = "OK" ]; then
            echo -e "  ${GREEN}✅ $LANG${NC} - $DETAILS"
            ((SUCCESS++))
        else
            echo -e "  ${RED}❌ $LANG${NC} - $STATUS: $DETAILS"
            ((FAILED++))
        fi
    done
    
    echo "----------------------------------------------"
    echo "Résultat: $SUCCESS succès, $FAILED échecs"
    echo "=============================================="
    
    # Retourner le nombre d'échecs (pour exit code)
    return $FAILED
}

# ============================================
# MAIN
# ============================================
main() {
    local PERFUME_SLUG=$1
    local TARGET_LANG=$2
    local DRY_RUN=false
    
    # Vérifier les arguments
    if [ -z "$PERFUME_SLUG" ]; then
        echo "Usage: $0 <perfume_slug> [langue|--dry-run]"
        echo ""
        echo "Options:"
        echo "  <langue>     Générer une seule langue (ex: fr, en, de)"
        echo "  --dry-run    Vérifier les prérequis sans générer"
        echo ""
        echo "Exemples:"
        echo "  $0 boss-alive              # Toutes les langues"
        echo "  $0 boss-alive fr           # Français uniquement"
        echo "  $0 boss-alive --dry-run    # Vérification seule"
        exit 1
    fi
    
    # Mode dry-run
    if [ "$TARGET_LANG" = "--dry-run" ]; then
        DRY_RUN=true
        TARGET_LANG=""
    fi
    
    # Afficher l'entête
    echo ""
    echo "=============================================="
    echo "   GÉNÉRATION ROBUSTE V2.0 - HelloBeautyBlog"
    echo "=============================================="
    echo "Parfum: $PERFUME_SLUG"
    echo "Mode: $([ "$DRY_RUN" = true ] && echo "VÉRIFICATION" || echo "GÉNÉRATION")"
    echo "Log: $LOG_FILE"
    echo "=============================================="
    echo ""
    
    log_info "Démarrage génération pour $PERFUME_SLUG"
    
    # Vérification des prérequis
    check_prerequisites "$PERFUME_SLUG"
    local PREREQ_ERRORS=$?
    
    if [ $PREREQ_ERRORS -gt 0 ]; then
        log_error "$PREREQ_ERRORS erreur(s) de prérequis détectée(s)"
        echo ""
        echo "Corrigez les erreurs ci-dessus avant de relancer."
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
    
    # Mode dry-run: s'arrêter ici
    if [ "$DRY_RUN" = true ]; then
        echo ""
        log_info "Mode dry-run: vérification terminée, pas de génération"
        exit 0
    fi
    
    # Déterminer les langues à générer
    local LANGS_TO_GENERATE=()
    if [ -n "$TARGET_LANG" ]; then
        # Vérifier que la langue existe
        local VALID=false
        for L in "${LANGUAGES[@]}"; do
            [ "$L" = "$TARGET_LANG" ] && VALID=true
        done
        
        if [ "$VALID" = false ]; then
            log_error "Langue invalide: $TARGET_LANG"
            echo "Langues disponibles: ${LANGUAGES[*]}"
            exit 1
        fi
        
        LANGS_TO_GENERATE=("$TARGET_LANG")
    else
        LANGS_TO_GENERATE=("${LANGUAGES[@]}")
    fi
    
    log_info "Langues à générer: ${LANGS_TO_GENERATE[*]}"
    echo ""
    
    # Génération
    local RESULTS=()
    local TOTAL=${#LANGS_TO_GENERATE[@]}
    local CURRENT=0
    
    for lang in "${LANGS_TO_GENERATE[@]}"; do
        ((CURRENT++))
        log "[$CURRENT/$TOTAL] Génération $lang..."
        
        if assemble_and_save "$PERFUME_SLUG" "$lang"; then
            local SIZE=$(wc -c < "$CONTENT_DIR/$lang/perfumes/${PERFUME_SLUG}.md")
            RESULTS+=("$lang:OK:$SIZE bytes")
        else
            RESULTS+=("$lang:FAILED:voir log")
        fi
        
        # Pause entre les langues (sauf pour la dernière)
        if [ $CURRENT -lt $TOTAL ]; then
            log_info "Pause de ${PAUSE_BETWEEN_LANGS}s..."
            sleep $PAUSE_BETWEEN_LANGS
        fi
    done
    
    # Rapport final
    generate_report "$PERFUME_SLUG" "${RESULTS[@]}"
    local FAILED_COUNT=$?
    
    # Log final
    if [ $FAILED_COUNT -eq 0 ]; then
        log_success "Génération terminée avec succès!"
    else
        log_warning "Génération terminée avec $FAILED_COUNT échec(s)"
    fi
    
    exit $FAILED_COUNT
}

# Exécuter
main "$@"
