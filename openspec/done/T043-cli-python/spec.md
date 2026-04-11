# Spec — T043: Migrar CLI a Python

## Objetivo

Reescribir ovpn-connect en Python para que lea config.yaml y comparta código con la GUI.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/cli.py` | Nuevo módulo CLI en Python |
| `pyproject.toml` | Entry point: `ovpn-connect = ovpn_launcher.cli:main` |
| `scripts/ovpn-connect` | Mantener como legacy (no borrar) |
| `Makefile` | Actualizar install para no copiar el bash script (pip lo instala) |

## Comandos

- `ovpn-connect <alias>` — conectar por perfil
- `ovpn-connect <version> <config.ovpn>` — modo directo
- `ovpn-connect --list` / `-l` — listar versiones y perfiles
- `ovpn-connect --add` — agregar perfil interactivo
- `ovpn-connect --status` / `-s` — verificar si openvpn corre
- `ovpn-connect --version` / `-v` — mostrar versión (T058 gratis)

## Implementación

- Usa argparse para parseo de argumentos
- Reutiliza: load_profiles, save_profiles, load_settings, detect_versions, openvpn_binary de profiles.py y paths.py
- KeePass: subprocess con keepassxc-cli (mismo approach que bash)
- Privilegios: sudo (mismo que bash)
- Auth file: tempfile con 0600, cleanup con atexit
