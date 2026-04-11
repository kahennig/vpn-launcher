# T064 — Decisiones

| # | Decisión | Motivo |
|---|----------|--------|
| 1 | No crear platform.py separado, modificar paths.py | paths.py ya es el lugar centralizado, crear otro módulo sería over-engineering |
| 2 | AUTOSTART_DIR/AUTOSTART_DESKTOP = None en Windows | T068 manejará autostart en Windows (Registry/Startup folder) |
| 3 | Usar sys.platform == "win32" | Forma estándar de detectar Windows en Python |
| 4 | IS_WINDOWS exportado como constante | Otros módulos pueden necesitarlo (T065, T066, etc.) |
