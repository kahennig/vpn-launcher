# Checklist — T041: Migrar config a YAML

## F0 — Formato y migración

- [x] CONFIG_YAML definido en paths.py
- [x] load_profiles lee de config.yaml
- [x] save_profiles escribe config.yaml
- [x] load_settings / save_settings para sección settings
- [x] migrate_legacy_config convierte connections.conf → config.yaml
- [x] Migración automática al cargar si config.yaml no existe
- [x] pyyaml en dependencies

## F1 — Integrar en la app

- [x] CONNECTION_TIMEOUT lee de settings
- [x] Reconnect delay lee de settings
- [x] IP service URL lee de settings
- [x] Log level lee de settings
- [x] openvpn_prefix lee de settings

## F2 — Config example y tests

- [x] config.yaml.example creado
- [x] Tests actualizados para YAML
- [x] Tests de migración legacy
- [x] Todos los tests pasan
