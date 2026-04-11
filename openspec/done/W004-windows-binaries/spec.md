# W004 — Descarga de binarios pre-compilados para Windows

> Spec — 2026-04-11

## Contexto

En Linux, `builder.py` descarga el source, compila con configure/make e instala. En Windows no compilamos — descargamos el MSI oficial de OpenVPN y extraemos el binario.

## URLs de descarga

- MSI: `https://swupdate.openvpn.net/community/releases/OpenVPN-{version}-I001-amd64.msi`
- Versiones disponibles: mismas que GitHub tags (ya implementado en `fetch_available_versions`)

## Flujo en Windows

### Primera instalación (sin driver TAP/TUN)

Detectar si hay driver TAP instalado (`C:\Program Files\TAP-Windows\` o `C:\Windows\System32\drivers\tap0901.sys` o adaptador `wintun.dll`).

Si no hay driver → instalar MSI completo con `msiexec /i` (instala drivers + binario como "system"). Requiere UAC.

### Versiones adicionales

Extraer solo el binario con `msiexec /a` (administrative install, sin drivers):
```
msiexec /a OpenVPN-{version}.msi /qn TARGETDIR={prefix}\openvpn-{version}
```

Esto extrae los archivos sin registrar el producto. El binario queda en `{prefix}\openvpn-{version}\bin\openvpn.exe`.

## Cambios

### `src/ovpn_launcher/builder.py`

Agregar función `install_openvpn_windows(version, prefix, on_output, full_install=False)`:
- Descarga MSI a temp
- Si `full_install`: `msiexec /i` (con drivers, UAC)
- Si no: `msiexec /a` (solo extrae binario)

Modificar `build_openvpn` para bifurcar según plataforma.

Agregar `has_tap_driver()` para detectar si hay driver instalado.

### `src/ovpn_launcher/dialogs.py` — BuildDialog

En Windows, si no hay driver TAP, mostrar checkbox "Full install (includes TAP driver)" marcado por defecto.

## Archivos impactados

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/builder.py` | `install_openvpn_windows`, `has_tap_driver`, bifurcación en `build_openvpn` |
| `src/ovpn_launcher/dialogs.py` | Checkbox de full install en Windows |

## Criterios de aceptación

- [ ] En Linux: build_openvpn funciona igual que antes
- [ ] En Windows: descarga MSI y extrae binario a `{prefix}\openvpn-{version}\`
- [ ] En Windows sin driver: ofrece instalación completa
- [ ] Tests pasan en ambas plataformas
- [ ] App funciona en Linux
