---
name: debrief
description: "Debrief estructurado post-sesión para extraer aprendizaje de cada día de trading."
version: 1.0.0
author: Trading Companion
license: MIT
metadata:
  hermes:
    tags: [trading, debrief, post-sesion, aprendizaje, journal]
    related_skills: [briefing, validate, macro]
---

# Debrief Post-Sesión

Usa esta skill al cierre de la sesión de trading, al final del día, con o sin trades ejecutados.

## Objetivo

Extraer aprendizaje real, detectar patrones de comportamiento y sugerir actualizaciones para la memoria/wiki.

## Proceso

1. **Solicitar información de la sesión** si no la proporcionó:
   - Fecha y sesión (europea, americana, asiática)
   - Mercados operados
   - Resultado del día (en R, no en dinero)
   - Trades ejecutados (activo, dirección, resultado, plan vs improvisado, gestión, estado mental)
   - Trades no ejecutados (setups vistos pero no tomados, ¿por qué?)
   - Contexto de mercado (¿hizo lo esperado? ¿sorpresas?)
   - Estado mental durante la sesión

2. **Analizar con la siguiente estructura**:

### 1. CALIDAD DE EJECUCIÓN (independiente del resultado)

Evaluar si el trader siguió su proceso:

| Aspecto | Pregunta | Bueno | Malo |
|---------|----------|-------|------|
| Plan de sesión | ¿Los trades estaban en el plan? | Sí | Improvisado |
| Entrada | ¿Entré en la zona correcta? | Precio/condición | Entrada nerviosa |
| Stop loss | ¿El stop tenía lógica estructural? | Soporte/resistencia | Arbitrario |
| Gestión | ¿Dejé correr ganancias/seguí plan? | Sí | Corté temprano o añadí riesgo |
| Tamaño | ¿El tamaño era apropiado? | 1-2% riesgo | Sobrestimé |

**Principio clave**:
> "Un trade con -1R donde el proceso fue correcto es mejor que +2R donde improvisaste."

### 2. PATRÓN DETECTADO EN ESTA SESIÓN

**Patrones POSITIVOS a reforzar**:
- Espera paciente del setup correcto
- Gestión de posición según el plan
- No operar por aburrimiento
- Reconocer cuando el mercado no ofrece oportunidades

**Patrones NEGATIVOS a corregir**:

| Patrón | Señales en el Debrief | Acción |
|--------|----------------------|--------|
| Revenge trading | Trade inmediatamente tras pérdida | Implementar regla de cooldown |
| Overtrading | Más de 5-6 trades, varios impulsivos | Reducir concentración |
| Parálisis | Vi setups pero no entré por miedo | Documentar y revisar |
| Premature exit | Cerré en R:R < 1 cuando el plan era 1:2 | Reforzar regla de gestión |
| Entrada forzada | Entré sin tener el setup completo | Checklist pre-entrada |

### 3. LECCIÓN PRINCIPAL DEL DÍA

Distillar una sola lección, concreta y accionable:

```
LECCIÓN PRINCIPAL: [Título claro]

[Descripción de una frase de qué aprendiste]

ACCIONABLE PARA MAÑANA:
[Una cosa concreta que harás diferente mañana]
```

### 4. ACTUALIZACIÓN PARA LA MEMORIA

Sugerir qué añadir, modificar o reforzar:

| Tipo | Cuándo | Ejemplo |
|------|--------|---------|
| Nuevo setup | Descubriste un patrón que funciona | "Setup de engulfing en apertura NY funciona el 70% de veces" |
| Regla validada | Tu regla funcionó como esperabas | "Regla de no operar tras pérdida funciona" |
| Regla corregida | Tu expectativa era incorrecta | "Creía que los gaps siempre se cierran, pero no en apertura de mes" |
| Error documentado | Cometiste un error específico | "Overtrading tras primera pérdida del día" |
| Sesgo identificado | Detectaste un patrón cognitivo | "Sesgo de confirmación: ignoré divergencia porque ya estaba largo" |

### 5. ESTADO PARA MAÑANA

Evaluar preparación mental:

| Aspecto | Estado | Acción si NO |
|---------|--------|--------------|
| Sueño | ¿Dormiste bien? | No operar size grande |
| Estrés | ¿Hay estrés fuera del trading? | Reducir exposición |
| Emociones | ¿Estás en paz con las pérdidas? | Esperar setups claros |
| Plan | ¿Tienes plan para mañana? | Hacer pre-market analysis |
| Sesgo | ¿Traes sesgo de la sesión de hoy? | Reseteo antes de operar |

**Respuesta**:
```
ESTADO PARA MAÑANA: [ÓPTIMO / ACEPTABLE / PRECAUCIÓN]

Razón: [explicación breve]
```

## Matriz de Autoevaluación

| | Proceso Correcto | Proceso Incorrecto |
|---|---|---|
| **Resultado Positivo (R+)** | Excelente — reforzar | Atención — suerte o riesgo no calculado |
| **Resultado Negativo (R-)** | Aprendizaje — proceso ok | Alerta — proceso necesita corrección |

## Reglas

- Evaluar el proceso, no el resultado.
- Ser honesto y directo.
- Extraer una lección accionable concreta.
- Sugerir actualizaciones a MEMORY.md cuando sea relevante.
- Detectar patrones psicológicos con respeto pero claridad.
