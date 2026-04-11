# Spec — T061: Fix crashes al usar acciones del menú hamburguesa

## Problema

Crash (SIGABRT) al hacer click en acciones del menú hamburguesa que abren diálogos modales (About, Settings, Add, Edit, Remove, Import, Export). El menú hamburguesa usa `QToolButton` con `InstantPopup` que ejecuta `QMenu::exec()`. Cuando una acción del menú abre un diálogo modal (`dlg.exec()`), se crea un event loop anidado dentro del event loop del menú, lo que causa crash en PyQt6.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Todas las acciones que abren diálogos modales usan `QTimer.singleShot(0, ...)` para diferir la ejecución al siguiente ciclo del event loop |
| `src/ovpn_launcher/app.py` | `_rebuild_tray_menu()` en `_update_state()` también diferido con `QTimer.singleShot(0, ...)` |

## Acciones diferidas

- About, Settings (diálogos modales)
- Add, Edit, Remove, Import .ovpn, Import Profile, Export (abren QDialog/QFileDialog/QMessageBox)
- `_rebuild_tray_menu` (reconstruye menú durante procesamiento de evento)
