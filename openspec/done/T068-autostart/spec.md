# T068 — Abstracción de autostart

> Spec — 2026-04-11

## Contexto

Autostart actualmente es Linux-only (.desktop file). En Windows se usa la carpeta Startup del usuario (`shell:startup`). El enfoque más simple y portable es la carpeta Startup (no requiere permisos de admin, a diferencia del Registry).

## Cambios

### `src/ovpn_launcher/services.py`

```python
def is_autostart_enabled() -> bool:
def enable_autostart() -> None:
def disable_autostart() -> None:
```

- Linux: escribe/borra `.desktop` en `~/.config/autostart/`
- Windows: crea/borra un `.vbs` wrapper en `%APPDATA%/Microsoft/Windows/Start Menu/Programs/Startup/`
  (un .vbs que ejecuta `pythonw -m ovpn_launcher.app` para evitar ventana de consola)

### `src/ovpn_launcher/paths.py`

Agregar rutas de autostart para Windows:
- `AUTOSTART_DIR` = Startup folder
- `AUTOSTART_FILE` = archivo de autostart (.desktop en Linux, .vbs en Windows)

### `src/ovpn_launcher/app.py`

Reemplazar lógica inline por llamadas a services.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/paths.py` | AUTOSTART_DIR y AUTOSTART_FILE para Windows |
| `src/ovpn_launcher/services.py` | 3 funciones de autostart |
| `src/ovpn_launcher/app.py` | Delegar a services, quitar guard None |
| `tests/test_services.py` | Tests de autostart |

## Criterios de aceptación

- [ ] Autostart funciona en Linux (igual que antes)
- [ ] Autostart paths definidos para Windows
- [ ] Funciones puras testeables en CI
- [ ] Tests pasan
- [ ] App funciona en Linux
