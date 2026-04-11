# Spec — T036: Logging con Python logging module

## Objetivo

Agregar logging estructurado con el módulo logging de Python para debugging.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `import logging`, logger al inicio, reemplazar info relevante con logger.debug/info/warning |
| `src/ovpn_launcher/app.py` | `main()`: configurar logging con nivel desde env var `OVPN_LOG_LEVEL` (default WARNING) |

## Comportamiento

- Por defecto: solo WARNING+ va a stderr
- `OVPN_LOG_LEVEL=DEBUG ovpn-app` → muestra todo
- No afecta el log de conexión (QTextEdit), solo logging interno de la app
