# Checklist — T021: Expandir batería de tests

## F0 — paths.py

- [x] openvpn_binary("system") → /usr/bin/openvpn
- [x] openvpn_binary("2.6.14") → /opt/openvpn-2.6.14/sbin/openvpn
- [x] CONFIG_DIR termina en ovpn-launcher
- [x] CONNECTIONS_CONF dentro de CONFIG_DIR

## F1 — Edge cases profiles.py

- [x] save_profiles con lista vacía
- [x] save_profiles a archivo nuevo (sin header)
- [x] load_profiles con whitespace en auth_mode
- [x] Roundtrip preserva orden
- [x] load_profiles con auth_mode prompt

## F2 — ProfileDialog

- [x] Modo add: campos vacíos
- [x] Modo edit: campos pre-llenados
- [x] get_profile() retorna dict correcto
- [x] Validación: alias vacío rechazado
- [x] Validación: alias duplicado rechazado
- [x] Validación: config vacío rechazado
