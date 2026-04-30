#!/bin/bash
# Import all n8n workflows automatically

set -e

N8N_URL="http://localhost:5678"
N8N_USER="admin"

echo "📥 Importing all workflows into n8n..."
echo ""

WORKFLOWS_DIR="$(dirname "$0")/workflows"

# Import each workflow
for wf in "$WORKFLOWS_DIR"/*.json; do
    if [ -f "$wf" ]; then
        filename=$(basename "$wf")
        echo "  Importing: $filename"

        # Remove existing IDs to force create new workflows
        python3 -c "
import json
with open('$wf') as f:
    d = json.load(f)
# Remove the workflow ID if present
if 'id' in d:
    del d['id']
# Remove node IDs too so n8n generates new ones
for node in d.get('nodes', []):
    if 'id' in node:
        del node['id']
# Save to temp file
with open('/tmp/wf_import.json', 'w') as f:
    json.dump(d, f)
"
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -u "$N8N_USER:$N8N_BASIC_AUTH_PASSWORD" \
            -d @/tmp/wf_import.json \
            "$N8N_URL/rest/workflows" > /dev/null 2>&1

        echo "    ✓ Done"
    fi
done

echo ""
echo "✅ All workflows imported!"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:5678"
echo "2. Go to Workflows"
echo "3. Activate each workflow (toggle ON)"
echo ""
echo "Recommended order:"
echo "  1. economic_calendar_daily"
echo "  2. news_monitor_realtime"
echo "  3. price_feed_yahoo"
echo "  4. sentiment_snapshot"
echo "  5. crypto_funding_rates"
echo "  6. crypto_oi_liquidations"
echo "  7. crypto_global_metrics"
echo "  8. crypto_snapshot_aggregator"
echo "  9. premarket_briefing"
echo " 10. critical_event_alert"
