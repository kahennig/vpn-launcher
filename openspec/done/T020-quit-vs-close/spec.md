# Spec — T020: Distinguir Quit vs Close (X)

## Objetivo

Corregir que Quit mostraba el mensaje "Still running in the system tray" antes de cerrar la app.

## Problema

`quit_app()` llamaba `QApplication.quit()` pero `closeEvent` se disparaba antes mostrando el mensaje de tray, que no tenía sentido porque la app estaba terminando.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `quit_app()`: llamar `self.tray.hide()` antes de `QApplication.quit()` |

## Comportamiento

- **X (close)** → minimiza a tray, muestra "Still running in the system tray"
- **Quit** → desconecta, oculta tray, cierra la app sin mensaje
