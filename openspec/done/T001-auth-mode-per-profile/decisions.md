# Decisions — T001: Auth mode per profile

## D1: Default auth_mode = `none`

**Alternativas:** `none`, `keepass` (mantener comportamiento actual)
**Decisión:** `none`
**Justificación:** Es más explícito. Los perfiles que necesitan KeePass deben declararlo. Evita prompts inesperados de master password.

## D2: Modo `prompt` con QInputDialog secuenciales

**Alternativas:** QDialog custom con ambos campos, dos QInputDialog secuenciales
**Decisión:** Dos QInputDialog secuenciales (username normal, password con echo mode)
**Justificación:** Mínimo código, consistente con el QInputDialog ya usado para master password de KeePass.

## D3: Valores inválidos → `none` con warning

**Alternativas:** Error y no cargar perfil, silenciosamente tratar como `none`, warning + `none`
**Decisión:** Warning en log + tratar como `none`
**Justificación:** No romper la carga de perfiles por un typo. El warning informa al usuario.

## D4: Modo `prompt` en CLI con read

**Alternativas:** read interactivo, variable de entorno
**Decisión:** `read -p` para user, `read -sp` para pass
**Justificación:** Consistente con cómo el CLI ya pide el master password de KeePass.
