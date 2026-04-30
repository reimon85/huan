---
name: market-context
description: "Proactivo market data fetching — detecta activos mencionados y fetchea precios/datos automáticamente sin pedirlo explícitamente."
version: 1.1.0
tags: [trading, market-data, proactive, crypto]
triggers:
  - asset_mentioned: true
---

# Market Context — Fetcheo Proactivo

## Regla General

Cuando el usuario menciona un activo en conversación, el agente debe:

1. **Detectar** el/los activos mencionados
2. **Fetchear** datos relevantes según instrumento
3. **Adjuntar** el contexto al análisis subsiguiente

**Importante:** NO esperar a que el usuario pida "el precio" — mencionarlo es trigger suficiente.

## Activos Implementados

### Crypto (Binance — sin API key)

```python
get_crypto_price(symbol="BTC")       # spot price + 24h stats individual
get_crypto_prices(symbols=["BTC","ETH","SOL"])  # batch
```

Retorna: price, bid/ask, spread, change_24h%, volume_24h, high/low, funding_rate (futures)

### Trigger Phrases (auto-detect)

- "quiero operar BTC"
- "que opinás de ETH"
- "analicemos SOL"
- "como viene BTC"
- "estoy siguiendo [CRYPTO]"
- Cualquier mención de ticker o nombre de activo en contexto de trading

## Comportamiento

```
Usuario: "quiero operar BTC que te parece?"

Agente:
  → Detecta: BTC mencionado
  → Fetchea: get_crypto_price("BTC")
  → Analiza con ese contexto
  → Respuesta: "BTC está en $75,753 (-1.59% 24h)..."
```

## Providers Implementados

| Instrumento | Provider | Status | API Key |
|-------------|----------|--------|---------|
| Crypto spot | Binance (ccxt) | ✅ Activo | No requerida |
| Crypto futures | Hyperliquid | 🔜 Pendiente | - |

## Próximos Providers

- **Hyperliquid** — perpetuals con funding rate real, orderbook depth
- **Forex** — yfinance o API directa
- **Futuros US** — yfinance (ES, NQ, CL, GC)
