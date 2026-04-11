# T071 — Refactor app.py → lógica testeable sin GUI

> Discovery — 2026-04-11

## Contexto

`app.py` tiene 1477 líneas y 4 clases. Toda la lógica de negocio está acoplada a widgets Qt (QMessageBox, QFileDialog, QProcess, etc.), lo que hace imposible testearla en CI sin display gráfico.

El CI actual solo ejecuta `test_profiles.py` y `test_paths.py` — los tests de `test_app.py` requieren pytest-qt y no corren en CI.

## Estado actual de app.py

| Clase | Líneas aprox. | Responsabilidad |
|-------|---------------|-----------------|
| BuildDialog | 36-110 | Diálogo de compilación OpenVPN |
| SettingsDialog | 112-180 | Diálogo de configuración |
| ProfileDialog | 182-276 | Diálogo add/edit perfil |
| VPNLauncher | 278-1408 | **Todo lo demás** (~1130 líneas) |

## Lógica de negocio embebida en VPNLauncher

Candidatos a extraer (funciones puras o con dependencias mínimas, sin Qt):

### Grupo 1: Import/Export de perfiles
- `on_export_profile` → la serialización YAML del zip es lógica pura
- `on_import_zip` → el parsing del zip y validación es lógica pura
- `on_import_ovpn` → copiar archivo + crear profile dict

### Grupo 2: Credenciales
- `_get_keepass_creds` → invoca `keepassxc-cli` via subprocess (la parte de QInputDialog es GUI, pero el subprocess es lógica pura)

### Grupo 3: Validación y utilidades
- `_log_color` → función pura (texto → color)
- Validación de .ovpn (directives check) dentro de `on_connect` → lógica pura
- Construcción de argumentos de openvpn dentro de `on_connect` → lógica pura

### Grupo 4: Network checks
- `on_ping_profile` → extracción de host del .ovpn es lógica pura
- `on_dns_check` → solo invoca `dig`, poco que extraer

### Grupo 5: Diálogos como clases separadas
- `BuildDialog`, `SettingsDialog`, `ProfileDialog` ya son clases independientes pero viven en app.py

## Propuesta de módulos nuevos

| Módulo | Contenido | Testeable en CI |
|--------|-----------|-----------------|
| `src/ovpn_launcher/services.py` | Export/import zip, credenciales KeePass (subprocess), validación .ovpn, extracción de host, log coloring | ✅ Sí |
| `src/ovpn_launcher/dialogs.py` | BuildDialog, SettingsDialog, ProfileDialog (extraer de app.py) | ❌ Requiere Qt |

## Impacto en tests

- Nuevos tests en `tests/test_services.py` → corren en CI (sin Qt)
- `tests/test_app.py` sigue igual (pytest-qt)
- CI (`ci.yml`) se actualiza para incluir `test_services.py`

## Preguntas abiertas

1. **Nombre del módulo**: ¿`services.py` está bien o preferís otro nombre? (alternativas: `core.py`, `logic.py`, `operations.py`)
2. **Diálogos**: ¿Extraer los 3 diálogos a `dialogs.py` en esta misma tarea o dejarlo para después?
3. **Alcance**: ¿Extraer todo lo listado de una vez o hacerlo incremental (primero import/export + log_color, después credenciales, etc.)?
