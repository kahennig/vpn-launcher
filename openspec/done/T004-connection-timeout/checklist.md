# Checklist — T004: Timeout de conexión

## F0 — Timer y warning

- [x] Timer arranca al conectar
- [x] Timer se cancela si llega STATE_CONNECTED
- [x] Timer se cancela en _cleanup (disconnect o proceso termina)
- [x] Al disparar timeout, muestra warning con opción Yes/No
- [x] Yes → desconecta
- [x] No → sigue esperando (no repite warning)
