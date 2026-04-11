# Spec — T026: Copiar log al clipboard

## Objetivo

Agregar acción para copiar todo el contenido del log al clipboard.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Nueva acción `action_copy_log` con ícono `edit-copy`, shortcut Ctrl+Shift+C |
| `src/ovpn_launcher/app.py` | Agregar al menú hamburguesa junto a Clear Log |
| `src/ovpn_launcher/app.py` | Método: `QApplication.clipboard().setText(self.log_output.toPlainText())` |
