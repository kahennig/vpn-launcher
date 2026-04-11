# Spec — T008: Auto-reconnect

## Objetivo

Reconectar automáticamente si la conexión VPN cae inesperadamente.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_last_profile`, `_user_disconnected` flags, `reconnect_timer` (5s singleShot), `_on_reconnect()`, `_on_process_finished()` con lógica de reconnect |

## Comportamiento

- Si el proceso termina con exit_code != 0 y NO fue disconnect manual → reconnect en 5s
- Si el usuario hizo disconnect manual → no reconnect
- Si el usuario hace quit → no reconnect
- Log muestra "Reconnecting in 5 seconds..." y "Auto-reconnecting to {alias}..."
