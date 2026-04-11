# Spec — T022: Fix crash al hacer clic en tray icon

## Problema

Crash intermitente (SIGABRT) al hacer clic izquierdo en el system tray icon. El stack trace muestra:
- `QSystemTrayIcon::activated` → `PyQtSlotProxy::qt_metacall` → `pyqt6_err_print` → `qAbort`

## Causa raíz

Dos problemas:
1. `_tray_connect(profile)` no validaba que `profile` fuera no-None. Cuando `_rebuild_tray_menu()` reemplaza el menú, las QAction viejas pueden tener `data()` = None momentáneamente.
2. `_on_tray_activated` no tenía protección contra excepciones. Una excepción no capturada en un slot de PyQt6 causa SIGABRT (fatal de Qt).

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_tray_connect()`: guard `if not profile: return` |
| `src/ovpn_launcher/app.py` | `_on_tray_activated()`: try/except alrededor de `_toggle_window()` |
