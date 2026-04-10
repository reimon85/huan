# Trading Companion AI

Agente de IA copiloto para trading discrecional con base de conocimiento wiki y automatización n8n.

## Stack Tecnológico

- **n8n** (self-hosted via Docker) — Orquestación de workflows
- **FastAPI** — API REST para wiki
- **Python 3.11+** — Agente IA y servicios
- **SQLite FTS5** — Búsqueda full-text
- **NetworkX** — Knowledge graph

## Estructura del Proyecto

```
trading-agent/          # Automatización n8n
├── docker-compose.yml  # n8n self-hosted
├── workflows/          # 11 workflows JSON
└── data/               # Datos runtime

trading_companion/      # Agente IA Python
├── wiki/               # Base de conocimiento
│   ├── models/         # Modelos de datos
│   ├── repository/      # Markdown + SQLite FTS5
│   ├── services/       # Lógica de negocio
│   └── content/seeds/   # Contenido inicial
├── agents/             # Integración IA
├── core/               # Config, exceptions
└── main.py             # FastAPI app
```

## Quick Start

### 1. Levantar n8n

```bash
cd trading-agent
cp .env.example .env.local
# Editar .env.local con passwords y API keys
docker-compose up -d
# Acceder: http://localhost:5678
```

### 2. Importar Workflows en n8n

1. Abrir n8n → Settings → Import from File
2. Importar en orden:
   - `workflows/economic_calendar_daily.json`
   - `workflows/news_monitor_realtime.json`
   - `workflows/cot_weekly_update.json`
   - `workflows/sentiment_snapshot.json`
   - `workflows/price_feed_yahoo.json`
   - `workflows/crypto_funding_rates.json`
   - `workflows/crypto_oi_liquidations.json`
   - `workflows/crypto_global_metrics.json`
   - `workflows/crypto_snapshot_aggregator.json`
   - `workflows/premarket_briefing.json`
   - `workflows/critical_event_alert.json`

### 3. Configurar API Keys en .env.local

```bash
N8N_BASIC_AUTH_PASSWORD=tu_password_seguro
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Workflows n8n — 26 Endpoints

| Módulo | Trigger | Función |
|--------|---------|---------|
| Calendario | 06:00 L-V | Eventos macro del día |
| News Monitor | 15 min, 24/7 | RSS feeds clasificados |
| COT Report | Viernes 22:30 | Posicionamiento CFTC |
| Sentiment | Cada hora | Fear & Greed agregado |
| Prices | 15 min L-V | Forex, índices, crypto |
| Funding Rates | 5 min, 24/7 | 25+ exchanges crypto |
| OI & Liq | 15 min, 24/7 | Open Interest crypto |
| Crypto Global | Cada hora | Dominance, market cap |
| Crypto Aggregator | 30 min | Snapshot crypto unificado |
| Premarket Briefing | 06:30 L-V | Briefing IA completo |
| Critical Alert | Webhook | Alertas urgentes Telegram |

## Wiki del Agente

Base de conocimiento en `trading_companion/wiki/content/seeds/`:

- **Trading**: Fundamentos, Análisis Técnico, Gestión de Riesgo
- **Trading Systems**: Price Action, Mean Reversion, Prompts IA
- **Data Analysis**: Indicadores Técnicos
- **Trading Bots**: Arquitectura
- **Psicología**: Sesgos Cognitivos
- **Regulación**: Marco Legal

## API REST (Wiki)

```bash
# Levantar API
cd trading_companion
pip install -e .
uvicorn trading_companion.main:app --reload

# Endpoints
GET /api/v1/wiki/branches
GET /api/v1/wiki/branches/{branch}/tree
GET /api/v1/wiki/search?q=RSI
GET /api/v1/wiki/nodes/{id}
```

## Tests

```bash
pip install -e ".[dev]"
pytest --cov=trading_companion
```

## Prompts del Agente IA

El agente conversacional usa estos prompts estructurados:

1. **System Prompt Maestro** — Identidad del agente
2. **Análisis Macro** — Eventos geopolíticos/macro
3. **Validación Setup** — Pre-entrada
4. **Debrief Post-Sesión** — Aprendizaje estructurado

## Arquitectura Feed-Agnostic

Los módulos de precio siguen una capa de abstracción:

```
Feed Adapter → Normalizer → Cache → Webhook → Consumer (LLM)
```

Cambiar de Yahoo Finance a Polygon.io = solo cambiar el Feed Adapter.

## License

MIT
