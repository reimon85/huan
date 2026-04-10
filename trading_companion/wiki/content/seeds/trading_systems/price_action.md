---
title: Price Action
type: topic
branch: trading_systems
tags: price-action,soporte,resistencia,velas
summary: Trading basado en el movimiento puro del precio sin indicadores
---

# Price Action

Price Action es una metodología de trading que utiliza únicamente el movimiento del precio en los gráficos, sin dependence de indicadores técnicos. El trader lee e interpreta los patrones de las velas y la estructura del mercado.

## Fundamentos de Price Action

### Principios Básicos

1. **El precio es todo**: Toda la información está en el gráfico
2. **La historia se repite**: Los patrones tienen validez predecible
3. **Los mercados se mueven en ondas**: Impulso y reacción

### Ventajas

- No hay retroalimentación de indicadores (lag)
- Funciona en cualquier timeframe
- Aplicable a cualquier instrumento
- Reduce el ruido de múltiples indicadores

## Lectura de Velas (Candlesticks)

### Estructura de una Vela

```
        Open
        ┌─┐
        │ │ ← Cuerpo real (body)
        └─┘
       ╱   ╲ ← Sombras (wicks/shadows)
```

### Velas Básicas

| Vela | Características | Interpretación |
|------|-----------------|----------------|
| **Marubozu** | Sin sombras, cuerpo largo | Fuerte momentum |
| **Doji** | Apertura ≈ Cierre | Indecisión |
| **Martillo** | Sombra inferior larga | Posible reversión alcista |
| **Estrella Fugaz** | Sombra superior larga | Posible reversión bajista |

### Velas de Señal

#### Envolvente Alcista (Bullish Engulfing)
- Vela bajista pequeña seguida de vela alcista grande
- El cuerpo de la segunda vela "envuelve" a la primera
- **Señal de compra**

#### Envolvente Bajista (Bearish Engulfing)
- Vela alcista pequeña seguida de vela bajista grande
- El cuerpo de la segunda vela "envuelve" a la primera
- **Señal de venta**

#### Morning Star (Estrella de Mañana)
- 3 velas: larga bajista, corta indecisión, larga alcista
- **Patrón de reversión alcista**

#### Evening Star (Estrella de Tarde)
- 3 velas: larga alcista, corta indecisión, larga bajista
- **Patrón de reversión bajista**

## Estructura del Mercado

### Swing Highs y Swing Lows

```
        X ← Swing High
       / \
      /   \
     /     \       X ← Swing High superior
    X       X     / \
               \ /   \
                X     X ← Swing High menor
               / \
              /   \
             X     X ← Swing Low
```

### Tendencias

| Tendencia | Característica | Confirmación |
|-----------|-----------------|--------------|
| **Alcista** | Higher Highs, Higher Lows | Soportes crecientes |
| **Bajista** | Lower Highs, Lower Lows | Resistencias decrecientes |
| **Lateral** | igual highs y lows | Rango definido |

## Niveles Clave en Price Action

### Soporte y Resistencia

```
    ┌─────────┐
    │ Resisten│ ← Zona de oferta
    └─────────┘
       ↑
    Consolidación
       ↓
    ┌─────────┐
    │ Soporte │ ← Zona de demanda
    └─────────┘
```

### Cómo Identificar Niveles

1. **Máximos y mínimos anteriores**
2. **Precios redondos** (10, 50, 100, etc.)
3. **Aperturas y cierres de velas importantes**
4. **Zonas de reversión previas**
5. **Acumulación/distribución**

### Role Reversal

Cuando un soporte se rompe, frecuentemente se convierte en resistencia y viceversa.

## Pin Bars (Pinocchio Bars)

### Estructura

```
        │
        │ ← Mecha larga (nose)
        │
─────── ████████████████ ← Cuerpo pequeño
        │
        │ ← Mecha corta (tail)
```

### Características

- Mecha larga mínimo 2-3x el cuerpo
- Cuerpo pequeño (< 25% de la vela)
- Ubicación en extremos de movimientos

### Trading con Pin Bars

```
           │
    ┌───────╋────────┐  ← Zona de rechazo
    │                   │
    │                   │
─────                   │
    │                   │
    │                   │
    └───────╋────────────┘
            │
            ↓ Stop
```

## Inside Bars

### Definición
Una vela (o barras) contenidas completamente dentro del rango de la vela anterior.

### Tipos

- **Inside Bar simple**: 1 vela dentro de la anterior
- **Mother Bar**: La vela que contiene
- **Multiple Inside Bars**: Varias velas comprimidas

### Trading con Inside Bars

```
    ┌─────────┐  ← Mother Bar
    │         │
    │  ┌───┐  │  ← Inside Bar 1
    │  │   │  │
    │  │ ┌─┐│  │  ← Inside Bar 2
    │  │ │ ││  │
    │  │ └─┘│  │
    │  └───┘  │
    └─────────┘
```

### Confirmación

- Ruptura del rango de la mother bar
- Volumen por encima del promedio
- Confirmación con vela de seguimiento

## Breakouts y Fakeouts

### Tipos de Ruptura

| Tipo | Descripción | Trading |
|------|-------------|---------|
| **True Breakout** | Ruptura con seguimiento | Operar en dirección |
| **Fakeout** | Ruptura que revierte | Operar en contra |
| **No Breakout** | No llega a romper | Esperar |

### Cómo Diferenciarlos

1. **Volumen**: True breakouts tienen volumen alto
2. **Velocidad**: Verdaderas rupturas son rápidas
3. **Retesteo**: Los fakeouts frecuentemente re-testan
4. **Cierre**: El precio cierra decisively más allá del nivel

## Setups de Price Action

### Break of Structure (BOS)

```
    ↑ Higher Low
   / \
  /   \
 /     \     ↗ Higher High
/       \   /
        \ /
         X ← Previous low broken
```

### Changement of Character (CHoCH)

```
    ↑ Higher High
   / \
  /   \
 /     \
/       X ← Lower Low (changement!)
 \     /
  \   /
   \ /
    X ← Previous low
```

## Ejemplo de Trading Plan

```
1. IDENTIFICAR TENDENCIA
   - HCH/HCL (Higher Highs, Higher Lows)
   - Only trade in direction of trend

2. ESPERAR RETROCESO
   - Price pulls back to key level
   - Look for rejection candles

3. BUSCAR CONFIRMACIÓN
   - Pin bar, engulfing, or inside bar
   - Volume confirmation

4. EJECUTAR TRADE
   - Entry: After candle close
   - Stop: Beyond the swing high/low
   - Target: Previous structure
```
