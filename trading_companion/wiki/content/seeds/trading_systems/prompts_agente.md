---
title: Prompts del Agente IA - Índice
type: topic
branch: trading_systems
tags: prompts,agente,indice
summary: Índice de prompts de uso general para el agente de trading
---

# Prompts del Agente IA - Índice

Esta sección contiene los prompts de uso general para el agente de trading.

## Prompts Disponibles

| # | Prompt | Uso | Frecuencia |
|---|--------|-----|------------|
| 1 | [System Prompt Maestro](system_prompt_maestro.md) | Identidad del agente | Una vez por conversación |
| 2 | [Análisis de Evento Macro/Geopolítico](prompt_analisis_evento_macro.md) | Eventos externos con impacto | Cuando ocurre evento |
| 3 | [Validación de Setup](prompt_validacion_setup.md) | Validación pre-entrada | Antes de cada trade |
| 4 | [Debrief Post-Sesión](prompt_debrief_post_sesion.md) | Aprendizaje estructurado | Fin de cada sesión |

## Flujo de Uso

```
                    ┌───────────────────────────────┐
                    │    System Prompt Maestro      │
                    │   (carga al iniciar)         │
                    └───────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │         DURANTE LA SESIÓN           │
                    ├─────────────────────────────────────┤
                    │                                     │
                    ▼                                     ▼
    ┌──────────────────────────┐     ┌──────────────────────────┐
    │   Si HAY EVENTO MACRO:   │     │   ANTES DE ENTRAR:       │
    │   Prompt #2              │     │   Prompt #3              │
    │   (análisis de evento)   │     │   (validación setup)     │
    └──────────────────────────┘     └──────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │          DESPUÉS DE LA SESIÓN        │
                    │   Prompt #4                          │
                    │   (debrief post-sesión)              │
                    └─────────────────────────────────────┘
```

## Notas de Implementación

### System Prompt (Prompt #1)

Este prompt va en el campo `system` del LLM. Es la base de la identidad del agente y persiste durante toda la conversación.

**Cargar una vez** al inicio de cada sesión de chat.

### Prompts de Usuario (Prompts #2, #3, #4)

Estos son templates que el trader rellena con su situación específica y usa como input para el agente.

**Flujo recomendado**:

1. **Prompt #2**: Solo cuando hay un evento externo significativo (noticia sorpresa, dato macro shock, evento geopolítico)
2. **Prompt #3**: Antes de **cualquier** operación, sin excepción
3. **Prompt #4**: Al final de **cada** sesión de trading, sin excepción

## Integración con Wiki Personal

El agente puede acceder a la wiki del trader para:

- Personalizar análisis según el historial del trader
- Detectar patrones de error cognitivo repetidos
- Reforzar reglas que el trader ha validado
- Actualizar la wiki con nuevas lecciones

Ver también: [System Prompt Maestro](system_prompt_maestro.md) para la identidad completa del agente.
