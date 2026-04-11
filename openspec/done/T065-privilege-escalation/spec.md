# T065 — Abstracción de escalación de privilegios

> Spec — 2026-04-11

## Contexto

3 puntos hardcodean `pkexec` (GUI) y `sudo` (CLI):
- `app.py:870` — `self.process.setProgram("pkexec")` para lanzar openvpn
- `app.py:901` — `subprocess.run(["pkexec", "kill", ...])` para matar openvpn
- `cli.py:184` — `args = ["sudo", str(binary), ...]` para lanzar openvpn

En Windows no existe pkexec ni sudo. OpenVPN se ejecuta directamente (el instalador de OpenVPN configura un servicio, o se usa runas).

## Cambios

Agregar funciones en `services.py`:

```python
def elevate_command(command: list[str], gui: bool = False) -> list[str]:
    """Wrap a command with privilege escalation for the current platform."""
    if IS_WINDOWS:
        return command  # Windows: OpenVPN runs as service or via runas (T: W002)
    return ["pkexec" if gui else "sudo"] + command

def kill_command(pid: int, gui: bool = False) -> list[str]:
    """Build a command to kill a process with elevated privileges."""
    if IS_WINDOWS:
        return ["taskkill", "/F", "/PID", str(pid)]
    return ["pkexec" if gui else "sudo", "kill", str(pid)]
```

Luego reemplazar los 3 puntos hardcodeados.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/services.py` | Agregar `elevate_command()` y `kill_command()` |
| `src/ovpn_launcher/app.py` | Usar `elevate_command(gui=True)` y `kill_command(gui=True)` |
| `src/ovpn_launcher/cli.py` | Usar `elevate_command(gui=False)` |
| `tests/test_services.py` | Tests de ambas funciones |

## Criterios de aceptación

- [ ] `elevate_command` devuelve pkexec/sudo en Linux, comando directo en Windows
- [ ] `kill_command` devuelve pkexec kill en Linux, taskkill en Windows
- [ ] app.py y cli.py usan las funciones de services.py
- [ ] Tests cubren ambas plataformas (mockeando IS_WINDOWS)
- [ ] Tests pasan, app funciona en Linux
