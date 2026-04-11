# Spec — T033: IP pública en status bar

## Objetivo

Mostrar la IP pública actual en la status bar para confirmar que la VPN funciona.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | QLabel `_ip_label` en status bar (derecha) |
| `src/ovpn_launcher/app.py` | `_fetch_public_ip()`: QProcess con `curl -s --max-time 5 https://api.ipify.org` |
| `src/ovpn_launcher/app.py` | Fetch al iniciar, al conectar (CONNECTED), y al desconectar |

## Comportamiento

- Status bar: "[icon] Connected: alias — 00:05:32" a la izquierda, "IP: 1.2.3.4" a la derecha
- Fetch es async (QProcess) para no bloquear la UI
- Si falla: "IP: —"
