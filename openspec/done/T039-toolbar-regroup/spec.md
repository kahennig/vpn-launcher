# Spec — T039: Renombrar y reagrupar acciones

## Objetivo

Renombrar "Import Zip" a "Import Profile" y reagrupar acciones en toolbar y hamburger menu.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Renombrar acción a "Import Profile" |
| `src/ovpn_launcher/app.py` | Reagrupar toolbar y hamburger menu |

## Agrupación (toolbar y hamburger)

- Conexión: Connect, Disconnect
- ABM perfiles: Add, Edit, Remove
- Import/Export: Import .ovpn, Import Profile, Export Profile
- Network tools: Ping Server, DNS Check (solo hamburger)
- Log: Reload, Clear Log, Copy Log
- Settings: Start at Login (solo hamburger)
- App: About, Quit (solo hamburger)
