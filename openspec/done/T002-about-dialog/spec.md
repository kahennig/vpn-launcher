# Spec — T002: Diálogo About estilo KDE

## Objetivo

Agregar diálogo About con info de la app (versión, licencia, autor) accesible desde menú Help, imitando el estilo KDE.

## Alcance

**Incluye:** menu bar con Help → About, QDialog custom con ícono, nombre, versión, descripción, tabs (About, Author, License).
**No incluye:** otros menús, KAboutDialog nativo, otros diálogos.

## Fases

### F0 — Menu bar y acción About

**Objetivo:** Agregar menu bar con Help → About.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Nuevo método `_setup_menubar()` con menú Help → About |
| `src/ovpn_launcher/app.py` | Llamar `_setup_menubar()` en `__init__` |

### F1 — QDialog About

**Objetivo:** Diálogo con estilo KDE About.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Método `_show_about()` que crea y muestra el QDialog |

**Layout del diálogo:**
- Header: ícono grande (64px) + nombre app + versión (bold, grande)
- Descripción corta debajo del header
- QTabWidget con 3 tabs:
  - **About**: descripción más detallada del proyecto
  - **Author**: nombre del autor
  - **License**: texto GPL-3.0 (en QTextEdit read-only, monospace)
- Link al repo (clickeable)
- Botón Close

**Datos:**
- Versión: importar `__version__` desde `__init__.py`
- Licencia: texto corto de GPL-3.0-or-later
- Autor: "Andi"
- Repo: URL del pyproject.toml

## Casos borde

- Si el ícono del tema no existe, usar ícono genérico de Qt
