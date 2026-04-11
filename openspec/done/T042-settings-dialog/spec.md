# Spec — T042: Pantalla de configuración (Settings)

## Objetivo

Diálogo de Settings accesible desde el menú hamburguesa para editar config.yaml visualmente.

## Cambios

| Archivo | Cambio |
|---------|--------|
| `src/ovpn_launcher/app.py` | Clase `SettingsDialog(QDialog)` con formulario |
| `src/ovpn_launcher/app.py` | Acción "Settings" en hamburger menu |
| `src/ovpn_launcher/app.py` | Al aceptar: guardar settings, recargar en la app |

## Campos del formulario

| Campo | Widget | Default |
|-------|--------|---------|
| OpenVPN Prefix | QLineEdit + Browse | /opt |
| KeePass DB | QLineEdit + Browse | ~/Document/Keepass/keepass.kdbx |
| Connection Timeout (s) | QSpinBox (1-300) | 30 |
| Reconnect Delay (s) | QSpinBox (1-120) | 5 |
| IP Service URL | QLineEdit | https://api.ipify.org |
| Log Level | QComboBox (DEBUG/INFO/WARNING/ERROR) | WARNING |

## Comportamiento

- Abre pre-llenado con settings actuales
- OK → guarda a config.yaml, recarga `_app_settings` en la app
- Cancel → no cambia nada
- Browse para prefix abre QFileDialog directorio
- Browse para keepass_db abre QFileDialog archivo .kdbx
