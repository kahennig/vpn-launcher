# Spec — T019: Toolbar UX (iconos solos + reagrupar)

## Objetivo

Mejorar la toolbar: iconos sin texto (con tooltips) y reagrupar Import separado de Edit/Remove.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `ToolButtonTextBesideIcon` → `ToolButtonIconOnly` |
| `src/ovpn_launcher/app.py` | Reagrupar: Connect, Disconnect \| Reload, Clear \| Add, Import \| Edit, Remove \| ... Quit |
| `src/ovpn_launcher/app.py` | `setMinimumSize(780, 460)` → `setMinimumSize(580, 460)` |

## Agrupación

- Conexión: Connect, Disconnect
- Vista: Reload, Clear Log
- Crear: Add, Import
- Gestionar: Edit, Remove
- Quit al final con spacer
