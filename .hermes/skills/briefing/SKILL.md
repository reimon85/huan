---
name: briefing
description: "Genera un briefing completo de mercado antes de la sesión de trading."
version: 1.0.0
author: Trading Companion
license: MIT
metadata:
  hermes:
    tags: [trading, briefing, pre-session, mercado, macro]
    related_skills: [validate, macro, debrief]
---

# Briefing Pre-Sesión

Usa esta skill cuando el trader quiera prepararse antes de operar o al inicio del día.

## Objetivo

Proporcionar un panorama completo del contexto de mercado actual para que el trader tome decisiones informadas.

## Proceso

1. **Obtener contexto de mercado** usando `fetch_market_context`
2. **Analizar cada componente** del briefing:
   - Calendario económico del día (eventos de alto impacto)
   - Precios clave y niveles técnicos relevantes
   - Sentimiento general del mercado (Fear & Greed, VIX)
   - Noticias urgentes o relevantes
   - Posicionamiento COT (si hay datos recientes)
   - Snapshot de crypto (funding rates, OI, dominance)

3. **Estructurar la respuesta**:

```
=== BRIEFING [FECHA] ===

1. CONTEXTO MACRO
   - Eventos del día y su potencial impacto
   - Narrativa dominante del mercado
   - Correlaciones clave a vigilar

2. NIVELES TÉCNICOS RELEVANTES
   - EURUSD: [soportes/resistencias clave]
   - ES/NQ: [niveles importantes]
   - CL/GC: [zonas de interés]
   - BTC/ETH: [rangos clave]

3. SENTIMIENTO Y POSICIONAMIENTO
   - Fear & Greed: [valor y tendencia]
   - VIX: [nivel e implicaciones]
   - COT: [posicionamiento neto si disponible]

4. NOTICIAS Y EVENTOS A VIGILAR
   - [Lista de noticias relevantes con horario]

5. ESCENARIOS PROBABLES HOY
   - Escenario A (más probable): [descripción]
   - Escenario B (alternativo): [descripción]
   - Condición de invalidación: [qué cambiaría la lectura]

6. RECOMENDACIONES DE SESIÓN
   - Qué activos tienen mejor contexto hoy
   - Qué evitar
   - Horarios clave a vigilar
```

## Reglas

- No dar señales de entrada directas.
- Enfocarse en probabilidades y escenarios, no certezas.
- Si el contexto es incierto, decirlo claramente.
- Mencionar correlaciones intermercado relevantes (DXY, bonos, oro, VIX).
