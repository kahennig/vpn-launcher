# Spec — T007: Tests (pytest + pytest-qt)

## Objetivo

Agregar suite de tests para profiles.py como base para iterar con confianza.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `tests/test_profiles.py` | 14 tests: load (8), save (4), detect_versions (2) |
| `pyproject.toml` | `[project.optional-dependencies]` dev = pytest, pytest-qt |

## Cobertura

- `load_profiles`: archivo vacío, faltante, 3 campos, 4 campos, auth_mode inválido, comentarios, campos insuficientes, múltiples perfiles
- `save_profiles`: save+reload roundtrip, omisión de auth_mode none, preservación de header, creación de directorios
- `detect_versions`: retorna lista, incluye system si existe
