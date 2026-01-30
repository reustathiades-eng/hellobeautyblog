#!/bin/bash
# Batch generation de tous les parfums restants

# ANTHROPIC_API_KEY doit être définie avant de lancer ce script
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERREUR: ANTHROPIC_API_KEY non définie"
    exit 1
fi

cd /home/ubuntu/hbb
LOG="/home/ubuntu/hbb/generation/logs/batch_$(date +%Y%m%d_%H%M%S).log"

echo "=== BATCH GENERATION START ===" | tee -a "$LOG"
echo "Date: $(date)" | tee -a "$LOG"

PERFUMES=(
    "guerlain-shalimar"
    "miss-dior"
    "jadore"
    "la-vie-est-belle"
    "black-opium"
    "coco-mademoiselle"
    "good-girl"
    "bleu-de-chanel"
    "acqua-di-gio"
    "1-million"
)

TOTAL=${#PERFUMES[@]}
CURRENT=0

for perfume in "${PERFUMES[@]}"; do
    ((CURRENT++))
    echo "" | tee -a "$LOG"
    echo "[$CURRENT/$TOTAL] ========== $perfume ==========" | tee -a "$LOG"
    echo "Started: $(date)" | tee -a "$LOG"
    
    ./generation/scripts/generate_perfume_v2.sh "$perfume" >> "$LOG" 2>&1
    
    echo "Finished: $(date)" | tee -a "$LOG"
    
    # Pause entre les parfums
    if [ $CURRENT -lt $TOTAL ]; then
        echo "Pause 10s before next perfume..." | tee -a "$LOG"
        sleep 10
    fi
done

echo "" | tee -a "$LOG"
echo "=== BATCH GENERATION COMPLETE ===" | tee -a "$LOG"
echo "Date: $(date)" | tee -a "$LOG"

# Créer un fichier status
echo "COMPLETED at $(date)" > /home/ubuntu/hbb/generation/logs/batch_status.txt
