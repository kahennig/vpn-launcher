# Spec — T048: Retry con backoff en auto-reconnect

## Objetivo

En vez de siempre 5s, usar backoff exponencial y parar después de N intentos.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_reconnect_attempt` counter, backoff delays [5, 10, 20, 60], max 5 intentos |
| `src/ovpn_launcher/app.py` | Reset counter al conectar exitosamente o al disconnect manual |

## Comportamiento

- Intento 1: 5s, intento 2: 10s, intento 3: 20s, intento 4+: 60s
- Después de 5 intentos fallidos: parar y log "Auto-reconnect gave up after 5 attempts"
- Conexión exitosa resetea el counter
- Disconnect manual resetea el counter
