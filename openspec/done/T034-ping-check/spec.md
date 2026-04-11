# Spec — T034: Ping/latency check pre-conexión

## Objetivo

Mostrar latencia al servidor VPN en el tree, para verificar alcanzabilidad antes de conectar.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acción "Ping" en hamburger menu, método `on_ping_profile()` |
| `src/ovpn_launcher/app.py` | Parsea `remote <host>` del .ovpn, ejecuta `ping -c 1 -W 3 <host>` con QProcess |
| `src/ovpn_launcher/app.py` | Resultado en log: "Ping <host>: 25ms" o "Ping <host>: unreachable" |

## Comportamiento

- Seleccionar perfil → Ping → parsea .ovpn → ping async → resultado en log
- Si no encuentra directiva `remote` → log warning
