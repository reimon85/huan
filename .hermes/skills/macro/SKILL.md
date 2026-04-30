---
name: macro
description: "Análisis de evento macro o geopolítico en tiempo real con impacto en mercados."
version: 1.0.0
author: Trading Companion
license: MIT
metadata:
  hermes:
    tags: [trading, macro, geopolitico, evento, gap, analisis]
    related_skills: [briefing, validate, debrief]
---

# Análisis de Evento Macro/Geopolítico

Usa esta skill cuando ocurra un evento externo con impacto en mercados: apertura con gap, noticia de alto impacto, evento geopolítico sorpresa.

## Objetivo

Contextualizar el evento con el posicionamiento actual del mercado y precedentes históricos relevantes.

## Proceso

1. **Solicitar información del evento** si no la proporcionó:
   - Qué ocurrió
   - Activo que está mirando
   - Situación de precio (gap, movimiento)
   - Qué observa el trader

2. **Obtener contexto adicional** usando `fetch_market_context` y `fetch_news`

3. **Analizar con la siguiente estructura**:

### 1. CONTEXTO MACRO DEL EVENTO

- Tipo de evento (geopolítico, macro, natural, regulatorio)
- Precedentes históricos relevantes
- Reacción típica del mercado ante este tipo de situación

### 2. LECTURA DEL GAP / MOVIMIENTO INICIAL

Determinar:
- ¿Es gap técnico o fundamental?
- Probabilidad histórica de cierre en este contexto

**Factores que AUMENTAN probabilidad de cierre**:
- Gap menor al 1%
- Mercado en rango antes del evento
- Sin acumulación previa de posiciones
- Evento "known unknown"

**Factores que REDUCEN probabilidad de cierre**:
- Gap mayor al 3%
- Evento sorpresa genuina ("unknown unknown")
- Reserva estratégica liberada
- Conflicto en zona de producción crítica

### 3. CORRELACIONES A VIGILAR

| Evento | Activos a Monitorizar | Divergencia a Buscar |
|--------|----------------------|---------------------|
| Spike en crudo | CL, XAUUSD, USO, energéticos | Oro no confirma |
| Crisis geopolítica | DXY, JPY, CHF, Bund | Dólar no actúa como safe haven |
| Shock en renta variable | VIX, TNX, oro | Oro y acciones cayendo = deflación |
| Noticias de OPEP | Brent, WTI, USD/CAD | Divergencia CL vs Brent |

### 4. ESCENARIOS PROBABLES

#### Escenario A (más probable)
- Qué haría el precio y por qué
- Condiciones que lo activan

#### Escenario B (alternativo)
- Qué condición lo activaría

#### Condición de invalidación
- Qué le diría que la lectura está equivocada

### 5. IMPLICACIONES PARA EL TRADING HOY

- Setups válidos en este contexto
- Setups a evitar
- Errores comunes a evitar

## Reglas

- No predecir con certeza. Trabajar con probabilidades.
- Contextualizar siempre con precedentes históricos.
- Señalar divergencias entre activos correlacionados.
- Recordar al trader que los primeros 30 minutos de volatilidad extrema son peligrosos.
