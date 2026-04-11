# Spec — T063: Build OpenVPN desde la GUI

## Objetivo

Diálogo para descargar, compilar e instalar versiones de OpenVPN desde la GUI.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/builder.py` | Nuevo módulo: fetch_available_versions (GitHub API), build_openvpn (Python, reemplaza bash script) |
| `src/ovpn_launcher/app.py` | BuildDialog con combo de versiones + progreso, acción en toolbar y hamburger |

## Detección de versiones disponibles

- GitHub API: `https://api.github.com/repos/OpenVPN/openvpn/tags`
- Filtrar solo releases estables (vX.Y.Z, sin rc/alpha/beta)
- Excluir versiones ya instaladas en /opt/
- Combo editable para tipear manualmente

## Descarga y compilación (builder.py)

- URL: `https://swupdate.openvpn.net/community/releases/openvpn-{version}.tar.gz`
- Pasos: download → extract → configure → make → install
- Cada paso reporta progreso via callback
- Prefix: configurable desde settings (openvpn_prefix)
- Flags: `--disable-dco --quiet`
- Requiere pkexec para make install

## BuildDialog

- Combo editable con versiones disponibles (async fetch)
- Botón "Build"
- QTextEdit de progreso (read-only)
- Botón Close (deshabilitado durante build)
- Al completar: reload profiles para detectar nueva versión
