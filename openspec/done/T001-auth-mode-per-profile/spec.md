# Spec — T001: Auth mode per profile

## Objetivo

Permitir configurar por perfil el modo de autenticación: sin credenciales, KeePass, o prompt manual.

## Alcance

**Incluye:** parseo del 4to campo, lógica condicional en GUI y CLI, diálogo prompt, columna en tree, docs.
**No incluye:** nuevos modos de auth, edición de perfiles desde GUI, migración automática.

## Formato de configuración

```
alias|version|config_path|auth_mode
```

- `auth_mode` es opcional. Valores: `none` (default), `keepass`, `prompt`
- Valores no reconocidos se tratan como `none` (con warning en log)

## Fases

### F0 — Parseo y modelo de datos

**Objetivo:** Que el perfil cargue auth_mode sin romper nada.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/profiles.py` | Aceptar 3 o 4 campos; agregar `auth_mode` al dict (default `none`) |

**Criterios:** Perfiles de 3 campos siguen funcionando. Perfiles de 4 campos cargan auth_mode correctamente. Valores inválidos → `none`.

### F1 — Lógica de auth en GUI

**Objetivo:** Que `on_connect` use auth_mode para decidir cómo obtener credenciales.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `on_connect`: condicionar auth según `auth_mode` del perfil |
| `src/ovpn_launcher/app.py` | Nuevo método `_get_prompt_creds(alias)`: QInputDialog para user, QInputDialog (password) para pass |
| `src/ovpn_launcher/app.py` | Agregar columna "Auth" al QTreeWidget |

**Comportamiento:**

- `none` → no pide credenciales, conecta directo
- `keepass` → llama `_get_keepass_creds(alias)` (comportamiento actual)
- `prompt` → muestra dos QInputDialog secuenciales (username, luego password con echo mode)

**Casos borde:**
- `keepass` pero KEEPASS_DB no existe → log warning, conectar sin credenciales
- `prompt` y usuario cancela cualquier diálogo → abortar conexión
- `keepass` y usuario cancela master password → abortar conexión (comportamiento actual)

### F2 — Lógica de auth en CLI

**Objetivo:** Que `ovpn-connect` use auth_mode.

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `scripts/ovpn-connect` | Parsear campo 4 con `cut -d'|' -f4`, default `none` |
| `scripts/ovpn-connect` | Condicionar bloque KeePass a `auth_mode=keepass` |
| `scripts/ovpn-connect` | Nuevo bloque para `auth_mode=prompt`: `read -p` user, `read -sp` pass |

**Comportamiento:**
- `none` → conecta directo sin credenciales
- `keepass` → comportamiento actual (pide master password, busca en KeePass)
- `prompt` → pide user y pass por terminal

### F3 — Config ejemplo y documentación

**Cambios:**

| Archivo | Cambio |
|---------|--------|
| `config/connections.conf.example` | Actualizar formato y agregar ejemplos con los 3 modos |
| `README.md` | Documentar el campo auth_mode en sección Configuration |
