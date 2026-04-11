# Spec — T025: Contador de tiempo conectado

## Objetivo

Mostrar en la status bar cuánto tiempo lleva la conexión activa (HH:MM:SS).

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | QTimer de 1s (`_elapsed_timer`), `_elapsed_seconds` counter, `_update_elapsed()` actualiza status bar |
| `src/ovpn_launcher/app.py` | `_update_state(CONNECTED)`: iniciar timer y resetear counter |
| `src/ovpn_launcher/app.py` | `_update_state(DISCONNECTED)`: parar timer |

## Comportamiento

- DISCONNECTED: status bar muestra "Disconnected"
- CONNECTING: "Connecting: alias…"
- CONNECTED: "Connected: alias — 00:05:32" (actualiza cada segundo)
