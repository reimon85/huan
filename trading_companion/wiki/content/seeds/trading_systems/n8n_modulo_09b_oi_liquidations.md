---
title: Módulo 9B — Crypto OI & Liquidations
type: article
branch: trading_systems
tags: n8n,modulo-9b,crypto,open-interest,liquidations,loris
summary: Workflow de Open Interest y liquidaciones desde Loris Tools
---

# Módulo 9B — Crypto Open Interest & Liquidations

**Archivo**: `workflows/crypto_oi_liquidations.json`
**Trigger**: Cada 15 minutos, 24/7
**Fuente**: [Loris Tools API](https://loris.tools) (gratuita, sin API key)

## Endpoints Utilizados

| Endpoint | Frecuencia | Datos |
|----------|------------|-------|
| `/oi` | 15 min | Open Interest por símbolo/exchange |
| `/liquidations` | 15 min | Liquidaciones recientes |
| `/volume` | 15 min | Volumen por símbolo/exchange |

## Open Interest — Schema

```json
{
  "symbol": "BTC",
  "exchanges": {
    "binance": 12500000000,
    "bybit": 8500000000,
    "okx": 6200000000
  },
  "total_oi_usd": 27200000000,
  "oi_change_1h_pct": 8.2,
  "oi_change_24h_pct": 12.5,
  "regime": "OI_RISING_PRICE"
}
```

## Liquidaciones — Schema

```json
{
  "total_liquidation_4h_usd": 45000000,
  "long_liquidations_4h": 32000000,
  "short_liquidations_4h": 13000000,
  "liquidation_concentration": [
    { "price": 67400, "side": "long", "size": 8500000 },
    { "price": 67200, "side": "long", "size": 5200000 }
  ]
}
```

## Regímenes de OI

| Régimen | Condición | Interpretación |
|---------|-----------|----------------|
| `OI_RISING_PRICE` | OI↑ + Precio↑ | Tendencia sana (posiciones nuevas long) |
| `OI_FALLING_PRICE` | OI↑ + Precio↓ | Capitulación (posiciones nuevas short) |
| `SHORT_SQUEEZE` | OI↓ + Precio↑ | Cierre de shorts empuja precio |
| `DELVERAGING` | OI↓ + Precio↓ | Cierre de posiciones, mercado limpiándose |
| `NEUTRAL` | Default | Sin régimen claro |

## Señales de Alerta

### Open Interest
| Señal | Condición | Interpretación |
|-------|-----------|----------------|
| OI > 10% 1h | BTC/ETH | Movimiento institucional grande |
| OI↑ + Precio↑ | Confirma | Tendencia saludable |
| OI↑ + Precio↓ | Alerta | Capitulación |

### Liquidaciones
| Señal | Condición | Interpretación |
|-------|-----------|----------------|
| Longs > $100M/1h | Capitulación | Pánico vendedor |
| Shorts > $50M/1h | Short squeeze | Rebote inminente |
| Concentración en precio | Zona interés | Posible soporte/resistencia |

## Endpoints Webhook

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/webhook/crypto-oi` | GET | Snapshot de OI |
| `/webhook/crypto-liquidations` | GET | Liquidaciones recientes |
| `/webhook/crypto-volume` | GET | Volumen |

## Archivos de Cache

| Archivo | Contenido |
|---------|-----------|
| `crypto_oi_latest.json` | OI actual |
| `crypto_liquidations.json` | Liquidaciones |
| `crypto_oi_history.json` | Histórico OI (rolling) |

## Ejemplo de Output

```
OI & LIQUIDACIONES — 10 abril 2026 14:30
Fuente: Loris Tools

OPEN INTEREST:
BTC OI: $28.5B (+8.2% 1h) → OI subiendo + precio subiendo = tendencia sana
ETH OI: $14.2B (+12.1% 1h) → ⚠️ ALERTA: cambio > 10%
SOL OI: $3.8B (+6.3% 1h) → Normal

LIQUIDACIONES ÚLTIMAS 4H:
Longs: $45M | Shorts: $28M
Mayor concentración: $67,400 (longs), $67,200 (longs)

SEÑAL OI: OVERHEATED_MOMENTUM
```

## Integración

- **Consumido por**: Módulo 10 (Crypto Snapshot Aggregator)
- **Para precio**: Consume del Módulo 8 (prices-raw)
