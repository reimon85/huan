---
title: Mean Reversion
type: topic
branch: trading_systems
tags: mean-reversion,sobrecompra,sobreventa,bandas
summary: Estrategias que explotan el retorno del precio a su valor promedio
---

# Mean Reversion

Mean Reversion es una estrategia que asume que los precios tienden a volver a su promedio histórico o "mean" después de moverse excesivamente lejos de él.

## Teoría de Mean Reversion

### Premisa Fundamental

> Los precios oscilan alrededor de un valor justo. Las desviaciones extremas son temporales.

### Conceptos Clave

- **Mean (Media)**: Valor promedio del precio en un período
- **Desviación**: Distancia del precio respecto a la media
- **Regresión a la media**: Tendencia a volver al promedio

## Indicadores de Mean Reversion

### Bollinger Bands

```python
def bollinger_bands(prices: list[float], period: int = 20, std_dev: float = 2.0) -> tuple:
    """
    Calcula las Bandas de Bollinger.

    Args:
        prices: Lista de precios de cierre
        period: Período para la media móvil
        std_dev: Número de desviaciones estándar

    Returns:
        (upper_band, middle_band, lower_band)
    """
    if len(prices) < period:
        return None, None, None

    # Media móvil simple
    middle = sum(prices[-period:]) / period

    # Desviación estándar
    variance = sum((p - middle) ** 2 for p in prices[-period:]) / period
    std = variance ** 0.5

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return upper, middle, lower
```

### Interpretación

| Posición del Precio | Señal |
|---------------------|-------|
| Cerca de banda superior | Posible sobrecompra |
| Cerca de banda inferior | Posible sobreventa |
| Cruce de banda | Posible reversión |

### RSI (Relative Strength Index)

```python
def calculate_rsi(prices: list[float], period: int = 14) -> float:
    """
    Calcula el RSI.

    Returns:
        Valor RSI entre 0-100
    """
    if len(prices) < period + 1:
        return 50.0

    # Calcular cambios
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]

    # Separar ganancias y pérdidas
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]

    # Promedios
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

### Zona de Sobrecompra/Sobreventa

| RSI | Interpretación |
|-----|----------------|
| > 70 | Sobrecompra, posible venta |
| < 30 | Sobreventa, posible compra |
| > 80 | Extremo, fuerte señal de venta |
| < 20 | Extremo, fuerte señal de compra |

## Estrategias de Mean Reversion

### Estrategia 1: Bollinger Band Bounce

```
Upper Band (2 std)
      │
      │  ╭───╮
      │  │   │ ← Venta aquí
      │  ╰───╯
 SMA ──────●─────────────── Mean
      │  ╭───╮
      │  │   │ ← Compra aquí
      │  ╰───╯
Lower Band (-2 std)
```

**Reglas**:
1. Precio toca banda inferior → Compra
2. Precio toca banda superior → Venta
3. Stop: Más allá del siguiente swing
4. Target: Media móvil (SMA)

### Estrategia 2: RSI Extreme

**Condiciones de Compra**:
- RSI < 30 (sobreventa extrema)
- RSI cruza hacia arriba > 30
- Confirmación con vela alcista

**Condiciones de Venta**:
- RSI > 70 (sobrecompra extrema)
- RSI cruza hacia abajo < 70
- Confirmación con vela bajista

### Estrategia 3: Gap Reversion

Los gaps de precios frecuentemente se llenan (rellenan).

```
│
│     ╭───╮  ← Gap向上
│     │ G │     ↑
│     ╰───╯     │ Llenar gap
│     │         │
│     ╰─────────╯  Target = Origen del gap
```

## Condiciones de Mercado

### Mercados Adecuados

| Condición | Suitability |
|-----------|-------------|
| Rango lateral | Óptimo |
| Baja volatilidad | Bueno |
| Alta volatilidad | Cautela |
| Tendencia fuerte | Peligroso |

### Filtros de Tendencia

Para evitar trades contrarios a la tendencia:

```python
def trend_filter(prices: list[float], short_period: int = 20, long_period: int = 50) -> str:
    """
    Determina la tendencia usando dos medias móviles.

    Returns:
        'uptrend', 'downtrend', o 'range'
    """
    if len(prices) < long_period:
        return 'unknown'

    short_ma = sum(prices[-short_period:]) / short_period
    long_ma = sum(prices[-long_period:]) / long_period

    # Calcular pendiente de la MA larga
    long_ma_prev = sum(prices[-(long_period+5):-5]) / long_period

    if short_ma > long_ma and long_ma > long_ma_prev:
        return 'uptrend'
    elif short_ma < long_ma and long_ma < long_ma_prev:
        return 'downtrend'
    else:
        return 'range'
```

## Gestión de Riesgo

### Position Sizing Adaptativo

```python
def calculate_mean_reversion_size(
    account: float,
    risk_percent: float,
    entry: float,
    stop: float,
    volatility: float
) -> float:
    """
    Tamaño de posición con ajuste por volatilidad.

    Args:
        volatility: ATR actual como medida de volatilidad
    """
    base_risk = account * risk_percent

    # Ajustar por volatilidad
    # Más volatilidad = menor posición
    vol_adjustment = 1.0 / (volatility / 20)  # Normalizado a ATR=20

    adjusted_risk = base_risk * min(vol_adjustment, 1.5)

    risk_per_unit = abs(entry - stop)

    return adjusted_risk / risk_per_unit
```

## Tiempo de Exposición

### Estadísticas de Holds

| Estrategia | Tiempo Promedio |
|-----------|-----------------|
| Bollinger Band Bounce | 1-5 días |
| RSI Extreme | 3-10 días |
| Gap Reversion | 1-7 días |

### Time decay
En opciones, el tiempo работает против posiciones largas de mean reversion.

## Ejemplo de Sistema Completo

```python
class MeanReversionSystem:
    def __init__(self, lookback: int = 20, std_dev: float = 2.0):
        self.lookback = lookback
        self.std_dev = std_dev

    def generate_signal(self, prices: list[float]) -> str | None:
        if len(prices) < self.lookback:
            return None

        upper, middle, lower = bollinger_bands(prices, self.lookback, self.std_dev)
        current = prices[-1]
        rsi = calculate_rsi(prices)

        # Señal de compra
        if current <= lower and rsi < 30:
            return 'buy'

        # Señal de venta
        if current >= upper and rsi > 70:
            return 'sell'

        return None

    def calculate_stop(self, prices: list[float], entry: float, direction: str) -> float:
        atr = calculate_atr(prices)
        if direction == 'buy':
            return entry - (atr * 1.5)
        else:
            return entry + (atr * 1.5)

    def calculate_target(self, entry: float, stop: float, direction: str) -> float:
        risk = abs(entry - stop)
        if direction == 'buy':
            return entry + (risk * 2)  # 2:1 ratio
        else:
            return entry - (risk * 2)
```
