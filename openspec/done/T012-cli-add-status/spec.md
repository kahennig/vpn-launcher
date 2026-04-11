# Spec — T012: CLI --add y --status

## Objetivo

Agregar comandos --add y --status al CLI para paridad con la GUI.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `scripts/ovpn-connect` | Funciones `add_profile()` y `show_status()`, parsing de --add y --status flags |

## Comportamiento

- `--add`: prompt interactivo para alias, version, config, auth_mode. Valida alias único. Appende a connections.conf.
- `--status` / `-s`: verifica si hay proceso openvpn corriendo con `pgrep -x openvpn`, muestra PID.
