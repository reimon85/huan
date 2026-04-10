---
title: Módulo 9C — Crypto Global Metrics
type: article
branch: trading_systems
tags: n8n,modulo-9c,crypto,coingecko,dominance,global
summary: Workflow de métricas globales de crypto desde CoinGecko
---

# Módulo 9C — Crypto Global Metrics

**Archivo**: `workflows/crypto_global_metrics.json`
**Trigger**: Cada hora, 24/7
**Fuente**: [CoinGecko API](https://www.coingecko.com/api) (gratuitos, sin API key)

## Endpoints

| Endpoint | Datos |
|----------|-------|
| `/api/v3/global` | Market cap total, volume, dominance, etc. |
| `/api/v3/simple/price` | BTC, ETH, SOL prices + 24h change |

**Rate Limit**: 30 calls/min (sin problema con llamadas cada hora)

## Schema Normalizado

```json
{
  "timestamp": "2026-04-10T14:00:00Z",
  "total_market_cap_usd": 2580000000000,
  "total_volume_24h_usd": 98000000000,
  "btc_dominance": 52.3,
  "eth_dominance": 17.8,
  "altcoin_dominance": 29.9,
  "market_cap_change_24h_pct": 1.2,
  "active_cryptos": 12450,
  "vol_to_mcap_ratio": 0.038,
  "regime": "NEUTRAL",
  "btc_price": { "usd": 67400, "change_24h": 2.1 },
  "eth_price": { "usd": 3520, "change_24h": 1.8 },
  "sol_price": { "usd": 178, "change_24h": 4.2 },
  "signals": [],
  "warnings": []
}
```

## Regímenes de Mercado

| Régimen | Condición | Interpretación |
|---------|-----------|----------------|
| `BTC_SEASON` | btc_dominance > 55% | Capital concentrado en BTC |
| `ETH_SEASON` | eth_dominance > 20% + market cap change > 0 | Ethereum liderando |
| `ALT_SEASON` | btc_dominance < 45% | Dinero rotando a altcoins |
| `RISK_OFF` | market_cap_change_24h < -3% | Fuga general de crypto |
| `NEUTRAL` | Default | Sin régimen claro |

## Señales Detectadas

| Señal | Condición | Interpretación |
|-------|-----------|----------------|
| Dominance BTC↑ + Precio↓ | BTC dom sube, precio baja | Capitulación de alts, posible bottom |
| Dominance BTC↓ rápido | Rotación agresiva | Alt season incoming |
| Vol/MCap > 0.15 | Ratio extremo | Evento de alta volatilidad |

## Endpoints Webhook

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/webhook/crypto-global` | GET | Métricas globales formateadas |

## Archivos de Cache

| Archivo | Contenido |
|---------|-----------|
| `crypto_global_latest.json` | Datos estructurados |
| `crypto_global_latest.txt` | Texto formateado |

## Ejemplo de Output

```
CRYPTO GLOBAL — 10 abril 2026 14:00
Fuente: CoinGecko

Market Cap Total: $2.58T (+1.2% 24h)
Volumen 24h: $98B | Ratio Vol/MCap: 0.038

DOMINANCE:
BTC: 52.3% | ETH: 17.8% | Alts: 29.9%

PRECIOS:
BTC: $67,400 (+2.1%) | ETH: $3,520 (+1.8%) | SOL: $178 (+4.2%)

Régimen actual: NEUTRAL
BTC dominance estable en 52%. Sin rotación clara hacia alts.
Mercado en modo espera con leve momentum alcista.

SEÑALES:
• SOL outperforming: +4.2% vs BTC +2.1% — posible rotación a mid-caps
```

## Integración

- **Consumido por**: Módulo 10 (Crypto Snapshot Aggregator)
- Útil para el briefing (Módulo 6) para contexto macro crypto
