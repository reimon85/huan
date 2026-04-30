# Trading Companion

## Contexto

Este es un agente de IA copiloto para **trading discrecional**.
El trader opera Forex (majors y crosses), Futuros (ES, NQ, CL, GC), criptomonedas y materias primas.
Estilo mixto: intradiario cuando el contexto lo justifica, swing cuando la estructura lo permite.

## Stack

- **Motor**: Hermes Agent (NousResearch) v0.11.0
- **Modelo**: minimax/minimax-m2.7
- **Datos de mercado**: Fuentes directas vía tools (Yahoo Finance, ForexFactory, CoinGecko, etc.)
- **Base de conocimiento**: Wiki interno en Markdown + memoria persistente de Hermes
- **Interfaz**: CLI de Hermes + Gateway multi-plataforma (Telegram, Discord)

## Convenciones

- Todo el conocimiento de trading vive en skills y contexto, no hardcodeado.
- Las tools obtienen datos de mercado de forma feed-agnostic.
- Los prompts de análisis son skills invocables (`/briefing`, `/validate`, `/macro`, `/debrief`).
- El agente nunca da señales de entrada directas sin contexto completo.

## Estructura del proyecto

```
.
├── AGENTS.md              # Este archivo
├── SOUL.md                # Identidad del agente
├── MEMORY.md              # Memoria persistente de sesiones
├── USER.md                # Perfil del trader
├── .hermes/skills/        # Skills de trading (briefing, validate, macro, debrief)
├── .hermes/plugins/       # Plugin con tools de datos
├── trading_companion/     # Código Python (tools, wiki)
│   ├── tools/
│   │   ├── market_data.py   # 7 tools de datos de mercado
│   │   └── wiki_context.py  # Búsqueda en wiki
│   └── wiki/                # Base de conocimiento legacy
└── trading-agent/         # n8n legacy (opcional, ya no requerido)
```

## Estado actual

- [x] Hermes Agent instalado y configurado
- [x] Modelo LLM: minimax/minimax-m2.7
- [x] Plugin trading-companion: habilitado
- [x] Skills: 4 skills activas (briefing, validate, macro, debrief)
- [x] Tools: 8 tools registradas
- [x] Fuentes directas reemplazan webhooks n8n
- [x] Test end-to-end exitoso

## Próximos pasos

1. Probar skills en sesión real: `/briefing`
2. Configurar gateway (Telegram/Discord) si se desea
3. Agregar cron jobs para automatización
4. Expandir wiki con nuevo aprendizaje
