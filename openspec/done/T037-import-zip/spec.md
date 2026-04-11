# Spec — T037: Import de perfil exportado (.zip)

## Objetivo

Permitir importar un perfil desde un .zip generado por Export (T031).

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acción "Import .zip" en hamburger menu y toolbar, método `on_import_zip()` |

## Comportamiento

1. File picker con filtro .zip
2. Extrae `profile.conf` del zip → parsea alias, version, config filename, auth_mode
3. Extrae el .ovpn a `~/.config/ovpn-launcher/configs/` (pregunta si sobreescribir)
4. Abre ProfileDialog pre-llenado con los datos del profile.conf (config apunta al destino)
5. Si acepta → agrega perfil, guarda, recarga
