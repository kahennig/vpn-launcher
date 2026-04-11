# Spec — T003: Gestión de perfiles desde la GUI

## Objetivo

Permitir agregar, editar y eliminar perfiles VPN desde la GUI sin editar el archivo manualmente.

## Alcance

**Incluye:** diálogo de perfil (Add/Edit), Remove con confirmación, detección de versiones, guardar a connections.conf preservando comentarios.
**No incluye:** drag & drop, import/export, edición inline.

## Fases

### F0 — Detección de versiones y escritura de perfiles

**Objetivo:** Funciones de soporte en profiles.py.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/profiles.py` | `detect_versions()`: escanea `/opt/openvpn-*/sbin/openvpn` + system, retorna lista de strings |
| `src/ovpn_launcher/profiles.py` | `save_profiles(profiles, conf_path)`: escribe connections.conf preservando header de comentarios |

**Comportamiento de save_profiles:**
- Lee el archivo existente y extrae las líneas de comentario del inicio (header)
- Reescribe: header de comentarios + líneas de perfiles
- Formato: `alias|version|config|auth_mode` (omitir auth_mode si es `none` para mantener limpieza)

### F1 — Diálogo de perfil (ProfileDialog)

**Objetivo:** QDialog reutilizable para Add y Edit.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Clase `ProfileDialog(QDialog)` con formulario |

**Campos del formulario:**
- Alias: QLineEdit
- Version: QComboBox editable (poblado con detect_versions())
- Config file: QLineEdit + botón Browse (QFileDialog, filtro *.ovpn *.conf)
- Auth mode: QComboBox (none, keepass, prompt)

**Validación al aceptar:**
- Alias no vacío
- Alias único (en modo Add, o diferente al original en Edit)
- Config file no vacío y archivo existe (warning si no, pero permite guardar)
- Versión no vacía

**Método `get_profile()`** retorna dict con alias, version, config, auth_mode.

### F2 — Acciones Add/Edit/Remove en la GUI

**Objetivo:** Integrar las acciones en toolbar y conectar con el diálogo y save.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Acciones: Add (list-add), Edit (document-edit), Remove (list-remove) |
| `src/ovpn_launcher/app.py` | Métodos: `on_add_profile()`, `on_edit_profile()`, `on_remove_profile()` |
| `src/ovpn_launcher/app.py` | Toolbar: Add, Edit, Remove después de Reload |

**Comportamiento:**
- **Add**: abre ProfileDialog vacío → si acepta, agrega a self.profiles, guarda, recarga tree
- **Edit**: abre ProfileDialog con datos del perfil seleccionado → si acepta, actualiza, guarda, recarga tree
- **Remove**: QMessageBox.question confirmación → si acepta, elimina, guarda, recarga tree
- Edit y Remove deshabilitados si no hay perfil seleccionado
- Los 3 deshabilitados durante conexión activa

## Casos borde

- connections.conf no existe → save_profiles lo crea
- No hay versiones instaladas → combo vacío pero editable (el usuario puede tipear)
- Perfil seleccionado se elimina → seleccionar el primero o ninguno
- Edit sin perfil seleccionado → botón deshabilitado
