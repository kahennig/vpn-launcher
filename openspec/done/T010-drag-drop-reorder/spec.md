# Spec — T010: Reordenar perfiles (drag & drop)

## Objetivo

Permitir reordenar perfiles arrastrando en el tree, guardando el orden automáticamente.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `setDragDropMode(InternalMove)`, `setDefaultDropAction(MoveAction)`, `rowsMoved` → `_on_profiles_reordered()` |

## Comportamiento

- Drag & drop dentro del QTreeWidget para mover perfiles
- Al soltar, `_on_profiles_reordered()` reconstruye la lista de perfiles desde el tree y llama `save_profiles()`
