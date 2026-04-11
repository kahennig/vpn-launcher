# Checklist — T003: Gestión de perfiles desde la GUI

## F0 — Detección y escritura

- [x] `detect_versions()` retorna versiones de /opt + system
- [x] `save_profiles()` escribe connections.conf con formato correcto
- [x] `save_profiles()` preserva header de comentarios
- [x] auth_mode "none" se omite al guardar (3 campos)
- [x] auth_mode "keepass"/"prompt" se escribe como 4to campo

## F1 — ProfileDialog

- [x] Campos: alias, version (combo editable), config (con browse), auth_mode (combo)
- [x] Browse abre QFileDialog con filtro .ovpn/.conf
- [x] Validación: alias no vacío
- [x] Validación: alias único en modo Add
- [x] Validación: config file warning si no existe
- [x] get_profile() retorna dict correcto

## F2 — Acciones Add/Edit/Remove

- [x] Botón Add en toolbar abre ProfileDialog vacío
- [x] Botón Edit en toolbar abre ProfileDialog con datos del perfil seleccionado
- [x] Botón Remove pide confirmación y elimina
- [x] Guardar actualiza connections.conf y recarga tree
- [x] Edit/Remove deshabilitados sin selección (retorna si no hay item)
- [x] Add/Edit/Remove deshabilitados durante conexión
