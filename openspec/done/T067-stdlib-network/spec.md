# T067 — Reemplazar curl/dig por Python stdlib

> Spec — 2026-04-11

## Contexto

- `_fetch_public_ip` usa `curl` via QProcess para obtener IP pública
- `on_dns_check` usa `dig` via QProcess para DNS leak check

Ni `curl` ni `dig` existen en Windows. Reemplazar por `urllib` y `socket`.

## Cambios

### `src/ovpn_launcher/services.py` — funciones puras

```python
def fetch_public_ip(url="https://api.ipify.org", timeout=5):
    """Fetch public IP. Returns IP string or empty string on failure."""

def dns_resolver_ip(timeout=5):
    """Check DNS resolver via Akamai whoami. Returns IP string or empty string."""
```

`fetch_public_ip` usa `urllib.request.urlopen`.
`dns_resolver_ip` usa `socket.getaddrinfo` para resolver `whoami.akamai.net` via el DNS del sistema.

### `src/ovpn_launcher/app.py`

Reemplazar QProcess+curl/dig por llamadas a services en un thread (para no bloquear la GUI), usando QTimer.singleShot o threading + signal.

Enfoque: usar `threading.Thread` + `QMetaObject.invokeMethod` para actualizar la GUI desde el thread, similar a como ya se hace en BuildDialog.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/services.py` | Agregar fetch_public_ip, dns_resolver_ip |
| `src/ovpn_launcher/app.py` | Reemplazar QProcess curl/dig por threading + services |
| `tests/test_services.py` | Tests de ambas funciones |

## Criterios de aceptación

- [ ] fetch_public_ip funciona sin curl
- [ ] dns_resolver_ip funciona sin dig
- [ ] IP pública se muestra en status bar
- [ ] DNS check funciona desde el menú
- [ ] No se bloquea la GUI durante las operaciones
- [ ] Tests cubren ambas funciones
- [ ] Tests pasan, app funciona en Linux
