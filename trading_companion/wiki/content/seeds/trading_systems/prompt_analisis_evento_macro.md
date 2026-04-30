---
title: Prompt 2 — Análisis de Evento Macro/Geopolítico en Tiempo Real
type: article
branch: trading_systems
tags: prompt,macro,geopolitico,evento,gap
summary: Prompt para analizar eventos macro y geopolíticos con impacto en mercados
---

# Prompt 2 — Análisis de Evento Macro/Geopolítico en Tiempo Real

**Uso**: Prompt de usuario para cuando ocurre un evento externo con impacto en mercados.
**Cuándo usarlo**: Apertura con gap, noticia de alto impacto, evento geopolítico sorpresa.

---

## Template del Prompt

```
Acaba de ocurrir / está ocurriendo el siguiente evento:

EVENTO: [describe qué pasó — ej: "EEUU e Israel han lanzado ataques sobre infraestructura nuclear iraní durante el fin de semana"]

ACTIVO QUE ESTOY MIRANDO: [ej: "CL (Crude Oil futuros)" / "XAUUSD" / "ES futuros" / "EURUSD"]

SITUACIÓN DE PRECIO: [ej: "apertura con gap alcista del 4.2% desde el cierre del viernes" / "precio cayendo con fuerza desde apertura asiática"]

LO QUE YO OBSERVO: [ej: "el gap no parece querer cerrarse, el volumen de apertura es alto, las velas son impulsivas"]

---

Necesito que analices:
```

---

## Guía de Uso para el Agente

Cuando el trader presenta esta consulta, el agente debe responder con el siguiente análisis estructurado:

### 1. CONTEXTO MACRO DEL EVENTO

El agente debe responder:

- ¿Qué tipo de evento es este? (geopolítico, macro, natural, regulatorio)
- ¿Qué precedentes históricos son relevantes?
- ¿Cómo suelen reaccionar los mercados ante este tipo de situación?

**Ejemplo de análisis para conflicto en Oriente Medio**:

| Tipo de Evento | Precedentes | Reacción Típica |
|----------------|-------------|------------------|
| Conflicto militar en región petrolera | Gulf War, Irak 2003 | Spike en crudo, safe haven en oro |
| Tensión sin acción militar | Sanciones, rhetórica | Mercado lo descuenta y revierte |
| Escalada de aliados regionales | Yemen, Hezbollah | Incertidumbre sostenida |

### 2. LECTURA DEL GAP / MOVIMIENTO INICIAL

El agente debe determinar:

- ¿Es un gap/movimiento técnico o fundamental?
- ¿Cuál es la probabilidad histórica de cierre en este contexto?
- ¿Qué factores aumentan o reducen esa probabilidad?

**Factores que AUMENTAN probabilidad de cierre del gap**:

- Gap menor al 1%
- Mercado en rango antes del evento
- Sin acumulación previa de posiciones
- Evento "known unknown" (mercado esperaba posibilidad)

**Factores que REDUCEN probabilidad de cierre**:

- Gap mayor al 3%
- Evento sorpresa genuina ("unknown unknown")
- Reserva estratégica petroleum liberada
- Conflicto en zona de producción crítica

### 3. CORRELACIONES A VIGILAR AHORA MISMO

El agente debe indicar:

- ¿Qué otros activos monitorizar para confirmar o invalidar la narrativa?
- ¿Hay divergencias relevantes entre activos correlacionados?

**Tabla de correlaciones por evento**:

| Evento | Activos a Monitorizar | Divergencia a Buscar |
|--------|----------------------|---------------------|
| Spike en crudo | CL, XAUUSD, USO, energécos | Oro no confirma |
| Crisis geopolítica | DXY, JPY, CHF, Bund | Dólar no actúa como safe haven |
| Shock en renta variable | VIX, TNX, oro | Oro y acciones cayendo = deflación |
| Noticias de OPEP | Brent, WTI, USD/CAD | Divergencia CL vs Brent |

### 4. ESCENARIOS PROBABLES

El agente debe presentar:

#### Escenario A (más probable)
- Qué haría el precio y por qué
- Condiciones que lo activan

#### Escenario B (alternativo)
- Qué condición lo activaría

#### Condición de invalidación
- Qué le diría que su lectura está equivocada

**Ejemplo de estructura**:

```
Escenario A (60%): El gap se mantiene y el precio consolida arriba.
- Razón: El mercado descuenta que habrá represalias iraníes sostenidas.
- Condición: Precio mantiene sopra 85.50 en CL.

Escenario B (30%): El gap se cierra parcialmente.
- Razón: Diplomacia internacional contiene la escalada.
- Condición: Llamadas de Biden-Netanyahu reducen tensión.

Invalidación: CL rompe 82.00 con volumen vendedor fuerte —
el mercado no cree en escalada sostenida.
```

### 5. IMPLICACIONES PARA MI TRADING HOY

El agente debe indicar:

- ¿Qué tipo de setups tienen más sentido en este contexto?
- ¿Qué debo evitar hacer hoy?

**Setsups a considerar**:

| Contexto | Setup Válido | Setup a Evitar |
|----------|--------------|----------------|
| Gap con rechazo de cierre | Fade del gap con bajo riesgo | Comprar el gap inmediatamente |
| Gap con volumen fuerte | Follow-through en dirección del gap | Counter-trend sin estructura |
| Evento en desarrollo | Esperar resolución | Entrar por "fomo" |

**Errores comunes a evitar**:

- Tratar de "recuperar" el gap inmediatamente si es en tu contra
- Tomar decisiones de trading durante los primeros 30 minutos de volatilidad extrema
- Ignorar el contexto de la sesión (不开 apertura de Londres/NY)
