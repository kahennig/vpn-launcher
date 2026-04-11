# Decisions — T023: Menú hamburguesa

## D1: Eliminar menú bar completamente

**Alternativas:** Mantener menú bar + agregar hamburguesa, reemplazar menú bar por hamburguesa
**Decisión:** Reemplazar
**Justificación:** Tener ambos es redundante. Las apps KDE modernas que usan hamburguesa no tienen menú bar.

## D2: Ícono application-menu

**Alternativas:** `application-menu`, `open-menu-symbolic`, texto "☰"
**Decisión:** `application-menu` con fallback a `open-menu-symbolic`
**Justificación:** Es el ícono estándar freedesktop para menú hamburguesa, usado por Dolphin y Kate.
