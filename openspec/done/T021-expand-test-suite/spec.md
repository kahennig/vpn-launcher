# Spec — T021: Expandir batería de tests

## Objetivo

Cubrir paths.py, edge cases de profiles.py y ProfileDialog con tests.

## Alcance

**Incluye:** tests para openvpn_binary, constantes de paths, edge cases de save/load, ProfileDialog (validación, pre-llenado, get_profile).
**No incluye:** tests de VPNLauncher (conexión, tray, state machine — requieren mocking complejo).

## Fases

### F0 — Tests para paths.py

**Archivo:** `tests/test_paths.py`

**Tests:**
- `openvpn_binary("system")` retorna `/usr/bin/openvpn`
- `openvpn_binary("2.6.14")` retorna `/opt/openvpn-2.6.14/sbin/openvpn`
- `CONFIG_DIR` termina en `ovpn-launcher`
- `CONNECTIONS_CONF` termina en `connections.conf`
- `CONNECTIONS_CONF` está dentro de `CONFIG_DIR`

### F1 — Edge cases de profiles.py

**Archivo:** `tests/test_profiles.py` (agregar)

**Tests:**
- `save_profiles` con lista vacía → archivo solo con header (o vacío)
- `save_profiles` a archivo nuevo sin header previo
- `load_profiles` con whitespace en auth_mode (`" Keepass "` → `"keepass"`)
- Roundtrip: save → load preserva orden de perfiles
- `load_profiles` con auth_mode `prompt`

### F2 — Tests de ProfileDialog

**Archivo:** `tests/test_app.py`

**Tests (con pytest-qt):**
- Modo add: campos vacíos por defecto
- Modo edit: campos pre-llenados con datos del perfil
- `get_profile()` retorna dict correcto
- Validación: alias vacío no acepta
- Validación: alias duplicado no acepta
- Validación: config vacío no acepta
