# Spec — T040: Marcar conexión activa en menú del tray

## Objetivo

En el menú de clic derecho del system tray, resaltar en bold el perfil que está conectado o conectando.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_rebuild_tray_menu()`: setear font bold si el alias coincide con `connected_alias` y state != DISCONNECTED |
| `src/ovpn_launcher/app.py` | `_rebuild_tray_menu()`: disconnect action enabled según estado |
| `src/ovpn_launcher/app.py` | `_update_state()`: llamar `_rebuild_tray_menu()` para actualizar el menú |
| `src/ovpn_launcher/app.py` | Eliminar `tray_disconnect_action.setEnabled()` redundante de `_update_state()` |

## Comportamiento

- DISCONNECTED: todos los perfiles en font normal, Disconnect deshabilitado
- CONNECTING/CONNECTED: perfil activo en bold, Disconnect habilitado
