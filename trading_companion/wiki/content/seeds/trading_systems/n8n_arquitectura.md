---
title: Arquitectura n8n - Sistema Completo
type: article
branch: trading_systems
tags: n8n,arquitectura,workflows,orquestacion
summary: Arquitectura general del sistema de automatización n8n para trading
---

# Arquitectura del Sistema de Trading Agent

## Visión General

El sistema está compuesto por 4 capas principales que trabajan de forma coordinada:

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRADER (Humano)                          │
│                    Discrecional, con experiencia                                        │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                         CAPA 4: LLM                             │
│              Agente IA (Claude/GPT) como copiloto              │
│              - Análisis de contexto                             │
│              - Briefing de pre-mercado                          │
│              - Validación de setups                             │
│              - Alertas críticas                                 │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 3: n8n Workflows                       │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Premarket   │  │  Critical   │  │  Trading    │            │
│  │ Briefing    │  │   Alert     │  │  Journal    │            │
│  │  #6         │  │   #7       │  │  (futuro)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Economic   │  │    News     │  │  Sentiment  │            │
│  │  Calendar   │  │  Monitor    │  │  Snapshot   │            │
│  │  #2         │  │   #3       │  │   #5       │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                         ↕                                      │
│                   ┌─────────────┐                              │
│                   │    COT      │                              │
│                   │   Report    │                              │
│                   │    #4       │                              │
│                   └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 2: Datos + Almacenamiento              │
│                                                                   │
│  /data/                                                         │
│  ├── wiki/          ← Base de conocimiento del agente           │
│  ├── sessions/      ← Logs de sesiones, briefings, debriefs      │
│  └── cache/        ← Datos temporales de workflows              │
│      ├── calendar_today.txt                                     │
│      ├── news_feed.json                                         │
│      ├── cot_latest.json                                        │
│      ├── sentiment_latest.json                                  │
│      └── briefing_today.txt                                     │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 1: Fuentes de Datos                      │
│                                                                   │
│  APIS PÚBLICAS (gratuitas):                                     │
│  - Forex Factory / nfs.faireconomy.media (calendario)           │
│  - Reuters, ForexLive, BBC RSS feeds (noticias)                  │
│  - CFTC public API (COT)                                        │
│  - CNN Fear & Greed, Alternative.me (sentiment)                  │
│  - Yahoo Finance (VIX, DXY, commodities)                        │
│  - EIA (energía)                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

### Flujo Principal del Día

```
06:00  ┌──────────────────┐
       │  Módulo 2:       │
       │  Calendario       │
       │  Económico       │
       └────────┬─────────┘
                ↓
06:30  ┌──────────────────┐     ┌──────────────────┐
       │  Módulo 6:       │────▶│  LLM:             │
       │  Premarket       │     │  Genera Briefing  │
       │  Briefing        │     │  para el trader   │
       └────────┬─────────┘     └──────────────────┘
                │
                ▼
08:00-23:00
       ┌──────────────────┐
       │  Módulo 5:       │
       │  Sentiment       │ (cada hora)
       │  Snapshot        │
       └────────┬─────────┘

       ┌──────────────────┐
       │  Módulo 3:       │
       │  News Monitor    │ (cada 15 min, 24/7)
       │                  │
       └────────┬─────────┘
                │ Si urgencia ALTA
                ▼
       ┌──────────────────┐
       │  Módulo 7:       │────▶ LLM: Análisis
       │  Critical Alert   │     rápido + Telegram
       └──────────────────┘

Viernes 22:30
       ┌──────────────────┐
       │  Módulo 4:       │
       │  COT Weekly      │
       └──────────────────┘
```

## Módulos n8n

| Módulo | Nombre | Schedule | Función |
|--------|--------|----------|---------|
| #1 | Docker + Base | - | Infraestructura |
| #2 | Calendario Económico | 06:00 L-V | Eventos macro del día |
| #3 | News Monitor | Cada 15 min, 24/7 | RSS feeds + clasificación |
| #4 | COT Report | Viernes 22:30 | Posicionamiento CFTC |
| #5 | Sentiment Snapshot | Cada hora L-V 7-23 | Fear & Greed agregado |
| #6 | Premarket Briefing | 06:30 L-V | Orquestador + LLM briefing |
| #7 | Critical Alert | Webhook (on-demand) | Análisis urgente + Telegram |

## Webhooks Internos

Los workflows se comunican entre sí mediante webhooks internos de n8n:

| Endpoint | Método | Retorna |
|----------|--------|---------|
| `/webhook/calendar-today` | GET | Calendario formateado |
| `/webhook/news-latest` | GET | Últimas 20 noticias |
| `/webhook/news-urgent` | GET | Noticias urgencia alta |
| `/webhook/news-alert` | POST | Alerta de noticia urgente |
| `/webhook/cot-latest` | GET | Resumen COT |
| `/webhook/cot-data` | GET | JSON completo COT |
| `/webhook/sentiment` | GET | Snapshot sentiment |
| `/webhook/briefing-today` | GET | Briefing del día |
| `/webhook/alerts-today` | GET | Historial de alertas |

## Variables de Entorno

```bash
# n8n Auth
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=CHANGE_ME

# LLM
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Webhook
WEBHOOK_URL=http://localhost:5678
```

## Archivos Locales

### `/data/wiki/`
- `trader_profile.md` — Perfil del trader, estilo, mercados
- System prompts del agente

### `/data/sessions/`
- `briefing_YYYY-MM-DD.md` — Briefing diario
- `last_session.md` — Notas última sesión
- Debriefs post-sesión

### `/data/cache/`
- `calendar_today.txt` — Calendario del día
- `news_feed.json` — Últimas noticias (100 max)
- `news_seen.json` — GUIDs de noticias vistas
- `cot_latest.json` / `cot_history.json` — Datos COT
- `sentiment_latest.json/txt` — Sentiment actual
- `briefing_today.txt` — Briefing más reciente
- `alerts_today.json` — Alertas del día
