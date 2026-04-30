# Trading Companion (Hermes Agent)

Copiloto de IA para trading discrecional, ahora basado en **Hermes Agent**.

## Arquitectura

Este proyecto es un **plugin + skills pack** para Hermes Agent. No es una aplicación standalone: Hermes es el motor, y este repo aporta:

- **Skills de trading** en `.hermes/skills/` — prompts estructurados invocables via `/briefing`, `/validate`, `/macro`, `/debrief`
- **Tools de datos** en `trading_companion/tools/` — obtienen precios, calendario, sentiment, noticias, COT, crypto y wiki
- **Contexto persistente** via `AGENTS.md`, `SOUL.md`, `MEMORY.md`, `USER.md`
- **Plugin** en `.hermes/plugins/trading-companion/` para auto-registro de tools

## Requisitos

- Python 3.11+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) instalado
- n8n (opcional, legacy) para workflows de datos de mercado

## Instalación

```bash
# 1. Instalar Trading Companion como paquete editable
pip install -e .

# 2. Verificar que Hermes detecta el plugin
hermes plugins

# 3. Configurar modelo LLM
hermes model

# 4. Probar
hermes
> /briefing
```

## Uso

### CLI

```bash
hermes
```

Dentro de la sesión:
- `/briefing` — Genera briefing pre-sesión completo
- `/validate` — Valida un setup antes de entrar
- `/macro` — Analiza un evento macro/geopolítico
- `/debrief` — Debrief post-sesión con aprendizaje estructurado

### Gateway (Telegram / Discord)

```bash
hermes gateway setup
hermes gateway start
```

### Cron (automatización)

```bash
# Ejemplo: briefing diario a las 06:30
hermes cron add --name "briefing-morning" --schedule "30 6 * * 1-5" --platform telegram --prompt "/briefing"
```

## Estructura

```
.
├── AGENTS.md                    # Contexto del proyecto para Hermes
├── SOUL.md                      # Identidad del agente de trading
├── MEMORY.md                    # Memoria persistente (reglas, setups, errores)
├── USER.md                      # Perfil del trader
├── .hermes/
│   ├── skills/
│   │   ├── briefing/SKILL.md    # Skill: briefing pre-sesión
│   │   ├── validate/SKILL.md    # Skill: validación de setup
│   │   ├── macro/SKILL.md       # Skill: análisis macro/geopolítico
│   │   └── debrief/SKILL.md     # Skill: debrief post-sesión
│   └── plugins/
│       └── trading-companion/   # Plugin con tools de datos
├── trading_companion/
│   ├── tools/
│   │   ├── market_data.py       # Tools: precios, calendario, sentiment, etc.
│   │   └── wiki_context.py      # Tool: búsqueda en wiki interna
│   └── wiki/                    # Base de conocimiento legacy (Markdown)
├── trading-agent/               # n8n workflows (legacy, opcional)
└── tests/
```

## Tools registradas

| Tool | Función | Emoji |
|------|---------|-------|
| `fetch_market_context` | Contexto completo de mercado | 📊 |
| `fetch_prices` | Precios actuales | 💹 |
| `fetch_calendar` | Calendario económico | 📅 |
| `fetch_sentiment` | Fear & Greed, VIX | 🧠 |
| `fetch_news` | Noticias urgentes | 📰 |
| `fetch_cot` | Reporte COT semanal | 📈 |
| `fetch_crypto_snapshot` | Funding, OI, dominance | 🪙 |
| `fetch_wiki_context` | Búsqueda en wiki interna | 📚 |

## Datos de mercado

Las tools obtienen datos directamente de fuentes públicas (sin API key):
- **Precios**: Yahoo Finance (Forex, futuros, crypto, commodities)
- **Calendario**: ForexFactory JSON público
- **Sentiment**: Alternative.me Fear & Greed + VIX (Yahoo Finance)
- **Noticias**: ForexLive RSS
- **Crypto**: CoinGecko API pública
- **COT**: CFTC (legacy fallback si n8n está disponible)

n8n es ahora opcional/legacy. Si aún lo usas, configura `WEBHOOK_URL` en tu `.env`.

## Seguridad

### Protección de secretos

- `.env` y `.env.local` están en `.gitignore` — nunca se suben
- Solo `.env.example` (plantilla sin secretos) está trackeado
- Pre-commit hooks con `detect-secrets` bloquean commits con API keys
- `trading-agent/.env.local` (con secretos legacy) está en `.gitignore`

### Configurar pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Verificar que no hay secretos en el historial

```bash
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
```

### Rotar una key comprometida

Si accidentalmente subiste una key a git:
1. Rota la key inmediatamente en el proveedor (MiniMax, OpenRouter, etc.)
2. Borra el archivo del historial: `git filter-repo --path <archivo> --invert-paths`
3. Fuerza push al remoto (si ya se subió)

## Desarrollo

```bash
pip install -e ".[dev]"
pytest --cov=trading_companion
```

## License

MIT
