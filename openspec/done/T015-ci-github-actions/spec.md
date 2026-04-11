# Spec — T015: CI básico (GitHub Actions)

## Objetivo

Automatizar tests en cada push/PR.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `.github/workflows/ci.yml` | Workflow: checkout, setup-python 3.12, install deps (libegl1, PyQt6, pytest, pytest-qt), install package, run pytest con xvfb |

## Notas

- Usa `coactions/setup-xvfb` para display virtual (PyQt6 necesita display)
- `libegl1` necesario para Qt en headless Ubuntu
