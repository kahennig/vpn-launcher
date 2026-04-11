# Spec — T059: Ícono custom de la app

## Cambios

| Archivo | Cambio |
|---------|--------|
| `share/icons/ovpn-launcher.svg` | Nuevo: SVG escudo azul con candado |
| `src/ovpn_launcher/app.py` | `_app_icon()`: busca custom SVG, fallback a theme |
| `share/applications/ovpn-launcher.desktop` | Icon=ovpn-launcher |
| `Makefile` | Instala SVG a /usr/local/share/icons/ |
