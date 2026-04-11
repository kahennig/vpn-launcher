# T064 — Módulo platform.py — abstracción de rutas

> Spec — 2026-04-11

## Objetivo

Hacer que paths.py resuelva rutas según la plataforma (Linux vs Windows) sin romper nada en Linux.

## Cambios en `src/ovpn_launcher/paths.py`

```python
import sys
from pathlib import Path
import os

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    _config_base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    CONFIG_DIR = _config_base / "ovpn-launcher"
    AUTOSTART_DIR = None
    AUTOSTART_DESKTOP = None
    OPENVPN_PREFIX = Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
    KEEPASS_DB = Path(os.environ.get(
        "OVPN_KEEPASS_DB",
        Path.home() / "Documents" / "Keepass" / "keepass.kdbx",
    ))
else:
    XDG_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    CONFIG_DIR = XDG_CONFIG / "ovpn-launcher"
    AUTOSTART_DIR = XDG_CONFIG / "autostart"
    AUTOSTART_DESKTOP = AUTOSTART_DIR / "ovpn-launcher.desktop"
    OPENVPN_PREFIX = Path("/opt")
    KEEPASS_DB = Path(os.environ.get(
        "OVPN_KEEPASS_DB",
        Path.home() / "Document" / "Keepass" / "keepass.kdbx",
    ))

CONNECTIONS_CONF = CONFIG_DIR / "connections.conf"
CONFIG_YAML = CONFIG_DIR / "config.yaml"
LOG_DIR = CONFIG_DIR / "logs"


def openvpn_binary(version: str, prefix: Path = OPENVPN_PREFIX) -> Path:
    if version == "system":
        if IS_WINDOWS:
            return Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "OpenVPN" / "bin" / "openvpn.exe"
        return Path("/usr/bin/openvpn")
    if IS_WINDOWS:
        return prefix / f"openvpn-{version}" / "bin" / "openvpn.exe"
    return prefix / f"openvpn-{version}" / "sbin" / "openvpn"
```

## Cambios en `src/ovpn_launcher/app.py`

Guard para AUTOSTART donde se usa (ya que en Windows será None):

```python
# En _setup_toolbar, donde se chequea AUTOSTART_DESKTOP:
self.action_autostart.setChecked(AUTOSTART_DESKTOP is not None and AUTOSTART_DESKTOP.is_file())

# En _toggle_autostart:
if AUTOSTART_DIR is None:
    return
```

## Cambios en `tests/test_paths.py`

Hacer los tests cross-platform: los valores esperados dependen de `sys.platform`.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/paths.py` | Bifurcación Linux/Windows |
| `src/ovpn_launcher/app.py` | Guard para AUTOSTART None en Windows |
| `tests/test_paths.py` | Tests cross-platform |

## Criterios de aceptación

- [ ] En Linux: todas las rutas se resuelven igual que antes
- [ ] En Windows: CONFIG_DIR usa %APPDATA%, OPENVPN_PREFIX usa Program Files
- [ ] AUTOSTART_DIR/AUTOSTART_DESKTOP son None en Windows
- [ ] app.py no crashea si AUTOSTART es None
- [ ] openvpn_binary devuelve .exe en Windows
- [ ] Tests pasan en Linux
- [ ] Tests pasan en Windows (validación en VM)
