# Spec — T051: Última conexión exitosa por perfil

## Objetivo

Mostrar en el tree cuándo fue la última conexión exitosa de cada perfil.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Columna "Last Connected" en el tree |
| `src/ovpn_launcher/app.py` | Al llegar a CONNECTED, guardar timestamp en profile y save |
| `src/ovpn_launcher/profiles.py` | Campo `last_connected` en profiles (string ISO, opcional) |
