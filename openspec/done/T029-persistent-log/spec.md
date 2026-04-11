# Spec — T029: Log persistente a archivo

## Objetivo

Guardar el log de cada conexión a un archivo para debugging post-mortem.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/paths.py` | Constante `LOG_DIR = CONFIG_DIR / "logs"` |
| `src/ovpn_launcher/app.py` | Al conectar: abrir archivo de log `LOG_DIR/{alias}_{timestamp}.log` |
| `src/ovpn_launcher/app.py` | `_on_read_output()`: escribir también al archivo |
| `src/ovpn_launcher/app.py` | `_cleanup()`: cerrar archivo de log |

## Formato del archivo

- Nombre: `{alias}_{YYYY-MM-DD_HH-MM-SS}.log`
- Contenido: mismo texto que aparece en el QTextEdit
