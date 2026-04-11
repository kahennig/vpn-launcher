# Spec — T027: Config validation on load

## Objetivo

Al cargar perfiles, validar que los binarios y configs existen y mostrar warnings visuales en el tree.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `reload_profiles()`: validar cada perfil, mostrar ícono warning si binary o config no existe |
| `src/ovpn_launcher/app.py` | Tooltip del item muestra qué falta |

## Comportamiento

- Si el binary no existe → ícono `dialog-warning` + tooltip "OpenVPN binary not found: /opt/..."
- Si el config no existe → ícono `dialog-warning` + tooltip "Config file not found: /path/..."
- Si ambos OK → ícono `network-vpn` normal
- No bloquea la carga, solo feedback visual
