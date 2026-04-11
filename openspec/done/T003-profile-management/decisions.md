# Decisions — T003: Gestión de perfiles desde la GUI

## D1: Preservar comentarios del header al guardar

**Alternativas:** Reescribir todo sin comentarios, preservar header, preservar todos los comentarios inline
**Decisión:** Preservar líneas de comentario del inicio del archivo (header)
**Justificación:** El header tiene documentación del formato. Comentarios inline entre perfiles son raros y complicarían la lógica.

## D2: Omitir auth_mode si es "none" al guardar

**Alternativas:** Siempre escribir 4 campos, omitir si none
**Decisión:** Omitir auth_mode si es "none"
**Justificación:** Mantiene compatibilidad visual con el formato original de 3 campos. Menos ruido.

## D3: Combo de versiones editable

**Alternativas:** Combo fijo (solo detectadas), combo editable, QLineEdit libre
**Decisión:** QComboBox editable con versiones detectadas
**Justificación:** Autodetección para conveniencia, editable para versiones nuevas sin reiniciar.

## D4: Warning (no error) si config file no existe

**Alternativas:** Bloquear guardado, warning y permitir, ignorar
**Decisión:** Warning y permitir guardar
**Justificación:** El usuario puede estar preparando el perfil antes de copiar el archivo .ovpn.
