# T070 — Migrar import/export de perfiles a YAML + limpiar referencias legacy

> Discovery — 2026-04-11

## Contexto

Desde T041 toda la configuración de la app se maneja en formato YAML (`config.yaml`). Sin embargo, el import/export de perfiles sigue usando el formato legacy pipe-delimited dentro de los archivos `.zip`.

## Problemas detectados

### P1: Export genera `profile.conf` con formato pipe-delimited

**Archivo**: `src/ovpn_launcher/app.py` línea ~945

```python
zf.writestr("profile.conf", "|".join(parts) + "\n")
```

El zip exportado contiene un archivo `profile.conf` con formato `alias|version|config_name|auth_mode`. Esto es inconsistente con el formato YAML que usa la app internamente.

### P2: Export no incluye `keepass_entry`

**Archivo**: `src/ovpn_launcher/app.py` líneas ~940-945

El campo `keepass_entry` (agregado en T038) se pierde al exportar. Solo se exportan `alias`, `version`, `config_name` y `auth_mode`.

### P3: Import espera formato pipe-delimited

**Archivo**: `src/ovpn_launcher/app.py` líneas ~867-875

`on_import_zip` busca `profile.conf` y parsea con `split("|")`. No soporta YAML ni el campo `keepass_entry`.

### P4: Tooltip de Reload dice "connections.conf"

**Archivo**: `src/ovpn_launcher/app.py` línea 335

```python
self.action_reload.setToolTip("Reload profiles from connections.conf")
```

Debería decir `config.yaml`.

### P5: Import innecesario de `CONNECTIONS_CONF` en app.py

**Archivo**: `src/ovpn_launcher/app.py` línea 25

```python
from .paths import CONNECTIONS_CONF, openvpn_binary
```

`CONNECTIONS_CONF` no se usa en ningún otro lugar de `app.py`. El import sobra.

### P6: `CONNECTIONS_CONF` en paths.py solo se usa para migración

**Archivo**: `src/ovpn_launcher/paths.py` línea 10

La constante `CONNECTIONS_CONF` solo se referencia en:
- `profiles.py` líneas 53 y 89 (migración legacy → YAML)
- `app.py` línea 25 (import sin uso)
- `tests/test_profiles.py` (tests de migración)
- `tests/test_paths.py` (tests de la constante misma)

La constante debe mantenerse en `paths.py` porque la migración legacy sigue siendo necesaria para usuarios que actualicen desde versiones anteriores. Pero el import en `app.py` sobra.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Migrar export/import a YAML, fix tooltip, quitar import CONNECTIONS_CONF |
| `tests/test_app.py` | Actualizar tests de import/export |

## Decisiones

1. **Sin retrocompatibilidad**: No se soporta el formato pipe-delimited en import. Único usuario, no hay zips legacy que migrar.
2. **Nombre del archivo en el zip**: `profile.yaml`

## Propuesta de alcance

- Migrar `on_export_profile` para escribir `profile.yaml` (YAML) incluyendo todos los campos del perfil
- Migrar `on_import_zip` para leer `profile.yaml` (YAML), sin fallback legacy
- Fix tooltip de Reload
- Quitar import innecesario de `CONNECTIONS_CONF` en app.py
- Actualizar tests existentes de import/export
