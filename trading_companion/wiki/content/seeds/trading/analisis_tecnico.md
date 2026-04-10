---
title: Análisis Técnico
type: topic
branch: trading
tags: analisis-tecnico,chartismo,indicadores
summary: Estudio de gráficos y patrones para predecir movimientos de precios
---

# Análisis Técnico

El análisis técnico es el estudio del comportamiento del mercado a través de gráficos, con el objetivo de identificar patrones y tendencias para tomar decisiones de trading.

## Teoría de Dow

Charles Dow formuló los principios básicos del análisis técnico moderno:

1. **El precio lo descuenta todo**: Toda información disponible está reflejada en el precio
2. **Los precios se mueven en tendencias**: Las tendencias pueden ser alcistas, bajistas o laterales
3. **La historia se repite**: Los patrones gráficos tienden a repetirse

## Tipos de Gráficos

### Gráfico de Lineas
- Útil para ver la tendencia general
- Solo conecta precios de cierre

### Gráfico de Barras (OHLC)
- Muestra apertura, máximo, mínimo y cierre
- Mayor información que el de líneas

### Gráfico de Velas (Candlesticks)
- Representación visual del movimiento
- Permite identificar patrones de reversión

## Patrones Chartistas

### Patrones de Reversión Alcista

| Patrón | Descripción | Confirmación |
|--------|-------------|--------------|
| **Doble Suelo** | Dos mínimos similares | Ruptura de neckline |
| **Cabeza y Hombros Invertido** | Tres suelo con central más bajo | Ruptura de neckline |
| **Martillo** | Vela con cuerpo pequeño y sombra inferior larga | Cierre por encima del martillo |

### Patrones de Reversión Bajista

| Patrón | Descripción | Confirmación |
|--------|-------------|--------------|
| **Doble Techo** | Dos máximos similares | Ruptura de neckline |
| **Cabeza y Hombros** | Tres picos con central más alto | Ruptura de neckline |
| **Estrella Fugaz** | Vela con cuerpo pequeño y sombra superior larga | Cierre por debajo de la estrella |

### Patrones de Continuidad

- **Triángulos**: Simétrico, ascendente, descendente
- **Banderines**: Continuation after strong move
- **Rectángulos**: Consoldación lateral
- **Cuñas**: Similares a triángulos pero con inclinación

## Indicadores Técnicos

### Indicadores de Tendencia

```python
# Ejemplo conceptual de Media Móvil Simple (SMA)
def sma(prices: list[float], period: int) -> float:
    return sum(prices[-period:]) / period

# Media Móvil Exponencial (EMA)
def ema(prices: list[float], period: int, previous_ema: float = None) -> float:
    multiplier = 2 / (period + 1)
    if previous_ema is None:
        return sma(prices[-period:], period)
    return (prices[-1] * multiplier) + (previous_ema * (1 - multiplier))
```

- **SMA/EMA**: Medias móviles simples y exponenciales
- **MACD**: Moving Average Convergence Divergence
- **ADX**: Average Directional Index (fuerza de tendencia)

### Indicadores de Momentum

| Indicador | Descripción | Señal |
|-----------|-------------|-------|
| **RSI** | Relative Strength Index (0-100) | Sobrecompra >70, Sobreventa <30 |
| **Estocástico** | Compara cierre con rango | Cruce %K y %D |
| **CCI** | Commodity Channel Index | Lecturas extremas |

### Indicadores de Volatilidad

- **Bollinger Bands**: Media ± 2 desviaciones estándar
- **ATR**: Average True Range
- **Keltner Channels**: Canal basado en ATR

## Soportes y Resistencias

### Conceptos Fundamentales

- **Soporte**: Zona donde la demanda supera a la oferta
- **Resistencia**: Zona donde la oferta supera a la demanda
- **Role Reversal**: El soporte roto se convierte en resistencia

### Identificación de Niveles

1. Mínimos y máximos anteriores
2. Niveles de precio redondo (psicológicos)
3. Fibonacci retracements
4. Medias móviles importantes
5. Líneas de tendencia

## Divergencias

### Divergencia Regular

- **Alcista**: Precio hace nuevos mínimos, RSI hace mínimos más altos
- **Bajista**: Precio hace nuevos máximos, RSI hace máximos más bajos

### Divergencia Oculta

- **Alcista**: Precio hace mínimos más altos, RSI hace nuevos mínimos
- **Bajista**: Precio hace máximos más bajos, RSI hace nuevos máximos
