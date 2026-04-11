# Spec — T023: Menú hamburguesa estilo KDE

## Objetivo

Reemplazar el menú bar por un botón hamburguesa (☰) en la toolbar con todas las acciones, siguiendo el patrón de Dolphin/Kate/Konsole.

## Alcance

**Incluye:** botón hamburguesa con QMenu, eliminar menú bar.
**No incluye:** cambios en las acciones existentes, nuevos shortcuts.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Eliminar `_setup_menubar()` |
| `src/ovpn_launcher/app.py` | En `_setup_toolbar()`: reemplazar `action_quit` al final por un QToolButton con menú hamburguesa |

## Layout del menú

```
Connect          Ctrl+Enter
Disconnect       Ctrl+D
─────────────────
Add Profile
Import .ovpn
Edit Profile
Remove Profile
─────────────────
Reload Profiles  F5
Clear Log        Ctrl+L
─────────────────
About
Quit             Ctrl+Q
```

## Implementación

- Usar QToolButton con `setPopupMode(InstantPopup)` e ícono `application-menu` (freedesktop)
- El QMenu contiene las mismas QAction ya definidas en `_setup_actions()` + la acción About
- Eliminar la llamada a `self.menuBar()` — sin menú bar
- El spacer sigue empujando el botón hamburguesa a la derecha

## Casos borde

- Si el ícono `application-menu` no existe en el tema, fallback a `open-menu-symbolic` o texto "☰"
