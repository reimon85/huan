---
title: Indicadores Técnicos
type: topic
branch: data_analysis
tags: indicadores,osciladores,trend
summary: Indicadores matemáticos derivados del precio para análisis técnico
---

# Indicadores Técnicos

Los indicadores técnicos son cálculos matemáticos basados en el precio, volumen o interés abierto de un instrumento, utilizados para predecir movimientos futuros.

## Clasificación de Indicadores

### Por Función

| Tipo | Función | Ejemplos |
|------|---------|----------|
| **Tendencia** | Identificar dirección | MA, MACD, ADX |
| **Momentum** | Velocidad del movimiento | RSI, Estocástico, CCI |
| **Volatilidad** | Amplitud de movimientos | Bollinger, ATR |
| **Volumen** | Presión compradora/vendedora | OBV, Volume Profile |

## Medias Móviles

### Tipos

```python
def sma(prices: list[float], period: int) -> float:
    """Simple Moving Average"""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def ema(prices: list[float], period: int, previous_ema: float = None) -> float:
    """Exponential Moving Average"""
    multiplier = 2 / (period + 1)
    if previous_ema is None:
        return sma(prices, period)
    return (prices[-1] * multiplier) + (previous_ema * (1 - multiplier))


def wma(prices: list[float], period: int) -> float:
    """Weighted Moving Average"""
    if len(prices) < period:
        return None
    weights = list(range(1, period + 1))
    weighted_sum = sum(p * w for p, w in zip(prices[-period:], weights))
    return weighted_sum / sum(weights)
```

### Aplicaciones

- **Crossover systems**: Cruce de medias como señales
- **Dynamic support/resistance**: Precio respeta la MA
- **Trend identification**: Precio arriba/abajo de MA

## MACD (Moving Average Convergence Divergence)

### Componentes

```python
def calculate_macd(
    prices: list[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> tuple:
    """
    Calcula MACD.

    Returns:
        (macd_line, signal_line, histogram)
    """
    # Calcular EMAs
    ema_fast = None
    ema_slow = None
    macd_values = []

    for i in range(len(prices)):
        ema_fast = ema(prices[:i+1], fast_period, ema_fast)
        ema_slow = ema(prices[:i+1], slow_period, ema_slow)

        if ema_fast is not None and ema_slow is not None:
            macd_values.append(ema_fast - ema_slow)

    if len(macd_values) < signal_period:
        return None, None, None

    # Signal line = EMA del MACD
    signal = None
    for i in range(len(macd_values)):
        signal = ema(macd_values[:i+1], signal_period, signal)

    histogram = macd_values[-1] - signal if signal else 0

    return macd_values[-1], signal, histogram
```

### Interpretación

| Condición | Señal |
|-----------|-------|
| MACD > 0, Histograma positivo | Momentum alcista |
| MACD < 0, Histograma negativo | Momentum bajista |
| MACD cruza arriba de Signal | Señal de compra |
| MACD cruza abajo de Signal | Señal de venta |

## RSI (Relative Strength Index)

### Implementación Detallada

```python
def calculate_rsi_detailed(
    prices: list[float],
    period: int = 14
) -> dict:
    """
    Calcula RSI con información adicional.

    Returns:
        Dict con RSI, ganancias/pérdidas promedio, etc.
    """
    if len(prices) < period + 1:
        return {'rsi': 50, 'avg_gain': 0, 'avg_loss': 0}

    # Calcular cambios
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(prices[i] - prices[i-1])

    # Primeros promedios (SMA)
    gains = [d if d > 0 else 0 for d in deltas[:period]]
    losses = [-d if d < 0 else 0 for d in deltas[:period]]

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    # Suavizar con EMA para valores posteriores
    for i in range(period, len(deltas)):
        gain = deltas[i] if deltas[i] > 0 else 0
        loss = -deltas[i] if deltas[i] < 0 else 0

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    return {
        'rsi': rsi,
        'avg_gain': avg_gain,
        'avg_loss': avg_loss,
        'rs': rs if avg_loss > 0 else float('inf')
    }
```

### Señales de Trading

- **RSI < 30**: Sobreventa extrema
- **RSI > 70**: Sobrecompra extrema
- **RSI < 20**: Lectura extremadamente sobrevendida
- **RSI > 80**: Lectura extremadamente sobrecomprada

## Estocástico

### Fórmula

```python
def calculate_stochastic(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    k_period: int = 14,
    d_period: int = 3
) -> tuple:
    """
    Calcula Oscilador Estocástico.

    Returns:
        (k_percent, d_percent)
    """
    if len(closes) < k_period:
        return None, None

    # %K = (Cierre - Mínimo más bajo) / (Máximo más alto - Mínimo más bajo) × 100
    lowest_lows = []
    highest_highs = []

    for i in range(k_period - 1, len(closes)):
        window_highs = highs[i - k_period + 1:i + 1]
        window_lows = lows[i - k_period + 1:i + 1]

        highest_highs.append(max(window_highs))
        lowest_lows.append(min(window_lows))

    k_values = []
    for i in range(len(closes) - k_period + 1):
        c = closes[k_period - 1 + i]
        ll = lowest_lows[i]
        hh = highest_highs[i]

        if hh == ll:
            k_values.append(50)
        else:
            k = ((c - ll) / (hh - ll)) * 100
            k_values.append(k)

    # %D = SMA de %K
    if len(k_values) < d_period:
        return k_values[-1] if k_values else None, None

    d = sum(k_values[-d_period:]) / d_period

    return k_values[-1], d
```

### Interpretación

| Zona | Rango | Señal |
|------|-------|-------|
| Sobrecompra | > 80 | Posible venta |
| Sobreventa | < 20 | Posible compra |
| %K cruza %D arriba | - | Compra |
| %K cruza %D abajo | - | Venta |

## ATR (Average True Range)

### Cálculo del True Range

```python
def true_range(high: float, low: float, close: float, prev_close: float) -> float:
    """
    Calcula True Range para un período.
    """
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    return max(tr1, tr2, tr3)


def calculate_atr(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 14
) -> float:
    """
    Calcula Average True Range.
    """
    if len(closes) < period + 1:
        return None

    true_ranges = []
    for i in range(1, len(closes)):
        tr = true_range(highs[i], lows[i], closes[i], closes[i-1])
        true_ranges.append(tr)

    # Primera ATR es SMA del primer período
    atr = sum(true_ranges[:period]) / period

    # Suavizar con EMA
    for i in range(period, len(true_ranges)):
        atr = (atr * (period - 1) + true_ranges[i]) / period

    return atr
```

### Usos del ATR

1. **Stop Loss**: 1.5-2 × ATR
2. **Position Sizing**: Ajustar por volatilidad
3. **Confirmación de Breakouts**: ATR alto indica fuerza

## ADX (Average Directional Index)

### Cálculo

```python
def calculate_adx(highs, lows, closes, period: int = 14) -> float:
    """
    Calcula ADX para medir fuerza de tendencia.

    Returns:
        ADX value (0-100)
    """
    # +DM y -DM
    plus_dm = []
    minus_dm = []

    for i in range(1, len(highs)):
        high_diff = highs[i] - highs[i-1]
        low_diff = lows[i-1] - lows[i]

        if high_diff > low_diff and high_diff > 0:
            plus_dm.append(high_diff)
        else:
            plus_dm.append(0)

        if low_diff > high_diff and low_diff > 0:
            minus_dm.append(low_diff)
        else:
            minus_dm.append(0)

    # Suavizar DM y calcular DI
    atr = calculate_atr(highs, lows, closes, period)

    if atr is None or atr == 0:
        return 0

    plus_di = (sum(plus_dm[-period:]) / period / atr) * 100
    minus_di = (sum(minus_dm[-period:]) / period / atr) * 100

    # DX
    if plus_di + minus_di == 0:
        dx = 0
    else:
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100

    # ADX = EMA de DX
    return dx  # Simplified - real implementation needs EMA smoothing
```

### Interpretación

| ADX | Fuerza de Tendencia |
|-----|---------------------|
| 0-20 | Sin tendencia / Rango |
| 20-40 | Tendencia débil |
| 40-60 | Tendencia moderada |
| 60-80 | Tendencia fuerte |
| 80-100 | Tendencia muy fuerte |

## Volumen

### OBV (On-Balance Volume)

```python
def calculate_obv(closes: list[float], volumes: list[float]) -> list[float]:
    """
    Calcula On-Balance Volume.
    """
    obv = [0]

    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])

    return obv
```

### VWAP (Volume Weighted Average Price)

```python
def calculate_vwap(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float]
) -> float:
    """
    Calcula VWAP para el día actual.
    """
    typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
    cumulative_tp_vol = sum(t * v for t, v in zip(typical_prices, volumes))
    cumulative_vol = sum(volumes)

    if cumulative_vol == 0:
        return typical_prices[-1]

    return cumulative_tp_vol / cumulative_vol
```

## Combinación de Indicadores

### Sistema Multi-Timeframe

```python
def multi_timeframe_analysis(
    daily_prices: list[float],
    weekly_prices: list[float]
) -> dict:
    """
    Combina análisis de múltiples timeframes.
    """
    # Tendencia semanal (largo plazo)
    weekly_ema_fast = ema(weekly_prices, 8)
    weekly_ema_slow = ema(weekly_prices, 21)
    weekly_trend = 'up' if weekly_ema_fast > weekly_ema_slow else 'down'

    # Señales diarias (corto plazo)
    daily_rsi = calculate_rsi_detailed(daily_prices)
    daily_ema_fast = ema(daily_prices, 8)
    daily_ema_slow = ema(daily_prices, 21)
    daily_trend = 'up' if daily_ema_fast > daily_ema_slow else 'down'

    # Confluence
    aligned = weekly_trend == daily_trend

    return {
        'weekly_trend': weekly_trend,
        'daily_trend': daily_trend,
        'daily_rsi': daily_rsi['rsi'],
        'aligned': aligned,
        'signal': 'strong_buy' if aligned and daily_rsi['rsi'] < 40 else
                  'strong_sell' if aligned and daily_rsi['rsi'] > 60 else
                  'neutral'
    }
```
