# T071 — Checklist

## F0 — Diálogos
- [x] `dialogs.py` creado con BuildDialog, SettingsDialog, ProfileDialog
- [x] app.py importa diálogos desde dialogs.py
- [x] tests/test_app.py imports actualizados
- [x] 58 tests pasan
- [x] App funciona (validación manual)

## F1 — Lógica pura
- [x] `services.py` creado con funciones puras
- [x] `log_color()` extraída y testeada
- [x] `validate_ovpn()` extraída y testeada
- [x] `extract_remote_host()` extraída y testeada
- [x] `export_profile_zip()` extraída y testeada
- [x] `import_profile_zip()` extraída y testeada
- [x] `fetch_keepass_creds()` extraída y testeada
- [x] app.py delega a services.py
- [x] CI incluye test_services.py
- [x] 86 tests pasan (58 + 28 nuevos)
- [x] App funciona (validación manual)
