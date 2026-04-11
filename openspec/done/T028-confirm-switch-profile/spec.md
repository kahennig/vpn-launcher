# Spec — T028: Confirmación antes de cambiar perfil conectado

## Objetivo

Si hay una conexión activa y el usuario intenta conectar otro perfil, preguntar antes de desconectar.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | `on_connect()`: si state != DISCONNECTED, preguntar "Disconnect from X and connect to Y?" |

## Comportamiento

- Si está conectado/conectando y hace doble-click o Connect en otro perfil → QMessageBox.question
- Yes → desconecta y conecta al nuevo
- No → no hace nada
- Si el perfil seleccionado es el mismo que el conectado → no hace nada (ya está conectado)
