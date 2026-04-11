# Spec — T005: Notificaciones de estado en tray

## Objetivo

Mostrar notificaciones de escritorio al conectar y desconectar VPN.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_update_state()`: track `prev_state`, llamar `tray.showMessage()` al pasar a CONNECTED o DISCONNECTED |

## Comportamiento

- Al conectar: "VPN Connected — Connected to {alias}" (3s)
- Al desconectar: "VPN Disconnected — VPN connection closed." (3s)
- No notifica en la transición inicial DISCONNECTED → DISCONNECTED
