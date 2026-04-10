---
title: Módulo 8 — Price Feed Yahoo
type: article
branch: trading_systems
tags: n8n,modulo-8,precio,yahoo,forex,indices
summary: Workflow de precios en tiempo real desde Yahoo Finance
---

# Módulo 8 — Price Feed Yahoo

**Archivo**: `workflows/price_feed_yahoo.json`
**Trigger**: Cada 15 minutos, L-V 08:00-21:00 (Europe/Madrid)
**Arquitectura**: Feed-agnostic (capa de abstracción)

## Instrumentos Monitorizados

| Categoría | Símbolos |
|-----------|----------|
| **Forex** | EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY |
| **Índices** | ^GSPC (S&P500), ^NDX (Nasdaq100), ^DJI (Dow), ^VIX, ^FTSE, ^GDAXI, ^N225 |
| **Futuros** | ES=F, NQ=F, CL=F, GC=F, SI=F, NG=F, ZC=F |
| **Crypto** | BTC-USD, ETH-USD, SOL-USD, BNB-USD |
| **DXY** | DX-Y.NYB |
| **Bonos** | ^TNX (US 10Y), ^TYX (US 30Y), ^IRX (US 3M) |

## Arquitectura Feed-Agnostic

```
┌─────────────────────────────────────────────────────┐
│ CAPA 1 — FEED ADAPTER                               │
│ Yahoo Finance Batch API                              │
│ https://query1.finance.yahoo.com/v7/finance/quote  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ CAPA 2 — NORMALIZER                                 │
│ Transforma respuesta Yahoo al schema estándar         │
│ {symbol, price, change_pct_1d, high_1d, low_1d...} │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│ CAPA 3 — CACHE & WEBHOOK                            │
│ Almacena y expone datos normalizados                  │
└─────────────────────────────────────────────────────┘
```

## Schema Normalizado

```json
{
  "symbol": "EURUSD",
  "display_name": "EUR/USD",
  "price": 1.0842,
  "change_pct_1d": -0.12,
  "change_1d_abs": -0.0013,
  "high_1d": 1.0871,
  "low_1d": 1.0821,
  "open_1d": 1.0855,
  "prev_close": 1.0855,
  "volume": 0,
  "market_state": "REGULAR",
  "source": "yahoo_finance",
  "delay_minutes": 15,
  "timestamp": "2026-04-10T14:30:00Z",
  "trend_1d": "DOWN",
  "alert_level": "NORMAL"
}
```

## Métricas Calculadas

### Trend 1D
| Valor | Condición |
|-------|-----------|
| `UP` | cambio_1d > 0.1% |
| `DOWN` | cambio_1d < -0.1% |
| `FLAT` | entre -0.1% y 0.1% |

### Alert Level
| Nivel | Condición Forex | Condición Índices |
|-------|----------------|------------------|
| `NORMAL` | < 1% | < 2% |
| `WATCH` | > 1% | > 2% |
| `ALERT` | > 2% o cualquier > 3% | > 3% |

## Endpoints Webhook

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/webhook/prices` | GET | Snapshot completo formateado |
| `/webhook/prices-raw` | GET | JSON normalizado completo |
| `/webhook/prices-alerts` | GET | Solo instrumentos con WATCH/ALERT |
| `/webhook/price/{symbol}` | GET | Precio de instrumento específico |
| `/webhook/price-alert` | POST | Alerta (lo consume Módulo 7) |

## Archivos de Cache

| Archivo | Contenido |
|---------|-----------|
| `prices_latest.json` | Datos completos normalizados |
| `prices_snapshot.txt` | Texto formateado para LLM |
| `prices_alerts.json` | Solo instrumentos en alerta |

## Upgrade Futuro

Para cambiar a Polygon.io o Twelve Data:
1. Crear nuevo Feed Adapter con la nueva API
2. El Normalizer permanece igual (schema estándar)
3. Cache y Webhooks no cambian

**No se reescribe nada excepto el Feed Adapter.**
