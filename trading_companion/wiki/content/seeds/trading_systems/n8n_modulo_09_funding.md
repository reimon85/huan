---
title: Módulo 9A — Crypto Funding Rates
type: article
branch: trading_systems
tags: n8n,modulo-9a,crypto,funding,loris
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

## Señales Detectadas

| Señal | Condición | Interpretación | Urgencia |
|-------|-----------|----------------|----------|
| **Alta Funding Positivo** | avg_rate > 0.05% | Muchos longs pagando → posible corrección | Alta |
| **Funding Negativo Extremo** | avg_rate < -0.03% | Shorts pagando → posible rebote | Alta |
| **Divergencia** | max_spread > 0.08% | Desacuerdo institucional | Media |

## Endpoints

| Endpoint | Descripción |
|----------|-------------|
| `/webhook/funding` | Snapshot formateado |
| `/webhook/funding-raw` | JSON completo |
| `/webhook/funding-signals` | Solo señales activas |
| `/webhook/funding/{symbol}` | Símbolo específico |

**Alerta**: `POST /webhook/crypto-alert` (urgencia alta)

## Ejemplo

```
BTC: Binance 0.08% | Bybit 0.12% | OKX 0.07% | HL 0.15%
→ Avg: 0.10% (anualizado 36.5%) | Sesgo: POSITIVE
```
