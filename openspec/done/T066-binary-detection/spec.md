# T066 — Abstracción de detección de binarios OpenVPN

> Spec — 2026-04-11

## Contexto

`detect_versions()` y `installed_versions()` hardcodean paths Linux:
- `/usr/bin/openvpn` para system
- glob `openvpn-*/sbin/openvpn` para versiones compiladas

En Windows:
- System OpenVPN está en `C:/Program Files/OpenVPN/bin/openvpn.exe`
- Versiones compiladas no aplican (se descargan binarios, W004), pero el glob debería buscar `openvpn-*/bin/openvpn.exe`

## Cambios

### `src/ovpn_launcher/profiles.py` — `detect_versions()`

Usar `openvpn_binary("system")` de paths.py para la ruta del system binary, y adaptar el glob según plataforma.

### `src/ovpn_launcher/builder.py` — `installed_versions()`

Adaptar el glob según plataforma.

### Constantes auxiliares en `paths.py`

Agregar `OPENVPN_GLOB` para el patrón de búsqueda de binarios:
- Linux: `openvpn-*/sbin/openvpn`
- Windows: `openvpn-*/bin/openvpn.exe`

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/paths.py` | Agregar OPENVPN_GLOB |
| `src/ovpn_launcher/profiles.py` | Usar openvpn_binary("system") + OPENVPN_GLOB |
| `src/ovpn_launcher/builder.py` | Usar OPENVPN_GLOB |
| `tests/test_services.py` | No (lógica ya testeada en test_profiles.py) |

## Criterios de aceptación

- [ ] detect_versions usa openvpn_binary("system") en vez de path hardcodeado
- [ ] detect_versions y installed_versions usan OPENVPN_GLOB
- [ ] En Linux: comportamiento idéntico al actual
- [ ] Tests pasan
- [ ] App funciona en Linux
