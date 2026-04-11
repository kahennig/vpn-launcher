# Spec — T044: Columna KeePass entry en el tree

## Objetivo

Mostrar en el QTreeWidget qué entrada de KeePass usa cada perfil, a la derecha de la columna Auth.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Agregar columna "KeePass Entry" al header del tree |
| `src/ovpn_launcher/app.py` | `reload_profiles()`: mostrar keepass_entry si auth_mode=keepass, sino vacío |
| `src/ovpn_launcher/app.py` | ResizeToContents para la nueva columna |

## Comportamiento

- auth_mode=keepass con keepass_entry → muestra el valor
- auth_mode=keepass sin keepass_entry → muestra "(alias)"
- auth_mode!=keepass → celda vacía
