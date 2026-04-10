---
title: Sesgos Cognitivos
type: topic
branch: psicologia_trading
tags: psicologia,sesgos,cognitive-bias,emociones
summary: Errores sistemáticos en el pensamiento que afectan las decisiones de trading
---

# Sesgos Cognitivos en Trading

Los sesgos cognitivos son patrones de pensamiento predecibles que desvían nuestras decisiones de lo que sería lógicamente óptimo. En trading, estos sesgos pueden causar pérdidas significativas.

## ¿Por Qué Ocurren los Sesgos?

> "We are not thinking machines. We are feeling machines that think."
> — Joseph LeDoux

El cerebro humano evolucionó para tomar decisiones rápidas basándose en heuristics (atajos mentales), no para el análisis estadístico que requiere el trading.

## Principales Sesgos en Trading

### 1. Confirmation Bias (Sesgo de Confirmación)

**Definición**: Tendencia a buscar, interpretar y recordar información que confirme las creencias preexistentes.

**En Trading**:

| Situación | Respuesta Bias | Respuesta Objetiva |
|-----------|-----------------|---------------------|
| Abriste posición LONG | Ignorar malas noticias | Evaluar toda la información |
| Creés en tendencia | Buscar solo ejemplos a favor | Analizar también contraindicaciones |
| stop loss golpeado | "El mercado está mal" | Revisar si el análisis fue correcto |

**Cómo Combatirlo**:

- **Trading Plan**: Definir ANTES de operar qué constituye una señal válida
- **Journal**: Registrar exactamente por qué se entró, incluyendo la evidencia
- **Post-Mortem**: Revisar operaciones cerradas objetivamente
- **Contrarian**: Deliberadamente buscar evidencia en contra

```python
def pre_trade_check(trade_reason: dict, current_data: dict) -> bool:
    """
    Verificación antes de entrar para reducir confirmation bias.
    """
    # Escribir explícitamente por qué NO debería entrar
    reasons_not_to_trade = []

    if current_data['trend'] != trade_reason['expected_direction']:
        reasons_not_to_trade.append("Tendencia contradice dirección")

    if current_data['volume'] < average_volume * 0.5:
        reasons_not_to_trade.append("Volumen bajo - falta convicción")

    # Solo operar si las razones a favor superan las encontra
    strength = len(trade_reason['evidence_for']) - len(reasons_not_to_trade)

    return strength >= 2
```

### 2. Loss Aversion (Aversión a la Pérdida)

**Definición**: Las pérdidas duelen aproximadamente el doble de lo que agradan las ganancias equivalentes.

**Estadística Clave**:
- Pérdida de $100: -100 utilidad
- Ganancia de $100: +50 utilidad

**Implicación en Trading**:

```
Típico: Cerrar ganancias temprano, mantener pérdidas demasiado
Resultado: Muchas pequeñas ganancias, pocas grandes pérdidas
= Esperanza NEGATIVA
```

**El Problema del Break-Even**

Muchos traders mueven el stop a BE (break-even) demasiado rápido porque "no quieren perder".

```python
def should_move_stop_to_breakeven(
    current_profit_percent: float,
    target_profit_percent: float,
    time_in_trade: int,  # bars
    expected_holding_period: int
) -> tuple[bool, str]:
    """
    Decide si mover el stop a break-even.
    """
    # Criteria para mover a BE
    MIN_PROFIT_FOR_BE = 1.5  # 1.5R mínimo
    MIN_TIME_MULTIPLIER = 0.5  # Al menos 50% del tiempo esperado

    if current_profit_percent < MIN_PROFIT_FOR_BE:
        return False, f"Profit {current_profit_percent}% below minimum {MIN_PROFIT_FOR_BE}%"

    if time_in_trade < expected_holding_period * MIN_TIME_MULTIPLIER:
        return False, "Too early in expected holding period"

    # Todo OK
    return True, "Conditions met for BE move"
```

### 3. Recency Bias (Sesgo de lo Reciente)

**Definición**: Dar más peso a eventos recientes que a los históricos.

**En Trading**:
- Después de una racha ganadora: "Soy invencible"
- Después de una racha perdedora: "Nunca voy a ganar"

**El Problema de 3 Meses**

> Si tienes 3 meses malos, ¿eres mal trader?

Respuesta: No puedes saberlo. Necesitas años de datos.

**Solución: Journal de Largo Plazo**

```python
def calculate_performance_metrics(journal_entries: list[TradeEntry]) -> dict:
    """
    Calculate performance metrics over sufficient sample.
    """
    if len(journal_entries) < 100:
        return {
            'win_rate': None,
            'avg_win': None,
            'avg_loss': None,
            'sample_size_warning': "Need at least 100 trades for significance"
        }

    # Calculate metrics
    wins = [e for e in journal_entries if e.pnl > 0]
    losses = [e for e in journal_entries if e.pnl <= 0]

    return {
        'win_rate': len(wins) / len(journal_entries),
        'avg_win': sum(e.pnl for e in wins) / len(wins) if wins else 0,
        'avg_loss': sum(e.pnl for e in losses) / len(losses) if losses else 0,
        'expectancy': calculate_expectancy(wins, losses),
        'risk_reward': abs(sum(e.pnl for e in wins) / len(wins) /
                          (sum(e.pnl for e in losses) / len(losses))) if losses else None
    }
```

### 4. Anchoring (Anclaje)

**Definición**: Depender demasiado de la primera información recibida.

**En Trading**:

| Anclaje | Problema |
|---------|----------|
| Precio de entrada | Mantener posición perdedora "ya va a volver" |
| Máximo histórico | Vender cuando "ya ganó suficiente" |
| Precio psicológico | Ignorar señales en niveles "redondos" |

**Ejemplo de Anclaje Problemático**

```
Compraste ABC a $50
Precio baja a $45
Precio baja a $40
Precio baja a $35 → "En $50 parecía caro, en $35 es oportunidad"

ERROR: $35 no es "barato" intrínsecamente. Solo parece barato comparado a $50.
```

**Cómo Evitarlo**:

- Usar stops basados en EL MERCADO, no en tu entrada
- Revisar análisis sin mirar precio de entrada
- Establecer targets basados en reward:risk ratio

### 5. Overtrading (Negociação Excesiva)

**Definición**: Operar demasiado frecuentemente, usualmente por ansiedad.

**Causas**:

1. **Truncación de Riscos**: No poder tolerar la incertidumbre
2. **Boredom**: Necesidad de "hacer algo"
3. **Gambling mindset**: Buscar la emoción
4. **Commission bias**: Creer que más operaciones = más ganancias

**Señales de Warning**:

- > 5-10 operaciones por semana (depende del estilo)
- Sentir ansiedad cuando no hay posiciones
- Reducir tamaño cuando se está "en racha fría"

```python
def trading_frequency_analysis(trades: list[Trade], days: int = 30) -> dict:
    """
    Analiza si la frecuencia de trading es saludable.
    """
    total_trades = len(trades)
    avg_trades_per_week = (total_trades / days) * 7

    # Operar mucho no significa ganar mucho
    winning_trades = [t for t in trades if t.pnl > 0]
    losing_trades = [t for t in trades if t.pnl <= 0]

    # Calcular si el overtrading está afectando performance
    if len(losing_trades) > len(winning_trades) * 1.5:
        overtrading_probable = True
        reason = "High ratio of losses suggests impulse trading"
    else:
        overtrading_probable = False
        reason = None

    return {
        'trades_per_week': avg_trades_per_week,
        'win_rate': len(winning_trades) / total_trades if total_trades > 0 else 0,
        'overtrading_probable': overtrading_probable,
        'reason': reason,
        'recommendation': "Reduce" if avg_trades_per_week > 10 else "Normal"
    }
```

### 6. Sunk Cost Fallacy (Costo Hundido)

**Definición**: Continuar con una decisión por el tiempo/recursos ya invertidos.

**En Trading**:

```
Ya invertí $10,000 en esta acción →
Tengo que esperar a recuperarlo →
Mientras más espero, más pierdo →
pero "ya invertí tanto" →
¡FALLA!
```

**Solución**:

> "No compares el precio de entrada con el precio actual. Compara el precio actual con el precio de HOY."

```python
def should_hold_position(
    current_price: float,
    stop_loss: float,
    time_in_trade: int,
    initial_reason: str,
    current_market_state: dict
) -> tuple[bool, str]:
    """
    Decide si mantener posición basada en MERCADO, no en entrada.
    """
    # Evaluar razones ORIGINALES para entrar
    original_reasons_still_valid = True

    # El mercado cambió?
    if current_market_state['trend'] != 'bullish':
        original_reasons_still_valid = False

    # Precio cerca del stop?
    if current_price <= stop_loss * 1.05:  # 5% del stop
        return False, "Approaching stop loss"

    # Si las razones ya no son válidas, vender
    if not original_reasons_still_valid:
        return False, "Original thesis invalidated"

    return True, "Thesis intact"
```

### 7. Hindsight Bias (Sesgo de la Visión Perfecta)

**Definición**: "Saber" después que iba a pasar.

**Manifestación**:

> "Sabía que iba a bajar" - (pero no actúaste sobre ello)
> "Pude haber ganado 10x" - (pero no entradaste)

**Por Qué es Peligroso**:

- Sobreestimar habilidades
- Creer que el mercado es más predecible
- Frustración y decisiones impulsivas

**Solución**:

- Comparar decisiones con expectativas EN EL MOMENTO
- No confundir suerte con skill
- Mantener registro de predicciones Y sus razones

## Tabla Resumen de Sesgos

| Sesgo | Síntomas | Solución |
|-------|----------|----------|
| Confirmation | Ignorar señales en contra | Checklist pre-trade |
| Loss Aversion | Cortar ganancias rápido | Rules-based exit |
| Recency | Reaccionar a racha reciente | Stats de largo plazo |
| Anchoring | Comparar con entrada |忘记入场价 |
| Overtrading | Muchas operaciones | Trading plan rígido |
| Sunk Cost | Mantener perdedores | Mercado vs entrada |
| Hindsight | "Sabía que pasaría" | Registro de expectativas |

## Técnicas de Mitigación

### 1. Trading Plan Escrito

```
┌─────────────────────────────────────────┐
│           TRADING PLAN                   │
├─────────────────────────────────────────┤
│ Estrategia: Mean Reversion en índices    │
│ Timeframe: 4H                            │
│ Condiciones de entrada:                  │
│   □ RSI < 30                            │
│   □ Precio cerca de soporte               │
│   □ Confluencia con MA 200               │
│                                         │
│ Tamaño: 2% riesgo                        │
│ Stop: 1.5x ATR desde entrada            │
│ Target: 2:1 reward:risk                  │
│                                         │
│ NO operar si:                            │
│   □ News de alto impacto en 24h          │
│   □ Drawdown semanal > 3%                │
└─────────────────────────────────────────┘
```

### 2. Mindfulness y Trading

```python
EMOTION_CHECKLIST = [
    "¿Estoy operando por aburrimiento?",
    "¿Estoy tratando de recuperar pérdidas?",
    "¿Mi posición es más grande por emoción?",
    "¿Estoy verificando el precio constantemente?",
    "¿Siento ansiedad si no estoy en el mercado?",
]

def pre_trade_emotion_check() -> bool:
    """
    Verificación emocional antes de operar.
    Return True si está OK para tradear.
    """
    # Solo si TODAS las respuestas son "no"
    # Si alguna es "sí", no tradear
    # Esperar a estar en estado neutral
    pass
```

### 3. Revisión Semanal Estructurada

| Pregunta | Focus |
|----------|-------|
| ¿Seguí mi plan? | Discipline |
| ¿Mis razones eran válidas? | Analysis |
| ¿Métricas mejoran? | Progress |
| ¿Emociones afectaron? | Psychology |

## Conclusión

> "The market is a device for transferring money from the active to the patient."
> — Warren Buffett

Los sesgos cognitivos son naturales pero mitigables. La clave es:

1. **Reconocerlos**: El primer paso es saber que existen
2. **Crear sistemas**: Reglas que no dependen de emociones
3. **Medir objetivamente**: Stats de largo plazo vs sensaciones
4. **Aceptar imperfección**: No serás perfecto, pero puedes mejorar
