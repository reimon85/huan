---
title: Módulo 9A — Crypto Funding Rates
type: article
branch: trading_systems
tags: n8n,modulo-9a,crypto,funding,loris,bitcoin
summary: Workflow de funding rates de crypto desde Loris Tools
---

# Módulo 9A — Crypto Funding Rates

**Archivo**: `workflows/crypto_funding_rates.json`
**Trigger**: Cada 5 minutos, 24/7
**Fuente**: [Loris Tools API](https://api.loris.tools/funding) (gratuita, sin API key)

## Cobertura

| Aspecto | Detalle |
|---------|---------|
| **Exchanges** | 25+ CEX y DEX |
| **Principales** | Binance, Bybit, OKX, Hyperliquid, Drift, BingX, Bitget |
| **Símbolos** | BTC, ETH, SOL, XRP, DOGE, AVAX, MATIC, LINK |
| **Actualización** | Cada 60 segundos |

## Formato de Datos

```json
{
  "symbol": "BTC",
  "rates": {
    "binance": { "raw": 8, "pct": 0.0008, "annualized": 2.63 },
    "bybit":   { "raw": 12, "pct": 0.0012, "annualized": 3.94 },
    "okx":     { "raw": 7, "pct": 0.0007, "annualized": 2.30 },
    "hyperliquid": { "raw": 15, "pct": 0.0015, "annualized": 13.14 }
  },
  "avg_rate_primary": 0.0010,
  "max_spread": 0.0008,
  "consensus": "POSITIVE",
  "oi_rank": 1
}
```

**Nota**: Valores multiplicados x10,000 (valor 8 = 0.0008 = 0.08%)
**Hyperliquid**: Usa intervalo 1h, la API normaliza x8 para comparar.

## Señales Detectadas

### Alta Funding Positivo
- **Condición**: avg_rate_primary > 0.05% por período
- **Interpretación**: Muchos longs pagando a shorts → posible corrección
- **Urgencia**: Alta

### Funding Negativo Extremo
- **Condición**: avg_rate_primary < -0.03%
- **Interpretación**: Shorts pagando a longs → posible rebote
- **Urgencia**: Alta

### Divergencia Entre Exchanges
- **Condición**: max_spread > 0.08% entre exchanges principales
- **Interpretación**: Desacuerdo institucional → inestabilidad
- **Urgencia**: Media

### Normalización
- Compara con lectura anterior en cache
- Si venía de extremo y vuelve a rango normal → cambio de régimen

## Endpoints Webhook

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/webhook/funding` | GET | Snapshot formateado |
| `/webhook/funding-raw` | GET | JSON completo |
| `/webhook/funding-signals` | GET | Solo señales activas |
| `/webhook/funding/{symbol}` | GET | Funding de símbolo específico |
| `/webhook/crypto-alert` | POST | Alerta (lo consume Módulo 7) |

## Archivos de Cache

| Archivo | Contenido |
|---------|-----------|
| `funding_latest.json` | Datos normalizados actuales |
| `funding_snapshot.txt` | Texto formateado para LLM |
| `funding_history.json` | Últimas 12h (para detectar cambios) |
| `funding_signals.json` | Señales activas |

## Ejemplo de Output

```
FUNDING RATES — 10 abril 2026 14:30
Fuente: Loris Tools (25+ exchanges)

BTC: Binance 0.08% | Bybit 0.12% | OKX 0.07% | HL 0.15%
   → Sesgo: POSITIVE | Avg: 0.10% (anualizado 36.5%)

ETH: Binance 0.05% | Bybit 0.06% | OKX 0.04% | HL 0.10%
   → Sesgo: MIXED | Avg: 0.0625%

SEÑALES DETECTADAS:
⚠️ SOL: Funding positivo 0.18% (anualizado 65%) — mercado sobrecalentado long
⚠️ BTC: Divergencia 0.10% entre exchanges — cautela

LECTURA GLOBAL:
Funding positivo en 5/8 activos monitorizados. Hyperliquid consistently
más alto que otros exchanges. Mercado en modo OVERHEATED para shorts.
```

## Integración

- **Consumido por**: Módulo 10 (Crypto Snapshot Aggregator)
- **Alertas**: Módulo 7 (Critical Event Alert)
