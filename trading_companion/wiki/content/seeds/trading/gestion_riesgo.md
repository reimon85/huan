---
title: Gestión de Riesgo
type: topic
branch: trading
tags: riesgo,gestion-capital,position-sizing
summary: Estrategias para proteger el capital y limitar pérdidas
---

# Gestión de Riesgo

La gestión de riesgo es arguably el aspecto más importante del trading. Sin una gestión adecuada, incluso la mejor estrategia eventualmente fallará.

## Principios Fundamentales

### Regla del 1-2%

> **Nunca arriesgar más del 1-2% del capital en una sola operación**

Esta regla asegura que una racha perdedora no destruya la cuenta.

### Relación Riesgo/Beneficio

| Ratio R/B | Win Rate Requerida para BE |
|-----------|---------------------------|
| 1:1 | 50% |
| 1:2 | 33% |
| 1:3 | 25% |

**Ejemplo**: Con un ratio 1:2 y 40% de win rate:
- Esperanza = (0.4 × 2) - (0.6 × 1) = 0.2 (positivo)

## Position Sizing

### Fórmula de Position Size

```python
def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calcula el tamaño de posición en unidades.

    Args:
        account_balance: Capital total de la cuenta
        risk_per_trade: Porcentaje de riesgo (ej: 0.02 = 2%)
        entry_price: Precio de entrada
        stop_loss: Precio de stop loss

    Returns:
        Número de unidades a operar
    """
    risk_amount = account_balance * risk_per_trade
    risk_per_unit = abs(entry_price - stop_loss)
    position_size = risk_amount / risk_per_unit
    return position_size
```

### Ejemplo Práctico

- Cuenta: $10,000
- Riesgo: 2% = $200
- Entrada: $50.00
- Stop Loss: $48.50
- Riesgo por acción: $1.50
- **Position Size**: $200 / $1.50 = 133 acciones

## Tipos de Riesgo

### Riesgo de Mercado
La posibilidad de pérdidas debido a movimientos adversos del mercado.

**Mitigación**:
- Diversificación
- Cobertura (hedging)
- Stop losses

### Riesgo de Liquidez
Incapacidad de cerrar una posición al precio deseado.

**Mitigación**:
- Operar instrumentos líquidos
- Evitar posiciones grandes en mercados delgados

### Riesgo de Volatilidad
Movimientos de precio más amplios de lo esperado.

**Mitigación**:
- Reducir exposición antes de noticias
- Usar opciones para protección

### Riesgo de Apalancamiento
Las pérdidas se multiplican con el apalancamiento.

**Mitigación**:
- Usar apalancamiento bajo (máx 3-5x)
- Mantener margen libre suficiente

## Stop Losses

### Tipos de Stop Loss

| Tipo | Descripción | Uso |
|------|-------------|-----|
| **Fijo** | Precio exacto predeterminado | Estrategias discretas |
| **Porcentual** | % desde entrada |通用 |
| **Volatilidad** | Basado en ATR | Mercados volátiles |
| **Trailing** | Sigue el precio favorablemente | Tendencias |

### Colocación del Stop

1. **Por debajo/ariba del soporte/resistencia**
2. **Por debajo del mínimo/máximo anterior**
3. **Basado en volatilidad (ATR × 1.5-2)**
4. **Combinación de los anteriores**

## Kelly Criterion

### Fórmula

```
f* = (bp - q) / b

Donde:
f* = Fracción de capital a apostar
b = Probabilidad de ganancia (ratio neto)
p = Probabilidad de ganancia
q = Probabilidad de pérdida (1 - p)
```

### Implementación

```python
def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Calcula el porcentaje óptimo de capital según Kelly.

    Args:
        win_rate: Probabilidad de victoria (0-1)
        avg_win: Ganancia promedio en operaciones ganadoras
        avg_loss: Pérdida promedio en operaciones perdedoras

    Returns:
        Porcentaje óptimo de capital (0-1)
    """
    if avg_loss == 0:
        return 0

    b = avg_win / avg_loss  # Ratio de pago
    p = win_rate
    q = 1 - p

    kelly = (b * p - q) / b

    # Kelly fraccional (recomendado usar 25-50% de Kelly)
    return max(0, kelly * 0.5)
```

### Interpretación

- **Kelly = 0**: No operar (esperanza negativa)
- **Kelly < 0.25**: Conservador
- **Kelly 0.25-0.5**: Moderado
- **Kelly > 0.5**: Agresivo

## Drawdown y Recovery

### Conceptos

- **Drawdown**: Caída desde el máximo de la cuenta
- **Max Drawdown**: Mayor caída observada
- **Recovery Factor**: Ganancia total / Max Drawdown

### Recovery Table

| Max DD | Recovery Needed (% gain required) |
|--------|----------------------------------|
| 10% | 11% |
| 20% | 25% |
| 50% | 100% |
| 75% | 300% |

**Conclusión**: Es más fácil preservar capital que recuperarlo.

## Risk Management Checklist

- [ ] Position size calculada antes de cada operación
- [ ] Stop loss siempre definido antes de entrar
- [ ] Riesgo por operación ≤ 2% del capital
- [ ] Riesgo total de todas las posiciones abiertas ≤ 6%
- [ ] Relación R/B mínima de 1:1.5
- [ ] Esperanza positiva (win rate × avg win > avg loss)
