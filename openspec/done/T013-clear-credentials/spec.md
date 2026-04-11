# Spec — T013: Limpiar credenciales de memoria

## Objetivo

Minimizar el tiempo que el master password de KeePass permanece en memoria.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_get_keepass_creds()`: `finally: password = None` después de usar el master password |

## Nota

Python no garantiza borrado inmediato de strings (GC), pero setear a None permite que el GC lo recolecte lo antes posible. Es un hardening best-effort.
