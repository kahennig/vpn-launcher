# Spec — T006: Import de .ovpn

## Objetivo

Permitir importar un archivo .ovpn copiándolo a configs/ y creando un perfil automáticamente.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acción Import .ovpn en toolbar, método `on_import_ovpn()` |
| `src/ovpn_launcher/app.py` | Import CONFIG_DIR desde paths.py |

## Comportamiento

- File picker con filtro .ovpn/.conf
- Copia archivo a `~/.config/ovpn-launcher/configs/`
- Si ya existe, pregunta si sobreescribir
- Abre ProfileDialog pre-llenado (alias = nombre del archivo sin extensión, version = system, config = ruta destino)
- Se deshabilita durante conexión activa
