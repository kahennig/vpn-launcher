# W009 — Instalador Windows (PyInstaller)

> Spec — 2026-04-11

## Objetivo

Generar un .exe standalone para Windows que incluya Python + PyQt6 + la app. El usuario descarga, ejecuta, y listo.

## Cambios

### `scripts/build-windows.py`

Script de PyInstaller que genera el .exe:
- Entry point: `src/ovpn_launcher/app.py:main`
- Incluye el ícono SVG como dato
- `--onefile --windowed --name ovpn-launcher`
- Icono de la app como .ico para el .exe

### `share/icons/ovpn-launcher.ico`

Convertir el SVG existente a .ico (multi-resolución: 16, 32, 48, 256px) para el .exe de Windows.

### `ovpn-launcher.spec` (PyInstaller spec)

Archivo de configuración de PyInstaller para builds reproducibles.

### `.github/workflows/build-windows.yml`

Workflow separado que:
1. Se dispara en tags `v*` (releases)
2. Instala Python + PyInstaller + dependencias
3. Genera el .exe
4. Lo sube como artifact del release

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `ovpn-launcher.spec` | **Nuevo** — PyInstaller spec |
| `share/icons/ovpn-launcher.ico` | **Nuevo** — Ícono Windows |
| `.github/workflows/build-windows.yml` | **Nuevo** — CI para generar .exe |

## Criterios de aceptación

- [ ] PyInstaller spec genera .exe funcional
- [ ] .exe incluye ícono de la app
- [ ] .exe arranca sin Python instalado en Windows
- [ ] CI genera .exe en tags v*
- [ ] No rompe nada en Linux
