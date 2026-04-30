# Memoria del Agente

## Reglas validadas

- Esperar confirmación de precio en zonas de interés da mejores resultados que anticipar.
- No operar tras una pérdida sin cooldown de al menos 30 minutos.
- Los gaps mayores al 3% en apertura de sesión tienen baja probabilidad de cierre si el evento es sorpresa genuina.

## Setups documentados

- Setup de engulfing en apertura NY: alta probabilidad cuando hay momentum previo en H4.
- Mean reversion en zonas de demanda H4 validadas con order block + divergencia RSI.

## Errores documentados

- Overtrading tras primera pérdida del día → implementar regla de cooldown.
- Sesgo de confirmación: ignorar divergencia porque ya estaba direccionalmente sesgado.

## Preferencias del trader

- Timeframes preferidos: H4 para estructura, H1 para zona, M15 para entrada.
- Activos principales: EURUSD, ES, NQ, CL, GC, BTC.
- Ratio mínimo R:R: 1:1.5.
- Riesgo máximo por operación: 1-2%.
