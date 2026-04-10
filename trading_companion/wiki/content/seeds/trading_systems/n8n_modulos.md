---
title: Módulos n8n - Índice Completo
type: topic
branch: trading_systems
tags: n8n,modulos,workflows,indice,endpoints
summary: Índice y documentación de todos los workflows n8n del sistema
---

# Módulos n8n - Índice Completo

Todos los workflows de automatización para el sistema de trading agent.

## Resumen de Módulos

| # | Módulo | Archivo | Trigger | Estado |
|---|--------|---------|---------|--------|
| 1 | Docker + Base | `docker-compose.yml` | - | ✅ |
| 2 | Calendario Económico | `economic_calendar_daily.json` | 06:00 L-V | ✅ |
| 3 | News Monitor | `news_monitor_realtime.json` | 15 min, 24/7 | ✅ |
| 4 | COT Report | `cot_weekly_update.json` | Viernes 22:30 | ✅ |
| 5 | Sentiment Snapshot | `sentiment_snapshot.json` | Cada hora L-V | ✅ |
| 6 | Premarket Briefing | `premarket_briefing.json` | 06:30 L-V | ✅ |
| 7 | Critical Alert | `critical_event_alert.json` | Webhook | ✅ |
| 8 | Price Feed Yahoo | `price_feed_yahoo.json` | 15 min L-V | ✅ |
| 9A | Crypto Funding Rates | `crypto_funding_rates.json` | 5 min, 24/7 | ✅ |
| 9B | Crypto OI & Liq | `crypto_oi_liquidations.json` | 15 min, 24/7 | ✅ |
| 9C | Crypto Global | `crypto_global_metrics.json` | Cada hora, 24/7 | ✅ |
| 10 | Crypto Aggregator | `crypto_snapshot_aggregator.json` | 30 min + webhook | ✅ |

## Módulos Base

### Módulo 1: Docker + Base
**Archivo**: `docker-compose.yml`

```bash
cd trading-agent
cp .env .env.local  # Editar passwords
docker-compose up -d
# Acceder en http://localhost:5678
```

## Módulos de Contexto (No-Crypto)

### Módulo 2: Calendario Económico
**Archivo**: `workflows/economic_calendar_daily.json`
**Trigger**: 06:00 L-V (Europe/Madrid)

Obtiene eventos económicos del día desde Forex Factory.

### Módulo 3: News Monitor
**Archivo**: `workflows/news_monitor_realtime.json`
**Trigger**: Cada 15 minutos, 24/7

Monitoriza 10 feeds RSS (Reuters, ForexLive, EIA, BBC, NYTimes, etc.)

### Módulo 4: COT Report
**Archivo**: `workflows/cot_weekly_update.json`
**Trigger**: Viernes 22:30 (Europe/Madrid)

Descarga posicionamiento CFTC para Forex, índices, energía, metales.

### Módulo 5: Sentiment Snapshot
**Archivo**: `workflows/sentiment_snapshot.json`
**Trigger**: Cada hora, L-V 7-23

Agrega CNN Fear & Greed, Crypto F&G, VIX, DXY, Gold/Oil ratio.

## Módulo 6: Premarket Briefing
**Archivo**: `workflows/premarket_briefing.json`
**Trigger**: 06:30 L-V (Europe/Madrid)
**Actualizado**: Ahora incluye prices + crypto

Orquestador principal. Consume todos los módulos y genera briefing via LLM.

## Módulo 7: Critical Alert
**Archivo**: `workflows/critical_event_alert.json`
**Trigger**: Webhook `/webhook/news-alert`

Análisis rápido de eventos urgentes + Telegram.

## Módulos de Precio

### Módulo 8: Price Feed Yahoo
**Archivo**: `workflows/price_feed_yahoo.json`
**Trigger**: Cada 15 minutos, L-V

Precios de Forex, índices, futuros, crypto (Yahoo Finance).

| Categoría | Ejemplos |
|-----------|----------|
| Forex | EURUSD, GBPUSD, USDJPY... |
| Índices | S&P500, Nasdaq, VIX, DAX... |
| Futuros | ES, NQ, CL, GC... |
| Crypto | BTC, ETH, SOL, BNB |
| Bonos | US10Y, US30Y |

**Arquitectura**: Feed-agnostic (capa de abstracción lista para upgrade a Polygon.io)

## Módulos Crypto

### Módulo 9A: Crypto Funding Rates
**Archivo**: `workflows/crypto_funding_rates.json`
**Trigger**: Cada 5 minutos, 24/7
**Fuente**: Loris Tools API

Funding rates de 25+ exchanges. Detecta funding positivo/negativo extremo.

### Módulo 9B: Crypto OI & Liquidations
**Archivo**: `workflows/crypto_oi_liquidations.json`
**Trigger**: Cada 15 minutos, 24/7
**Fuente**: Loris Tools API

Open Interest y liquidaciones. Detecta regimes y anomalías.

### Módulo 9C: Crypto Global Metrics
**Archivo**: `workflows/crypto_global_metrics.json`
**Trigger**: Cada hora, 24/7
**Fuente**: CoinGecko API

Dominance, market cap, régimen global (BTC Season, ALT Season, etc.)

### Módulo 10: Crypto Snapshot Aggregator
**Archivo**: `workflows/crypto_snapshot_aggregator.json`
**Trigger**: Cada 30 minutos + webhook
**Consume**: Módulos 9A, 9B, 9C, 8

Agregador central crypto. Unifica todos los datos en un snapshot + régimen.

---

## Tabla Completa de Endpoints

| Endpoint | Módulo | Método | Descripción |
|----------|--------|--------|-------------|
| `/webhook/calendar-today` | #2 | GET | Calendario económico del día |
| `/webhook/news-latest` | #3 | GET | Últimas 20 noticias |
| `/webhook/news-urgent` | #3 | GET | Noticias de urgencia alta |
| `/webhook/news-alert` | #3 | POST | Alerta de noticia urgente |
| `/webhook/cot-latest` | #4 | GET | Resumen COT formateado |
| `/webhook/cot-data` | #4 | GET | JSON completo COT |
| `/webhook/sentiment` | #5 | GET | Risk Appetite Score |
| `/webhook/briefing-today` | #6 | GET | Briefing completo del día |
| `/webhook/prices` | #8 | GET | Snapshot de precios formateado |
| `/webhook/prices-raw` | #8 | GET | JSON normalizado completo |
| `/webhook/prices-alerts` | #8 | GET | Solo alertas activas |
| `/webhook/price/{symbol}` | #8 | GET | Precio de símbolo específico |
| `/webhook/price-alert` | #8 | POST | Alerta de precio (para #7) |
| `/webhook/funding` | #9A | GET | Funding rates formateado |
| `/webhook/funding-raw` | #9A | GET | JSON completo funding |
| `/webhook/funding-signals` | #9A | GET | Solo señales activas |
| `/webhook/funding/{symbol}` | #9A | GET | Funding de símbolo específico |
| `/webhook/crypto-alert` | #9A | POST | Alerta crypto (para #7) |
| `/webhook/crypto-oi` | #9B | GET | Open Interest snapshot |
| `/webhook/crypto-liquidations` | #9B | GET | Liquidaciones recientes |
| `/webhook/crypto-volume` | #9B | GET | Volumen |
| `/webhook/crypto-global` | #9C | GET | Métricas globales crypto |
| `/webhook/crypto-snapshot` | #10 | GET | Snapshot crypto completo |
| `/webhook/crypto-regime` | #10 | GET | Régimen + narrative |
| `/webhook/alerts-today` | #7 | GET | Historial de alertas del día |

---

## Orden de Carga en n8n

1. **Módulo 1** (docker-compose)
2. **Módulos independientes** (fuentes):
   - #2 Calendario
   - #3 News Monitor
   - #4 COT
   - #5 Sentiment
   - #8 Prices
   - #9A Funding
   - #9B OI/Liq
   - #9C Global
3. **Módulo 10** (consume #9A, #9B, #9C, #8)
4. **Módulo 6** (consume todos)
5. **Módulo 7** (consume #3, #5, #2, #4, #8, #9A)

**Importante**: Los webhooks internos deben existir antes de que los workflows que los consumen se activen.

## Flujo de Datos Completo

```
06:00  #2 Calendario
  ↓
06:30  #6 Briefing ← consume #2, #3, #4, #5, #8, #10
  ↓
08:00-23:00  #5 Sentiment (cada hora)
  ↓
15 min  #3 News Monitor (24/7)
  ↓     #8 Prices (L-V)
  ↓     #9B OI/Liq (24/7)
5 min   #9A Funding (24/7)
  ↓     #10 Aggregator (30 min)
  ↓
Si alerta alta → #7 Critical Alert → Telegram
```
