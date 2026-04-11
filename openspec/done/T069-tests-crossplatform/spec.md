# T069 — Tests cross-platform

> Spec — 2026-04-11

## Cambios

- Fix hardcoded `/usr/bin/openvpn` en test_profiles.py → usa `openvpn_binary("system")`
- CI matrix: ubuntu-latest + windows-latest
- Todos los tests de CI son cross-platform (no dependen de paths Linux)
