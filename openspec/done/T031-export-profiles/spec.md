# Spec — T031: Export de perfiles

## Objetivo

Exportar un perfil seleccionado como archivo .zip con el .ovpn y metadata.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acción Export en toolbar y hamburger, método `on_export_profile()` |

## Comportamiento

- Seleccionar perfil → Export → QFileDialog save → crea .zip con:
  - El archivo .ovpn (copia)
  - `profile.conf` con la línea del perfil (alias|version|config|auth_mode)
- El .ovpn dentro del zip usa nombre relativo (solo el filename)
