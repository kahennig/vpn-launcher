# Spec — T035: DNS leak check post-conexión

## Objetivo

Verificar que el DNS está pasando por la VPN después de conectar.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acción "DNS Check" en hamburger menu, método `on_dns_check()` |
| `src/ovpn_launcher/app.py` | Ejecuta `dig +short whoami.akamai.net @ns1-1.akamaitech.net` con QProcess |
| `src/ovpn_launcher/app.py` | Resultado en log: "DNS resolver: X.X.X.X" |

## Comportamiento

- Muestra la IP del resolver DNS que está usando el sistema
- Si coincide con la IP pública (sin VPN), hay leak
- Si es diferente (IP del VPN), está bien
- El usuario interpreta el resultado comparando con su IP pública
