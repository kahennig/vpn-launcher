# Spec — T052/T053: Abrir carpetas en file manager

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acciones "Open Configs Folder" y "Open Logs Folder" en hamburger menu |
| `src/ovpn_launcher/app.py` | `_open_folder()`: usa QDesktopServices.openUrl para abrir en file manager del sistema |
