# Decisions — T002: Diálogo About estilo KDE

## D1: QDialog custom en vez de KAboutDialog

**Alternativas:** KAboutDialog (PyKDE6), QMessageBox.about(), QDialog custom
**Decisión:** QDialog custom
**Justificación:** PyKDE6 no está disponible en Fedora ni PyPI. QMessageBox.about() es demasiado simple. QDialog custom permite imitar el estilo KDE.

## D2: Tabs para organizar contenido

**Alternativas:** Todo en un solo scroll, tabs, secciones colapsables
**Decisión:** QTabWidget con About/Author/License
**Justificación:** Es el patrón que usan los KAboutDialog nativos de KDE.

## D3: Versión desde __version__

**Alternativas:** Leer de pyproject.toml, hardcodear, usar __version__
**Decisión:** Importar __version__ desde __init__.py
**Justificación:** Ya existe como fuente de verdad, es el patrón estándar de Python.
