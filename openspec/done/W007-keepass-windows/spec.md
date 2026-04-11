# W007 — KeePassXC CLI en Windows

> Spec — 2026-04-11

## Contexto

`keepassxc-cli` se hardcodea como nombre de comando. En Linux está en PATH. En Windows se instala en `C:\Program Files\KeePassXC\keepassxc-cli.exe` y no está en PATH.

Hay 2 puntos que lo usan:
- `services.py` → `fetch_keepass_creds()`
- `cli.py` → `get_credentials()`

## Cambios

### `src/ovpn_launcher/services.py`

Agregar función `keepassxc_cli_path()` que:
1. Intenta `shutil.which("keepassxc-cli")` — funciona si está en PATH (Linux, o Windows con PATH configurado)
2. En Windows, busca en `C:\Program Files\KeePassXC\keepassxc-cli.exe`
3. Devuelve la ruta o None

Actualizar `fetch_keepass_creds` para usar esta función.

### `src/ovpn_launcher/cli.py`

Refactorizar `get_credentials` para usar `fetch_keepass_creds` de services.py en vez de duplicar la lógica de keepassxc-cli.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/services.py` | Agregar `keepassxc_cli_path()`, actualizar `fetch_keepass_creds` |
| `src/ovpn_launcher/cli.py` | Usar `fetch_keepass_creds` de services |
| `tests/test_services.py` | Tests de `keepassxc_cli_path` |

## Criterios de aceptación

- [ ] `keepassxc_cli_path()` encuentra el binario en Linux (PATH)
- [ ] `keepassxc_cli_path()` busca en Program Files en Windows
- [ ] `fetch_keepass_creds` usa la ruta detectada
- [ ] cli.py no duplica lógica de keepassxc-cli
- [ ] Tests pasan
