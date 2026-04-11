# W006 — Iconos bundled (sin freedesktop theme)

> Spec — 2026-04-11

## Contexto

app.py usa ~25 llamadas a `QIcon.fromTheme()` con nombres freedesktop. En Windows no hay tema de iconos freedesktop, así que todas devuelven iconos vacíos — la app funciona pero sin iconos.

## Enfoque

Crear una función helper `themed_icon(name, fallback_sp=None)` que:
1. Intenta `QIcon.fromTheme(name)` — funciona en Linux con KDE/GNOME
2. Si el icono está vacío y hay fallback, usa `QApplication.style().standardIcon(fallback_sp)` — funciona en todas las plataformas
3. Si no hay fallback, devuelve un QIcon vacío (igual que ahora)

Esto es no-invasivo: en Linux sigue usando el tema freedesktop, en Windows usa los iconos estándar de Qt.

## Mapeo de iconos

| freedesktop name | QStyle.StandardPixmap fallback |
|-----------------|-------------------------------|
| network-connect | SP_MediaPlay |
| network-disconnect | SP_MediaStop |
| view-refresh | SP_BrowserReload |
| edit-clear-history | SP_DialogResetButton |
| edit-copy | SP_FileIcon |
| list-add | SP_FileDialogNewFolder |
| document-import | SP_DialogOpenButton |
| package-x-generic | SP_DialogOpenButton |
| document-edit | SP_FileDialogDetailedView |
| list-remove | SP_DialogCancelButton |
| document-export | SP_DialogSaveButton |
| network-wired | SP_DriveNetIcon |
| network-server | SP_DriveNetIcon |
| run-build | SP_CommandLink |
| folder-open | SP_DirOpenIcon |
| help-about | SP_MessageBoxInformation |
| configure | SP_FileDialogDetailedView |
| application-exit | SP_DialogCloseButton |
| application-menu | SP_ToolBarHorizontalExtensionButton |
| window | SP_TitleBarNormalButton |
| dialog-warning | SP_MessageBoxWarning |
| network-vpn-acquiring | SP_BrowserReload |

## Cambios

### `src/ovpn_launcher/app.py`

1. Agregar función `_themed_icon(name, fallback_sp=None)` al inicio del módulo
2. Reemplazar `QIcon.fromTheme("name")` por `_themed_icon("name", QStyle.StandardPixmap.SP_xxx)`

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Helper + reemplazar ~25 llamadas |

## Criterios de aceptación

- [ ] En Linux: iconos se ven igual que antes (freedesktop theme)
- [ ] En Windows: iconos de fallback visibles (no vacíos)
- [ ] Tests pasan
- [ ] App funciona en Linux
