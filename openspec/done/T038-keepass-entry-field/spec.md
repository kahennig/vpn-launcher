# Spec — T038: Campo KeePass entry independiente del alias

## Objetivo

Permitir especificar un nombre de entrada KeePass diferente al alias del perfil.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/profiles.py` | 5to campo opcional `keepass_entry` en connections.conf, default vacío (usa alias) |
| `src/ovpn_launcher/app.py` | ProfileDialog: campo "KeePass Entry" (QLineEdit), visible solo si auth_mode=keepass |
| `src/ovpn_launcher/app.py` | `_get_keepass_creds()`: usar `keepass_entry` si existe, sino alias |
| `scripts/ovpn-connect` | Parsear 5to campo, usar para lookup en KeePass |
| `config/connections.conf.example` | Documentar 5to campo |

## Formato

```
alias|version|config|auth_mode|keepass_entry
```

- `keepass_entry` es opcional. Si vacío o ausente, se usa el alias como antes.
- Solo tiene sentido con auth_mode=keepass, pero se almacena siempre si se provee.
