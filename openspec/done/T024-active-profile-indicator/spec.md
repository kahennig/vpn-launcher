# Spec — T024: Indicador de perfil activo en el tree

## Objetivo

Resaltar visualmente en el QTreeWidget qué perfil está conectado o conectando.

## Alcance

**Incluye:** cambiar ícono y font del item conectado, restaurar al desconectar.
**No incluye:** colores custom, animaciones.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `_update_state()`: al conectar/connecting, poner bold + ícono `network-vpn-acquiring`/`network-vpn` en el item; al desconectar, restaurar ícono y font normal |

## Comportamiento

- CONNECTING: item del perfil con ícono `network-vpn-acquiring` y texto bold
- CONNECTED: item con ícono `network-vpn` y texto bold
- DISCONNECTED: todos los items con ícono `network-vpn` y font normal
