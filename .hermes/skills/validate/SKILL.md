---
name: validate
description: "Validación crítica de setup antes de ejecutar una operación."
version: 2.0.0
author: Trading Companion
license: MIT
metadata:
  hermes:
    tags: [trading, setup, validacion, pre-entrada, risk-management]
    related_skills: [briefing, macro, debrief]
---

# Validación de Setup

Usa esta skill cuando el trader tenga un setup identificado y quiera validarlo antes de entrar.

## Objetivo

Actuar como segundo par de ojos para detectar confluencias faltantes, agujeros en el razonamiento o riesgo no calculado. Consultar el journal histórico para personalizar la validación.

## Proceso

1. **Solicitar información del setup** si no la proporcionó completa:
   - Activo
   - Dirección (Long/Short)
   - Timeframe de referencia
   - Descripción del setup (estructura, zona, patrón, confluencias)
   - Contexto macro hoy
   - Plan de gestión (entrada, stop, target, ratio R:R, tamaño)

2. **Consultar estadísticas históricas** usando `get_stats` y `get_setup_performance`:
   - "Tu win rate en {setup_type} de {asset} es del X% — tenlo en cuenta"
   - "En los últimos 20 trades de este setup, tu avg R es +1.2 pero hoy el contexto macro es incierto"
   - "Llevas 3 pérdidas seguidas en {asset}. Tu regla dice cooldown de 30 min."

3. **Analizar usando el siguiente framework**:

### 1. FORTALEZAS DEL SETUP

Listar qué confluencias sólidas tiene:
- Confluencia técnica entre múltiples timeframes
- Contexto de tendencia alineado
- Zona de interés validada

### 2. PUNTOS DÉBILES O AUSENCIAS

Señalar qué falta:
- Confluencia importante no presente
- Algo que no encaje en el análisis
- Stop loss arbitrario o sin estructura

### 3. RIESGO DE CONTEXTO

Evaluar:
- Contexto macro/geopolítico favorece, neutraliza o va en contra
- Eventos próximos que puedan afectar
- Checklist: datos macro, sesión de mercado, gap potential, vencimientos

### 4. RIESGO DE PORTFOLIO

- ¿Cuántas operaciones abiertas tienes ya?
- ¿Este activo ya está correlacionado con alguna posición actual?
- ¿El riesgo total acumulado supera tu límite diario?

### 5. VEREDICTO

| Veredicto | Significado | Condición |
|-----------|-------------|-----------|
| **VERDE** | Setup sólido | Proceder con el plan |
| **AMARILLO** | Setup con condiciones | Ejecutar solo si [condición específica] |
| **ROJO** | No es el momento | Razón concreta, no genérica |

### 6. PREGUNTA INCÓMODA

Hacer la pregunta que un trader experimentado se haría:
- "Si este trade sale mal, ¿podré distinguir entre mala suerte y mal análisis?"
- "¿Estoy entrando porque el setup es válido o porque necesito acción?"
- "¿Este riesgo está dentro de mi plan de trading o estoy improvisando?"
- "En tus últimos 10 trades de este setup, ganaste X y perdiste Y. ¿Este contexto es similar a los ganadores o a los perdedores?"

## Criterios de evaluación

Un **VERDE** requiere:
1. Confluencia técnica (múltiples factores alineados)
2. Contexto macro compatible
3. Gestión de riesgo coherente (stop estructural, R:R ≥ 1:1.5)
4. Tamaño apropiado (≤ 2% riesgo)
5. Preparación emocional (no en modo reactivo)
6. Métrica histórica favorable para este setup (si existe)

Un **ROJO** significa:
1. Setup sin confluencias claras
2. Contexto macro en contra o incierto
3. Stop arbitrario o sin estructura
4. R:R desfavorable
5. Trader en modo emocional
6. Métrica histórica desfavorable o sin datos suficientes

## Reglas

- Ser crítico, no complacente. Un verde significa que realmente es sólido.
- No validar por presión o comodidad.
- Si falta información crítica, pedirla antes de dar veredicto.
- Consultar el journal (`get_stats`) para personalizar la validación con datos históricos.
