#!/bin/bash
# Launch lot generation in background with logging
# Usage: ./launch_lot.sh [lot.json] [extra args...]
# Example: ./launch_lot.sh lot.json --product=chanel-no-5
# Example: ./launch_lot.sh lot.json --lang=fr,de
# Example: ./launch_lot.sh lot.json --en-only

cd /home/ubuntu/hbb/generation

LOT_FILE="${1:-lot.json}"
shift 2>/dev/null
EXTRA_ARGS="$@"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/hbb_generate_${TIMESTAMP}.log"

echo "🚀 Launching generation..."
echo "   Lot: $LOT_FILE"
echo "   Args: $EXTRA_ARGS"
echo "   Log: $LOG_FILE"
echo ""
echo "📋 Follow progress:"
echo "   tail -f $LOG_FILE"
echo ""
echo "🛑 To stop:"
echo "   pkill -f generate_lot.py"

nohup python3 generate_lot.py "$LOT_FILE" $EXTRA_ARGS > "$LOG_FILE" 2>&1 &
PID=$!
echo ""
echo "✅ Started (PID: $PID)"
echo ""

# Auto git commit after generation completes
(
  wait $PID
  cd /home/ubuntu/hbb
  if [ -n "$(git status --porcelain content/)" ]; then
    git add content/ static/images/
    git commit -m "feat: generate articles from lot ($TIMESTAMP)"
    git push origin main
    echo "[$(date +%H:%M:%S)] 🚀 Git push done — deploying to Cloudflare" >> "$LOG_FILE"
  fi
) &

