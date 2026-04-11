# Spec — T047: Notificación con IP al conectar

## Objetivo

Que la notificación de tray al conectar incluya la IP pública.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_update_state(CONNECTED)`: no mostrar notificación inmediata, dejar que `_on_ip_fetched` la muestre |
| `src/ovpn_launcher/app.py` | `_on_ip_fetched()`: si state=CONNECTED, mostrar "Connected to X — IP: Y" |
