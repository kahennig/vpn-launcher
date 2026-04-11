# Decisions — T041: Migrar config a YAML

## D1: YAML sobre TOML

**Alternativas:** YAML, TOML (built-in 3.11+), JSON, INI
**Decisión:** YAML
**Justificación:** Más legible para listas de perfiles. TOML es bueno para settings pero incómodo para arrays de objetos. JSON no permite comentarios. El usuario prefiere YAML.

## D2: Un solo archivo config.yaml

**Alternativas:** Separar settings.yaml y profiles.yaml, un solo config.yaml
**Decisión:** Un solo archivo con secciones `settings:` y `profiles:`
**Justificación:** Más simple, un solo lugar para todo. Las secciones lo mantienen organizado.

## D3: No borrar connections.conf al migrar

**Alternativas:** Borrar, renombrar a .bak, mantener
**Decisión:** Mantener como backup
**Justificación:** El usuario puede querer volver atrás. El CLI bash todavía lo necesita hasta T043.

## D4: Settings con defaults

**Alternativas:** Requerir todos los campos, defaults para todo
**Decisión:** Defaults para todo — settings es opcional
**Justificación:** config.yaml puede tener solo `profiles:` y funcionar. Los defaults se aplican en código.
