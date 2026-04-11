# T071 — Refactor app.py → lógica testeable sin GUI

> Spec — 2026-04-11

## Objetivo

Reducir app.py extrayendo lógica de negocio a `services.py` (testeable en CI sin Qt) y diálogos a `dialogs.py` (reduce tamaño). Resultado esperado: app.py pasa de ~1477 líneas a ~900-1000.

## Fases

### F0 — Extraer diálogos a `dialogs.py`

Mover BuildDialog, SettingsDialog y ProfileDialog a `src/ovpn_launcher/dialogs.py`. app.py los importa desde ahí.

**Archivos:**
- Crear `src/ovpn_launcher/dialogs.py` — las 3 clases + sus imports Qt
- Modificar `src/ovpn_launcher/app.py` — reemplazar clases por imports desde dialogs
- Modificar `tests/test_app.py` — actualizar imports

**Criterios:**
- [ ] Las 3 clases viven en dialogs.py
- [ ] app.py importa desde dialogs
- [ ] 58 tests pasan
- [ ] La app funciona (validación manual)

### F1 — Extraer lógica pura a `services.py`

Crear `src/ovpn_launcher/services.py` con funciones puras extraídas de VPNLauncher:

| Función | Origen en app.py | Firma |
|---------|-------------------|-------|
| `log_color(text)` | `_log_color` | `str → str \| None` |
| `validate_ovpn(config_path)` | lógica dentro de `on_connect` | `Path → list[str]` (missing directives) |
| `extract_remote_host(config_path)` | lógica dentro de `on_ping_profile` | `Path → str \| None` |
| `export_profile_zip(profile, dest)` | `on_export_profile` | `dict, Path → None` |
| `import_profile_zip(src)` | `on_import_zip` | `Path → tuple[dict, bytes \| None]` (meta + ovpn content) |
| `fetch_keepass_creds(entry, db_path, master_pw)` | `_get_keepass_creds` | `str, Path, str → tuple[str,str] \| None` |

**Archivos:**
- Crear `src/ovpn_launcher/services.py`
- Modificar `src/ovpn_launcher/app.py` — reemplazar lógica inline por llamadas a services
- Crear `tests/test_services.py` — tests de todas las funciones
- Modificar `.github/workflows/ci.yml` — agregar `test_services.py`

**Criterios:**
- [ ] Todas las funciones en services.py son puras (sin dependencia Qt)
- [ ] tests/test_services.py cubre todas las funciones
- [ ] CI ejecuta test_services.py
- [ ] 58+ tests pasan (los existentes + los nuevos)
- [ ] La app funciona (validación manual)

## Archivos impactados (total)

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/dialogs.py` | **Nuevo** — 3 clases de diálogo |
| `src/ovpn_launcher/services.py` | **Nuevo** — funciones puras de lógica de negocio |
| `src/ovpn_launcher/app.py` | Reducir: importar dialogs + delegar a services |
| `tests/test_app.py` | Actualizar imports de diálogos |
| `tests/test_services.py` | **Nuevo** — tests de services.py |
| `.github/workflows/ci.yml` | Agregar test_services.py |
