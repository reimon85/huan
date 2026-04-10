---
title: Prompt 3 — Protocolo de Validación de Setup Antes de Entrar
type: article
branch: trading_systems
tags: prompt,validacion,setup,entrada,risk-management
summary: Protocolo de validación crítica antes de ejecutar cualquier operación
---

# Prompt 3 — Protocolo de Validación de Setup Antes de Entrar

**Uso**: Justo antes de ejecutar una operación. El agente actúa como segundo par de ojos.
**Cuándo usarlo**: Cuando tienes un setup identificado y quieres validarlo antes de pulsar.
**Objetivo**: Detectar confluencias que te faltan, agujeros en el razonamiento, riesgo no calculado.

---

## Template del Prompt

```
Estoy evaluando una posible entrada. Dame un análisis crítico antes de ejecutar.

ACTIVO: [ej: EURUSD / NQ / XAUUSD / BTC]
DIRECCIÓN: [Long / Short]
TIMEFRAME DE REFERENCIA: [ej: H1 con entrada en M15]

DESCRIPCIÓN DEL SETUP:
[Describe qué estás viendo — estructura de precio, zona de interés, patrón,
confluencias que ya identificaste. Sé específico: "precio ha llegado a zona de demanda
H4 entre 1.0820-1.0840, hay un order block limpio, el HTF (D1) está en tendencia alcista,
el retroceso actual es del 38.2% del último impulso"]

CONTEXTO MACRO HOY:
[¿Hay datos importantes? ¿Está el mercado en modo risk-on o risk-off?
¿Hay algún evento geopolítico activo que afecte este activo?]

MI PLAN DE GESTIÓN:
- Entrada: [precio o condición de entrada]
- Stop loss: [nivel y razonamiento]
- Target(s): [niveles y razonamiento]
- Ratio R:R: [calculado]
- Tamaño de posición: [% de riesgo sobre cuenta]
```

---

## Guía de Uso para el Agente

El agente debe responder con el siguiente análisis estructurado:

### 1. FORTALEZAS DEL SETUP

El agente debe listar qué confluencias sólidas tiene:

- ¿Qué hace que este setup tenga lógica desde el punto de vista técnico?
- ¿Hay confluencia entre múltiples timeframes?
- ¿El contexto de tendencia apoya la dirección?

**Ejemplo de análisis positivo**:

```
FORTALEZAS:
✓ Zona de demanda H4 validada con máximos anteriores
✓ Order block bullish en zona de entrada — acumulación institucional plausible
✓ HTF (D1) en tendencia alcista — contexto alineado
✓ RSI en H1 mostrando divergencia alcista
✓ Retroceso del 38.2% coincide con zona de demanda
```

### 2. PUNTOS DÉBILES O AUSENCIAS

El agente debe señalar qué falta:

- ¿Qué confluencia importante no está presente?
- ¿Hay algo que no encaja en el análisis?
- ¿El stop loss tiene lógica estructural o es arbitrario?

**Ejemplo de puntos débiles**:

```
PUNTOS DÉBILES:
⚠ No hay reacción de precio clara en la zona — podría ser que no sea zona de interés
⚠ El stop loss está muy cerca del precio de entrada (solo 15 pips) — muy ajustado
⚠ Faltan confirmaciones adicionales: me falta ver volumen en la reacción
⚠ No hay divergencia clara en timeframe superior
```

### 3. RIESGO DE CONTEXTO

El agente debe evaluar:

- ¿El contexto macro/geopolítico actual favorece, neutraliza o va en contra del setup?
- ¿Hay algún evento próximo (dato macro, cierre de sesión, vencimiento) que deba considerar?

**Checklist de riesgo de contexto**:

| Factor | Pregunta | Impacto en Setup |
|--------|----------|------------------|
| **Datos macro** | ¿Hay NFP, CPI, FOMC en las próximas 24h? | Puede invalidar estructura |
| **Sesión de mercado** | ¿Estoy operando en sesión de alta liquidez? | Mejor ejecución en NY/Londres |
| **Acumulación fin de semana** | ¿Hay gap potential tras noticias? | Mayor riesgo overnight |
| **Vencimientos** | ¿Hay vencimiento de opciones o futuros cerca? | Puede causar spikes |

### 4. VEREDICTO

El agente debe dar un veredicto claro:

| Veredicto | Significado | Condición |
|------------|-------------|-----------|
| **VERDE** | Setup sólido con la información disponible | Proceder con el plan |
| **AMARILLO** | Setup con condiciones | Ejecutar solo si [condición específica] |
| **ROJO** | No es el momento | Razón concreta, no genérica |

**Ejemplo de veredicto AMARILLO**:

```
VEREDICTO: [AMARILLO]

Setup tiene buena estructura pero el stop es demasiado ajustado.
Ejecutar SOLO si:
  - El precio reacciona con vela de rechazo clara en la zona
  - El volumen confirma la reacción
Si el precio atraviesa la zona sin reacción, abortar.
```

### 5. UNA PREGUNTA QUE DEBERÍAS HACERTE

El agente debe hacer la pregunta incómoda que un trader experimentado haría:

**Ejemplos de preguntas**:

- "Si este trade sale mal, ¿podré distinguir entre mala suerte y mal análisis?"
- "¿Estoy entrando porque el setup es válido o porque necesito acción?"
- "¿Este riesgo está dentro de mi plan de trading o estoy improvisando?"
- "¿Cuántas veces he visto este mismo setup funcionar? ¿Tengo datos o es intuición?"
- "¿No estoy ignorando alguna señal en contra porque ya estoy direcccionalmente sesgado?"

---

## Criterios de Evaluación del Agente

El agente debe ser crítico, no complaciente. Un VERDE significa:

1. **Confluencia técnica**: Múltiples factores alineados (soporte/resistencia, tendencia, señal)
2. **Contexto macro compatible**: No hay eventos que invaliden la dirección
3. **Gestión de riesgo coherente**: Stop tiene lógica estructural, R:R mínimo 1:1.5
4. **Tamaño apropiado**: No más del 1-2% de riesgo por operación
5. **Preparación emocional**: El trader está en estado mental de operar, no reaccionando

Un ROJO significa:

1. Setup sin confluencias claras
2. Contexto macro en contra o incierto
3. Stop loss arbitrario o sin estructura
4. R:R desfavorable
5. El trader está en modo emocional (recuperar pérdidas, FOMO, etc.)
