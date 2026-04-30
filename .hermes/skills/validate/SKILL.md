---
name: validate
description: "Validación crítica de setup antes de ejecutar una operación."
version: 1.0.0
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

Actuar como segundo par de ojos para detectar confluencias faltantes, agujeros en el razonamiento o riesgo no calculado.

## Proceso

1. **Solicitar información del setup** si no la proporcionó completa:
   - Activo
   - Dirección (Long/Short)
   - Timeframe de referencia
   - Descripción del setup (estructura, zona, patrón, confluencias)
   - Contexto macro hoy
   - Plan de gestión (entrada, stop, target, ratio R:R, tamaño)

2. **Analizar usando el siguiente framework**:

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

### 4. VEREDICTO

| Veredicto | Significado | Condición |
|-----------|-------------|-----------|
| **VERDE** | Setup sólido | Proceder con el plan |
| **AMARILLO** | Setup con condiciones | Ejecutar solo si [condición específica] |
| **ROJO** | No es el momento | Razón concreta, no genérica |

### 5. PREGUNTA INCÓMODA

Hacer la pregunta que un trader experimentado se haría:
- "Si este trade sale mal, ¿podré distinguir entre mala suerte y mal análisis?"
- "¿Estoy entrando porque el setup es válido o porque necesito acción?"
- "¿Este riesgo está dentro de mi plan de trading o estoy improvisando?"

## Criterios de evaluación

Un **VERDE** requiere:
1. Confluencia técnica (múltiples factores alineados)
2. Contexto macro compatible
3. Gestión de riesgo coherente (stop estructural, R:R ≥ 1:1.5)
4. Tamaño apropiado (≤ 2% riesgo)
5. Preparación emocional (no en modo reactivo)

Un **ROJO** significa:
1. Setup sin confluencias claras
2. Contexto macro en contra o incierto
3. Stop arbitrario o sin estructura
4. R:R desfavorable
5. Trader en modo emocional

## Reglas

- Ser crítico, no complaciente. Un verde significa que realmente es sólido.
- No validar por presión o comodidad.
- Si falta información crítica, pedirla antes de dar veredicto.
