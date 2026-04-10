---
title: Prompt 4 — Debrief Post-Sesión (Aprendizaje Estructurado)
type: article
branch: trading_systems
tags: prompt,debrief,post-sesion,aprendizaje,journal
summary: Protocolo de debrief estructurado para extraer aprendizaje de cada sesión de trading
---

# Prompt 4 — Debrief Post-Sesión (Aprendizaje Estructurado)

**Uso**: Al cierre de la sesión de trading, al final del día.
**Cuándo usarlo**: Después de cualquier sesión, con trades o sin ellos.
**Objetivo**: Extraer aprendizaje real, detectar patrones, actualizar la wiki.

---

## Template del Prompt

```
Sesión terminada. Vamos a hacer el debrief.

FECHA Y SESIÓN: [ej: "lunes 10 abril — sesión europea + americana"]
MERCADOS OPERADOS: [ej: EURUSD, CL futuros]
RESULTADO DEL DÍA: [ej: "+1.8R" / "-0.5R" / "sin trades"]

TRADES EJECUTADOS:
[Para cada trade, describe brevemente:
- Activo, dirección, resultado en R
- ¿El setup estaba en el plan de sesión o fue improvisado?
- ¿Seguiste las reglas de entrada y gestión?
- ¿Cómo te sentiste durante y después?]

TRADES NO EJECUTADOS (igual de importantes):
[Setups que viste pero no tomaste. ¿Por qué no entraste?
¿Fue disciplina correcta o miedo / duda injustificada?]

CONTEXTO DE MERCADO HOY:
[¿El mercado hizo lo que esperabas? ¿Hubo sorpresas?
¿El análisis de pre-sesión fue útil?]

ESTADO MENTAL DURANTE LA SESIÓN:
[Honestidad total: ¿Estuviste enfocado? ¿Hubo momentos de impulsividad,
impaciencia, o por el contrario exceso de parálisis?]
```

---

## Guía de Uso para el Agente

El agente debe responder con el siguiente análisis estructurado:

### 1. CALIDAD DE EJECUCIÓN (independiente del resultado)

El agente debe evaluar si el trader siguió su proceso, no si ganó o perdió dinero.

**Criterios de evaluación**:

| Aspecto | Pregunta | Bueno | Malo |
|---------|----------|-------|------|
| **Plan de sesión** | ¿Los trades estaban en el plan? | Sí | Improvisado |
| **Entrada** | ¿Entré en la zona correcta? | Precio/condición | Entrada nerviosa |
| **Stop loss** | ¿El stop tenía lógica estructural? | Soporte/resistencia | Arbitrario |
| **Gestión** | ¿Dejé correr ganancias/protseguí plan? | Sí | Corté temprano o添加 riesgo |
| **Tamaño** | ¿El tamaño era apropiado? | 1-2% riesgo | Sobrestimé |

**Principio clave**:

> "Un trade con -1R donde el proceso fue correcto es mejor que +2R donde improvisaste."

### 2. PATRÓN DETECTADO EN ESTA SESIÓN

El agente debe identificar patrones de comportamiento:

**Patrones POSITIVOS a reforzar**:

- Espera paciente del setup correcto
- Gestión de posición según el plan
- No operar por aburrimiento
- Reconocer cuando el mercado no ofrece oportunidades

**Patrones NEGATIVOS a corregir**:

| Patrón | Señales en el Debrief | Acción |
|--------|----------------------|--------|
| **Revenge trading** | Trade inmediatamente tras pérdida para "recuperar" | Implementar regla de cooldown |
| **Overtrading** | Más de 5-6 trades, varios impulsivos | Reducir concentración |
| **Parálisis** | Vi setups pero no entré por miedo | Documentar y revisar |
| **Premature exit** | Cerré en R:R < 1 cuando el plan era 1:2 | Reforzar regla de gestión |
| **Entrada forzada** | Entré sin tener el setup completo | Checklist pre-entrada |

### 3. LECCIÓN PRINCIPAL DEL DÍA

El agente debe distill una sola lección, concreta y accionable.

**Formato**:

```
LECCIÓN PRINCIPAL: [Título claro]

[Descripción de una frase de qué aprendiste]

ACCIONABLE PARA MAÑANA:
[Una cosa concreta que harás diferente mañana]
```

**Ejemplos**:

```
LECCIÓN PRINCIPAL: No forzar setups en zonas sin reacción

Aprendí que esperar confirmación de precio en zonas de interés
me da mejores resultados que anticipar.

ACCIONABLE PARA MAÑANA: Antes de entrar en cualquier zona,
esperaré una vela de reacción (rejecting candle) antes de actuar.
```

### 4. ACTUALIZACIÓN PARA LA WIKI

El agente debe recomendar qué añadir, modificar o reforzar en la base de conocimiento:

**Tipos de actualizaciones**:

| Tipo | Cuándo | Ejemplo |
|------|--------|---------|
| **Nuevo setup** | Descubriste un patrón que funciona | "Setup de engulfing en apertura NY funciona el 70% de veces" |
| **Regla validada** | Tu regla funcionó como esperabas | "Regla de no operar tras pérdida funciona" |
| **Regla corregida** | Tu expectativa era incorrecta | "Creía que los gaps siempre se cierran, pero no en apertura de mes" |
| **Error documentado** | Cometiste un error específico | "Overtrading tras primera pérdida del día - implementar cooldown" |
| **Sesgo identificado** | Detectaste un patrón cognitivo | "Sesgo de confirmación: ignoré divergencia porque ya estaba largo" |

**Formato de actualización**:

```
AGREGAR A WIKI:
- Nueva regla: [regla]
- Contexto: [cuándo aplica]
- Evidencia: [qué te hizo añadirla]
```

### 5. ESTADO PARA MAÑANA

El agente debe evaluar la preparación mental y física:

**Checklist de preparación**:

| Aspecto | Estado | Acción si NO |
|---------|--------|--------------|
| **Sueño** | ¿Dormiste bien? | No operar size grande |
| **Estrés** | ¿Hay estrés fuera del trading? | Reducir exposición |
| **Emociones** | ¿Estás en paz con las pérdidas? | Esperar setups claros |
| **Plan** | ¿Tienes plan para mañana? | Hacer pre-market analysis |
| **Sesgo** | ¿Traes sesgo de la sesión de hoy? | Reseteo antes de operar |

**Respuesta del agente**:

```
ESTADO PARA MAÑANA:

[ÓPTIMO / ACEPTABLE / PRECAUCIÓN]

Razón: [explicación breve]

Si estás en modo PRECAUCIÓN:
- Considera reducir tamaño de posición
- Limita el número de trades
- Evita operar el activoproblemático de hoy
- Si hay señales de revenge trading, no operes mañana
```

---

## Matriz de Autoevaluación Rápida

El agente puede usar esta matriz simple para el debrief:

| | Proceso Correcto | Proceso Incorrecto |
|---|---|---|
| **Resultado Positivo (R+)** | 🎯 Excelente — reinforce | ⚠️ Attention — suerte o riesgo no calculado |
| **Resultado Negativo (R-)** | 📚 Aprendizaje — proceso ok | 🔴 Alerta — proceso necesita修正 |

**Quadrante deseable**: Proceso Correcto + Resultado Positivo
**Quadrante de aprendizaje**: Proceso Correcto + Resultado Negativo (la varianza del mercado existe)
**Quadrante rojo**: Proceso Incorrecto + Resultado Negativo (esto es lo que hay que corregir)
