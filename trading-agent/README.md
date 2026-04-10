# Trading Agent n8n

AI copilot for personal discretionary trading. Automates market analysis, trade ideation, and execution workflow using n8n workflows and LLMs.

## Overview

This project sets up a self-hosted n8n instance configured for:
- **Markets**: Forex, Futures (ES/NQ/CL/GC), Crypto, Commodities
- **Trading Style**: Mixed intraday + swing trading
- **Stack**: n8n (Docker), Claude/GPT via API, free data sources

## Quick Start

```bash
# 1. Navigate to project directory
cd trading-agent

# 2. Copy and configure environment
cp .env.example .env
nano .env  # Update passwords and API keys

# 3. Start n8n
docker-compose up -d

# 4. Wait for health check (60 seconds)
docker-compose ps

# 5. Access n8n UI
open http://localhost:5678
```

## Access

| Service | URL | Credentials |
|---------|-----|-------------|
| n8n UI | http://localhost:5678 | See .env (N8N_BASIC_AUTH_USER/PASSWORD) |

## Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update these required variables:
   - `N8N_BASIC_AUTH_PASSWORD` - Strong password for n8n access
   - `WEBHOOK_SECRET` - Random secret for webhook authentication
   - `LLM_API_KEY` - Your Anthropic or OpenAI API key

3. Optional API keys (uncomment as needed):
   - `ALPACA_API_KEY/SECRET` - US brokerage for execution
   - `TRADING_ECONOMICS_API_KEY` - Economic calendar
   - `EIA_API_KEY` - Energy data

## Workflow Import

1. Open n8n at http://localhost:5678
2. Click "Import from File" (top-right menu)
3. Select workflow JSON from `workflows/` directory
4. Activate the workflow (toggle switch)

## Project Structure

```
trading-agent/
├── docker-compose.yml      # Container orchestration
├── .env                   # Environment variables (not in git)
├── README.md              # This file
├── n8n_data/              # n8n persistent data (credentials, settings)
├── workflows/             # n8n workflow JSON files
│   └── data/
│       ├── wiki/          # Market research & trading notes
│       ├── sessions/      # Trade session logs
│       └── cache/         # Temporary data cache
```

## Workflow Modules

### Module 1: Base Infrastructure (this repo)
- n8n server setup
- Environment configuration
- Directory structure

### Module 2: Data Ingestion (planned)
- Market data collection (prices, economic calendar)
- Real-time price feeds
- News aggregation

### Module 3: Analysis Engine (planned)
- Technical analysis calculations
- Pattern recognition
- LLM-powered trade ideation

### Module 4: Trade Execution (planned)
- Alpaca integration for US markets
- Position management
- Risk management rules

### Module 5: Session Management (planned)
- Trade journaling
- Performance tracking
- Session debriefing

## Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f n8n

# Stop services
docker-compose down

# Full reset (removes data)
docker-compose down -v
docker-compose up -d
```

## Security Notes

- Change all `CHANGE_ME_*` passwords immediately
- Never commit `.env` to version control
- Use strong webhook secrets (use `openssl rand -hex 32`)
- Consider VPN for remote access instead of exposing port 5678
- Enable HTTPS reverse proxy for production use

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs n8n
```

**Health check failing:**
```bash
docker-compose restart n8n
```

**Reset everything:**
```bash
docker-compose down -v
rm -rf n8n_data/* workflows/*
docker-compose up -d
```
