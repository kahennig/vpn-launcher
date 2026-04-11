# Spec — T032: Autostart al login

## Objetivo

Opción en el menú hamburguesa para habilitar/deshabilitar autostart al login.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acción checkable "Start at Login" en hamburger menu |
| `src/ovpn_launcher/app.py` | Toggle crea/elimina `~/.config/autostart/ovpn-launcher.desktop` |

## Comportamiento

- Checkable action: checked = autostart habilitado
- Al activar: copia el .desktop a `~/.config/autostart/`
- Al desactivar: elimina el .desktop de autostart
- Al iniciar la app: verifica si el archivo existe para setear el check
