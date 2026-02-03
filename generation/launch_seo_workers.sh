#!/bin/bash
cd /home/ubuntu/hbb/generation

echo "=== Launching 4 SEO workers ==="
for i in 0 1 2 3; do
    nohup python3 -u generate_subcats_seo_worker.py $i 4 > /tmp/subcats_seo_w${i}.log 2>&1 &
    echo "Worker $i: PID $!"
done

# Auto-commit loop every 3 minutes
echo "Starting auto-commit loop..."
while true; do
    sleep 180
    # Check if any worker still running
    if ! pgrep -f "generate_subcats_seo_worker" > /dev/null; then
        echo "All workers finished, final commit..."
        cd /home/ubuntu/hbb
        git add content/ && git commit -m "SEO: final batch" && git push origin main
        break
    fi
    cd /home/ubuntu/hbb
    DONE=$(python3 -c "import json; print(len(json.load(open('generation/subcats_seo_progress.json'))))" 2>/dev/null || echo "?")
    git add content/ && git commit -m "SEO: $DONE/2786 subcats done" && git push origin main 2>/dev/null
    echo "[$(date)] Committed - $DONE/2786 done"
done
echo "=== All done ==="
