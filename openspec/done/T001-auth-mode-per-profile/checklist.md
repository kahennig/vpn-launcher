# Checklist — T001: Auth mode per profile

## F0 — Parseo

- [x] Perfil con 3 campos carga con `auth_mode = "none"`
- [x] Perfil con 4to campo `keepass` carga con `auth_mode = "keepass"`
- [x] Perfil con 4to campo `prompt` carga con `auth_mode = "prompt"`
- [x] Perfil con 4to campo inválido carga con `auth_mode = "none"`

## F1 — GUI

- [x] `auth_mode = none` → conecta sin pedir credenciales
- [x] `auth_mode = keepass` → pide master password y busca en KeePass
- [x] `auth_mode = keepass` sin KEEPASS_DB → log warning, conecta sin credenciales
- [x] `auth_mode = prompt` → muestra diálogos de user y pass
- [x] `auth_mode = prompt` y usuario cancela → no conecta
- [x] Columna "Auth" visible en el QTreeWidget

## F2 — CLI

- [x] `auth_mode = none` → conecta directo
- [x] `auth_mode = keepass` → pide master password, busca en KeePass
- [x] `auth_mode = prompt` → pide user y pass por terminal
- [x] Perfiles de 3 campos en CLI funcionan como `none`

## F3 — Docs

- [x] `connections.conf.example` muestra formato con 4 campos y ejemplos de los 3 modos
- [x] `README.md` documenta el campo auth_mode
