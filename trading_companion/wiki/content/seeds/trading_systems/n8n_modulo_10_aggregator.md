---
title: Módulo 10 — Crypto Snapshot Aggregator
type: article
branch: trading_systems
tags: n8n,modulo-10,crypto,aggregator,snapshot,regime
summary: Workflow orquestador que combina todos los datos crypto
---

# Módulo 10 — Crypto Snapshot Aggregator

**Archivo**: `workflows/crypto_snapshot_aggregator.json`
**Trigger**: Cada 30 minutos + Webhook (on-demand)
**Fuentes**: Módulos 9A, 9B, 9C, 8

## Propósito

Este módulo es el **agregador central** de todos los datos de crypto. Unifica funding rates, OI, liquidaciones, dominance y precio en un único snapshot coherente que consume el LLM.

```
┌─────────────────────────────────────────────────────────────┐
│                    MÓDULO 10 — AGGREGATOR                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  9A      │  │  9B      │  │  9C      │  │   8      │ │
│  │ Funding  │  │  OI/Liq  │  │  Global  │  │  Prices  │ │
│  │  Rates   │  │          │  │  Metrics  │  │  (BTC)   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │              │              │              │        │
│       └──────────────┼──────────────┼──────────────┘        │
│                      │              │                         │
│                      ▼              ▼                         │
│              ┌───────────────────────────────┐               │
│              │     SYNTHESIZE + REGIME      │               │
│              │   Detecta régimen + narrative │               │
│              └───────────────────────────────┘               │
│                              │                             │
│                              ▼                             │
│              ┌───────────────────────────────┐               │
│              │   CRYPTO MARKET SNAPSHOT    │               │
│              │    Formato LLM-friendly     │               │
│              └───────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Regímenes Detectados

| Régimen | Condiciones | Interpretación |
|---------|-------------|----------------|
| `BULLISH_MOMENTUM` | funding > 0.05% + OI↑ + dominance estable | Tendencia sana,钱的跟着走 |
| `OVERHEATED` | funding alto + OI↑ pero con divergencias | Corrección próxima |
| `CORRECTING` | funding positivo alto + OI↓ | Unwinding de posiciones |
| `PANIC` | liquidaciones long grandes + funding negativo | Pánico, buscar soportes |
| `ACCUMULATION` | funding negativo + OI↓ | Acumulación institucional |
| `SHORT_SQUEEZE` | funding negativo + OI↑ | Shorts siendo cazados |
| `NEUTRAL` | Default | Sin régimen claro |

## Lógica de Síntesis

```
SI funding positivo > 0.05% + OI subiendo + dominance estable
  → BULLISH_MOMENTUM

SI funding positivo > 0.05% + OI bajando
  → CORRECTING (potencial unwinding)

SI liquidaciones long > $100M + funding negativo
  → PANIC

SI funding negativo + OI subiendo
  → SHORT_SQUEEZE_POTENTIAL
```

## Schema de Output

```json
{
  "timestamp": "2026-04-10T14:30:00Z",
  "regime": "BULLISH_MOMENTUM",
  "confidence": "media",
  "key_signals": [
    "BTC funding 0.10% (anualizado 36%)",
    "BTC OI +8.2% en 1h",
    "ETH funding mixto 0.06%",
    "Long liquidations $45M 4h"
  ],
  "narrative": "Funding positivo elevado en BTC sugiere mercado sobrecalentado. OI subiendo confirma momentum pero divergencia en funding entre exchanges indica cautela. Liquidaciones moderadas sugieren neither panic nor euphoria.",
  "funding": { ... },
  "oi": { ... },
  "liquidations": { ... },
  "global": { ... },
  "prices": { ... }
}
```

## Endpoints Webhook

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/webhook/crypto-snapshot` | GET | Snapshot completo formateado (PRIMARY) |
| `/webhook/crypto-regime` | GET | Solo régimen + narrative |

## Ejemplo de Output Completo

```
CRYPTO MARKET SNAPSHOT — 10 abril 2026 14:30
RÉGIMEN ACTUAL: OVERHEATED (confianza: media)
Funding positivo elevado sugiere mercado sobrecalentado. OI subiendo
confirma momentum pero divergencia en funding entre exchanges indica cautela.

=== FUNDING RATES ===
BTC: Binance 0.08% | Bybit 0.12% | OKX 0.07% | HL 0.15%
    → Avg: 0.10% | Anualizado: 36.5% | Sesgo: POSITIVE
ETH: Binance 0.05% | Bybit 0.06% | OKX 0.04% | HL 0.10%
    → Avg: 0.0625% | Sesgo: MIXED
SOL: 0.18% ⚠️ — Anualizado 65%!

SEÑALES FUNDING:
⚠️ SOL: Funding 0.18% — mercado sobrecalentado long
⚠️ BTC: Hyperliquid 0.15% vs Binance 0.08% — divergencia institucional

=== OPEN INTEREST ===
BTC OI: $28.5B (+8.2% 1h) → Tendencia sana
ETH OI: $14.2B (+12.1% 1h) → ⚠️ ALERTA > 10%

=== LIQUIDACIONES 4H ===
Longs: $45M | Shorts: $28M
Niveles concentración: $67,400 (longs)

=== DOMINANCE & GLOBAL ===
BTC Dom: 52.3% (+0.2%) | ETH Dom: 17.8% (+0.1%)
Market Cap: $2.58T (+1.2% 24h)
Régimen global: NEUTRAL

=== PRECIOS ===
BTC: $67,400 (+2.1%) | ETH: $3,520 (+1.8%) | SOL: $178 (+4.2%)
```

## Integración con Briefing (Módulo 6)

El workflow actualizado del Módulo 6 ahora consume:

```
GET /webhook/crypto-snapshot
```

E incluye la sección `=== MERCADO CRYPTO ===` en el contexto enviado al LLM.

## Uso Directo

El agente conversacional puede llamar directamente a:

```
GET /webhook/crypto-snapshot
```

Para obtener el estado completo del mercado crypto en cualquier momento.
