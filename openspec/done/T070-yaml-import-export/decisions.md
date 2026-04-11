# T070 — Decisiones

| # | Decisión | Motivo |
|---|----------|--------|
| 1 | Sin retrocompatibilidad con formato pipe-delimited en import | Único usuario, no hay zips legacy que migrar |
| 2 | Archivo en el zip se llama `profile.yaml` | Consistencia con el formato YAML de la app |
| 3 | No se modifica `CONNECTIONS_CONF` en paths.py | Sigue siendo necesaria para migración legacy en profiles.py |
