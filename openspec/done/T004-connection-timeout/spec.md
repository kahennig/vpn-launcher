# Spec — T004: Timeout de conexión

## Objetivo

Detectar conexiones que no completan en tiempo razonable y avisar al usuario.

## Alcance

**Incluye:** QTimer de timeout, warning dialog con opción de desconectar o seguir esperando.
**No incluye:** timeout configurable por perfil, retry automático.

## Fases

### F0 — Timer y warning

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Constante `CONNECTION_TIMEOUT = 30` (segundos) |
| `src/ovpn_launcher/app.py` | `on_connect`: iniciar QTimer singleShot al arrancar proceso |
| `src/ovpn_launcher/app.py` | `_update_state(CONNECTED)`: cancelar timer si conectó |
| `src/ovpn_launcher/app.py` | `_on_connection_timeout()`: QMessageBox con "Connection is taking longer than expected. Disconnect?" (Yes/No) |
| `src/ovpn_launcher/app.py` | `_cleanup()`: cancelar timer |

**Comportamiento:**
- Timer arranca al entrar en STATE_CONNECTING
- Si llega STATE_CONNECTED antes del timeout → timer se cancela, todo normal
- Si el timer dispara → warning con Yes (disconnect) / No (seguir esperando)
- Si el proceso termina antes del timeout → _cleanup cancela el timer
- El timer NO se reinicia si el usuario elige seguir esperando (un solo aviso)
