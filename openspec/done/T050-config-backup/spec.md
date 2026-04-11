# Spec — T050: Backup de config.yaml antes de guardar

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/profiles.py` | `_save_yaml()`: copia config.yaml a config.yaml.bak antes de sobreescribir |
