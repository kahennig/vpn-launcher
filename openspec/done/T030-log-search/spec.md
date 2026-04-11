# Spec — T030: Búsqueda en el log (Ctrl+F)

## Objetivo

Permitir buscar texto en el log de conexión con Ctrl+F.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | QLineEdit `_search_bar` debajo del log, oculto por defecto |
| `src/ovpn_launcher/app.py` | Ctrl+F muestra/oculta la barra, Enter busca siguiente |
| `src/ovpn_launcher/app.py` | Usa `QTextEdit.find()` para buscar y resaltar |

## Comportamiento

- Ctrl+F → toggle de la barra de búsqueda
- Escribir + Enter → busca siguiente ocurrencia
- Escape → oculta la barra
