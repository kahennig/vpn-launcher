# Spec — T041: Migrar config a YAML

## Objetivo

Migrar de connections.conf (pipe-delimited) a config.yaml con secciones settings y profiles.

## Alcance

**Incluye:** nuevo formato YAML, migración automática del formato viejo, actualizar profiles.py, paths.py, app.py, tests, config example.
**No incluye:** pantalla de Settings (T042), migración del CLI (T043).

## Formato nuevo: `~/.config/ovpn-launcher/config.yaml`

```yaml
settings:
  openvpn_prefix: /opt
  keepass_db: ~/Document/Keepass/keepass.kdbx
  connection_timeout: 30
  reconnect_delay: 5
  ip_service: https://api.ipify.org
  log_level: WARNING

profiles:
  - alias: client-a
    version: "2.6.14"
    config: /home/user/.config/ovpn-launcher/configs/client-a.ovpn
    auth_mode: keepass
    keepass_entry: VPN Client A

  - alias: office
    version: system
    config: /home/user/.config/ovpn-launcher/configs/office.ovpn
```

## Fases

### F0 — Nuevo formato y migración

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/paths.py` | Agregar `CONFIG_YAML = CONFIG_DIR / "config.yaml"` |
| `src/ovpn_launcher/profiles.py` | Reescribir load/save para YAML, agregar `migrate_legacy_config()`, `load_settings()`, `save_settings()` |
| `pyproject.toml` | Agregar `pyyaml>=6.0` a dependencies |

**Migración:**
- Al cargar, si `config.yaml` no existe pero `connections.conf` sí → migrar automáticamente
- Escribir `config.yaml` con settings defaults + profiles convertidos
- No borrar `connections.conf` (backup)

### F1 — Integrar en la app

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Usar settings para timeout, reconnect delay, IP service, log level |
| `src/ovpn_launcher/app.py` | Usar `openvpn_prefix` de settings en vez de constante |
| `src/ovpn_launcher/paths.py` | `openvpn_binary()` recibe prefix como parámetro |

### F2 — Config example y tests

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `config/config.yaml.example` | Nuevo ejemplo YAML |
| `config/connections.conf.example` | Mantener como referencia legacy |
| `tests/test_profiles.py` | Actualizar tests para YAML |
| `tests/test_paths.py` | Actualizar si paths cambian |
