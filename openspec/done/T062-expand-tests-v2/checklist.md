# Checklist — T062: Expandir tests v2

## F0 — profiles.py

- [x] save/load roundtrip con last_connected
- [x] save crea .yaml.bak
- [x] load auto-migra desde connections.conf

## F1 — ProfileDialog

- [x] keepass_entry hidden si auth_mode != keepass
- [x] keepass_entry visible si auth_mode = keepass
- [x] get_profile incluye keepass_entry

## F2 — SettingsDialog

- [x] Campos pre-llenados
- [x] get_settings retorna dict correcto
- [x] Defaults si settings vacío

## F3 — VPNLauncher

- [x] reload_profiles carga items en tree
- [x] _log_color: error → rojo
- [x] _log_color: warn → naranja
- [x] _log_color: success → verde
- [x] _log_color: internal → muted
- [x] _log_color: normal → None
