# Spec — T062: Expandir tests v2

## Objetivo

Cubrir gaps de testing post-migración YAML, SettingsDialog, log colors, y reload_profiles.

## Fases

### F0 — profiles.py gaps

| Test | Archivo |
|------|---------|
| save/load con last_connected | test_profiles.py |
| save crea backup .yaml.bak | test_profiles.py |
| load auto-migra si config.yaml no existe | test_profiles.py |

### F1 — ProfileDialog gaps

| Test | Archivo |
|------|---------|
| keepass_entry field hidden si auth_mode != keepass | test_app.py |
| keepass_entry field visible si auth_mode = keepass | test_app.py |
| get_profile incluye keepass_entry | test_app.py |

### F2 — SettingsDialog

| Test | Archivo |
|------|---------|
| Campos pre-llenados con settings | test_app.py |
| get_settings retorna dict correcto | test_app.py |
| Defaults si settings vacío | test_app.py |

### F3 — VPNLauncher

| Test | Archivo |
|------|---------|
| reload_profiles carga items en tree | test_app.py |
| _log_color retorna colores correctos | test_app.py |
