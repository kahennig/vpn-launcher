# Spec — T018: Tema oscuro/claro (palette-aware)

## Objetivo

Asegurar que la app se adapta correctamente a temas oscuros y claros del sistema.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | About dialog: reemplazar `color: gray` hardcodeado por `QPalette.ColorRole.PlaceholderText` |

## Notas

- Qt/PyQt6 ya respeta el tema del sistema automáticamente en KDE Plasma
- Los colores en `_update_state()` ya usaban QPalette (PlaceholderText, Link)
- El único color hardcodeado era el `gray` del version label en el About dialog
- No se agrega toggle manual de tema — en KDE se controla desde System Settings
