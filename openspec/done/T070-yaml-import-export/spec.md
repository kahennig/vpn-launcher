# T070 — Migrar import/export de perfiles a YAML + limpiar referencias legacy

> Spec — 2026-04-11

## Objetivo

Alinear el import/export de perfiles con el formato YAML que usa la app internamente desde T041. Limpiar referencias legacy residuales.

## Cambios

### 1. `on_export_profile` → YAML (`app.py`)

Reemplazar la escritura de `profile.conf` (pipe-delimited) por `profile.yaml` (YAML).

**Antes:**
```python
parts = [profile["alias"], profile["version"], config_path.name]
if profile.get("auth_mode", "none") != "none":
    parts.append(profile["auth_mode"])
zf.writestr("profile.conf", "|".join(parts) + "\n")
```

**Después:**
```python
meta = {
    "alias": profile["alias"],
    "version": profile["version"],
    "config": config_path.name,
}
if profile.get("auth_mode", "none") != "none":
    meta["auth_mode"] = profile["auth_mode"]
if profile.get("keepass_entry"):
    meta["keepass_entry"] = profile["keepass_entry"]
zf.writestr("profile.yaml", yaml.dump(meta, default_flow_style=False))
```

### 2. `on_import_zip` → YAML (`app.py`)

Reemplazar la lectura de `profile.conf` (pipe-delimited) por `profile.yaml` (YAML).

**Antes:**
```python
if "profile.conf" not in zf.namelist():
    ...
conf_line = zf.read("profile.conf").decode().strip()
parts = conf_line.split("|")
if len(parts) < 3:
    ...
alias, version, ovpn_name = parts[0], parts[1], parts[2]
auth_mode = parts[3] if len(parts) >= 4 else "none"
```

**Después:**
```python
if "profile.yaml" not in zf.namelist():
    QMessageBox.warning(self, "Import", "No profile.yaml found in zip.")
    return
meta = yaml.safe_load(zf.read("profile.yaml").decode())
if not meta or not all(k in meta for k in ("alias", "version", "config")):
    QMessageBox.warning(self, "Import", "Invalid profile.yaml format.")
    return
alias = meta["alias"]
version = meta["version"]
ovpn_name = meta["config"]
auth_mode = meta.get("auth_mode", "none")
keepass_entry = meta.get("keepass_entry", "")
```

Y al construir el profile dict, incluir `keepass_entry`:
```python
profile = {
    "alias": alias, "version": version,
    "config": str(dest), "auth_mode": auth_mode,
}
if keepass_entry:
    profile["keepass_entry"] = keepass_entry
```

### 3. Fix tooltip de Reload (`app.py` línea 335)

```python
# Antes
self.action_reload.setToolTip("Reload profiles from connections.conf")
# Después
self.action_reload.setToolTip("Reload profiles from config.yaml")
```

### 4. Quitar import innecesario (`app.py` línea 25)

```python
# Antes
from .paths import CONNECTIONS_CONF, openvpn_binary
# Después
from .paths import openvpn_binary
```

### 5. Agregar `import yaml` en app.py

Ya se usa `yaml` en profiles.py pero no en app.py. Agregar el import.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Cambios 1-5 |

## Tests

No se agregan tests en esta tarea. La lógica de import/export vive dentro de métodos de `VPNLauncher` que dependen de Qt (diálogos, widgets). Testearlos requiere pytest-qt + display, que el CI no soporta.

**T071** abordará el refactor de app.py para extraer lógica de negocio a módulos puros testeables en CI.

## Criterios de aceptación

- [ ] Export genera zip con `profile.yaml` (YAML) en vez de `profile.conf` (pipe-delimited)
- [ ] Export incluye `keepass_entry` cuando existe
- [ ] Import lee `profile.yaml` y carga todos los campos incluyendo `keepass_entry`
- [ ] Import muestra error claro si falta `profile.yaml` o tiene formato inválido
- [ ] Tooltip de Reload dice "config.yaml"
- [ ] No hay import de `CONNECTIONS_CONF` en app.py
- [ ] Tests existentes siguen pasando (no se rompe nada)
