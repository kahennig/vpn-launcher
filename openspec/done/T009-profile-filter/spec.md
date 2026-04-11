# Spec — T009: Filtro rápido de perfiles

## Objetivo

Permitir filtrar perfiles por nombre desde un campo de texto.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | QLineEdit `profile_filter` arriba del tree, método `_filter_profiles()` |

## Comportamiento

- QLineEdit con placeholder "Filter profiles…" y botón clear
- Filtra en tiempo real por nombre de perfil (case-insensitive)
- Oculta items que no coinciden con `setHidden()`
