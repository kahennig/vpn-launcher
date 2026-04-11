# OpenSpec — Especificar antes de programar

## Flujo

| Fase | Prompt | Entrada | Salida |
|------|--------|---------|--------|
| 1. Descubrir | `@openspec-discover` | proposal.md + código | discovery.md |
| 2. Especificar | `@openspec-specify` | discovery.md + respuestas | spec.md, decisions.md, checklist.md |
| 3. Validar | `@openspec-validate` | spec.md | spec aprobada o ambigüedades |
| 4. Implementar | (desarrollo normal) | spec.md | código + docs-draft/ |
| 5. Publicar | `@openspec-publish` | docs-draft/ + checklist.md | docs/ publicados |

## Convenciones

- Cada tarea vive en `openspec/active/{ID}-{Nombre}/`
- La documentación se escribe en `docs-draft/` DURANTE la implementación
- Al completar, `@openspec-publish` mueve docs al destino final y la spec a `openspec/done/`
- `backlog.md` es el índice maestro con estado de cada tarea
