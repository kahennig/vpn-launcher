# T064 — Módulo platform.py — abstracción de rutas

> Discovery — 2026-04-11

## Contexto

`paths.py` define todas las rutas con convenciones Linux/XDG hardcodeadas. Para soportar Windows necesitamos que las rutas se resuelvan según la plataforma.

## Estado actual de paths.py (23 líneas)

| Constante | Valor Linux | Valor Windows esperado |
|-----------|-------------|----------------------|
| CONFIG_DIR | `~/.config/ovpn-launcher/` | `%APPDATA%/ovpn-launcher/` |
| CONFIG_YAML | `CONFIG_DIR/config.yaml` | igual |
| CONNECTIONS_CONF | `CONFIG_DIR/connections.conf` | igual (migración) |
| LOG_DIR | `CONFIG_DIR/logs/` | igual |
| OPENVPN_PREFIX | `/opt` | `C:/Program Files` |
| KEEPASS_DB | `~/Document/Keepass/keepass.kdbx` | `~/Documents/Keepass/keepass.kdbx` |
| AUTOSTART_DIR | `~/.config/autostart/` | N/A (T068 lo maneja) |
| AUTOSTART_DESKTOP | `AUTOSTART_DIR/ovpn-launcher.desktop` | N/A (T068 lo maneja) |
| `openvpn_binary()` system | `/usr/bin/openvpn` | `C:/Program Files/OpenVPN/bin/openvpn.exe` |
| `openvpn_binary()` versioned | `/opt/openvpn-{ver}/sbin/openvpn` | `{prefix}/openvpn-{ver}/bin/openvpn.exe` |

## Consumidores

- `app.py` — CONFIG_DIR, LOG_DIR, AUTOSTART_DIR, AUTOSTART_DESKTOP, OPENVPN_PREFIX, openvpn_binary
- `profiles.py` — CONNECTIONS_CONF, CONFIG_YAML, OPENVPN_PREFIX
- `cli.py` — openvpn_binary
- `tests/test_paths.py` — CONFIG_DIR, CONNECTIONS_CONF, CONFIG_YAML, openvpn_binary

## Enfoque

Modificar `paths.py` para que detecte la plataforma y resuelva las rutas según corresponda. No crear un módulo `platform.py` separado — paths.py ya es el lugar centralizado y son solo 23 líneas.

## Decisiones

1. Mantener paths.py como módulo único (no crear platform.py separado — sería over-engineering)
2. Usar `sys.platform` para detectar OS
3. AUTOSTART_DIR/AUTOSTART_DESKTOP quedan como Linux-only por ahora (T068 los manejará)
4. Los tests deben funcionar en ambas plataformas
