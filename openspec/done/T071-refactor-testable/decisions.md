# T071 — Decisiones

| # | Decisión | Motivo |
|---|----------|--------|
| 1 | Módulo de lógica pura se llama `services.py` | Nombre claro, consistente con el proyecto |
| 2 | Diálogos van a `dialogs.py` | Reduce tamaño de app.py aunque no mejora testeabilidad en CI |
| 3 | Implementación en 2 fases (F0: diálogos, F1: lógica pura) | Refactor seguro e incremental |
| 4 | `fetch_keepass_creds` separa la parte subprocess de la parte GUI | La invocación a keepassxc-cli es testeable; el QInputDialog queda en app.py |
