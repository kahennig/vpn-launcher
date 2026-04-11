# Spec — T046: Colores de estado en el log

## Objetivo

Colorear líneas del log según su contenido para facilitar lectura.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_on_read_output()`: insertar con color según contenido |
| `src/ovpn_launcher/app.py` | Líneas internas (`-- ... --`): color muted (PlaceholderText) |

## Reglas de color

- Contiene "error" o "ERROR" o "FATAL" → rojo (palette Link visited o hardcoded)
- Contiene "WARNING" o "WARN" → amarillo/naranja
- Contiene "Initialization Sequence Completed" → verde
- Líneas internas de la app (`-- ... --`) → color muted
- Todo lo demás → color normal
