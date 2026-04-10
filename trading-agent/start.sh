#!/bin/bash
# Trading Agent - Quick Start Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Trading Companion Agent${NC}"
echo "=============================="

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not set${NC}"
    echo "Export it: export ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
fi

# Check if n8n is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5678 2>/dev/null | grep -q "200"; then
    echo -e "${GREEN}n8n:${NC} Running at http://localhost:5678"
else
    echo -e "${YELLOW}n8n:${NC} Not running (start with: cd trading-agent && docker-compose up -d)"
fi

echo ""
echo "Available commands:"
echo "=================="
echo ""
echo "1. Chat with the agent:"
echo "   python -m trading_companion.agent 'Qué vigilar hoy?'"
echo ""
echo "2. Analyze a macro event:"
echo "   python -m trading_companion.agent --mode analysis 'Evento: CPI sube 0.5%'"
echo ""
echo "3. Validate a trade setup:"
echo "   python -m trading_companion.agent --mode setup 'EURUSD long en 1.0850 con SL 1.0820'"
echo ""
echo "4. Debrief today's session:"
echo "   python -m trading_companion.agent --mode debrief '+1.8R hoy, 3 trades'"
echo ""
echo "5. Show system prompt:"
echo "   python -m trading_companion.agent --system"
echo ""
echo "6. Run without fetching n8n data (offline mode):"
echo "   python -m trading_companion.agent --no-fetch 'Pregunta general'"
echo ""
