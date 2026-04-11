# Spec — T049: Validar .ovpn antes de conectar

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `on_connect()`: antes de lanzar QProcess, verificar que el .ovpn tiene `remote` y `dev`. Warning si falta, pero permite continuar. |
