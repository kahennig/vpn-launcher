# Backlog OpenSpec

> Actualizado: 2026-04-11

## Completadas

| ID | Tarea | Estado |
|----|-------|--------|
| T001 | Auth mode per profile | ✅ DONE |
| T002 | About dialog estilo KDE | ✅ DONE |
| T003 | Gestión de perfiles (Add/Edit/Remove) | ✅ DONE |
| T004 | Timeout de conexión | ✅ DONE |
| T005 | Notificaciones de estado en tray | ✅ DONE |
| T006 | Import de .ovpn | ✅ DONE |
| T007 | Tests (pytest + pytest-qt) | ✅ DONE |
| T008 | Auto-reconnect | ✅ DONE |
| T009 | Filtro rápido de perfiles | ✅ DONE |
| T010 | Reordenar perfiles (drag & drop) | ✅ DONE |
| T012 | CLI --add y --status | ✅ DONE |
| T013 | Limpiar credenciales de memoria | ✅ DONE |
| T015 | CI básico (GitHub Actions) | ✅ DONE |
| T017 | Gap analysis + actualización de docs | ✅ DONE |
| T018 | Tema oscuro/claro (palette-aware) | ✅ DONE |
| T019 | Toolbar UX (iconos solos + reagrupar) | ✅ DONE |
| T020 | Distinguir Quit vs Close (X) | ✅ DONE |
| T021 | Expandir batería de tests | ✅ DONE |
| T022 | Fix crash al hacer clic en tray icon | ✅ DONE |
| T023 | Menú hamburguesa estilo KDE | ✅ DONE |
| T024 | Indicador de perfil activo en el tree | ✅ DONE |
| T025 | Contador de tiempo conectado | ✅ DONE |
| T026 | Copiar log al clipboard | ✅ DONE |
| T027 | Config validation on load | ✅ DONE |
| T028 | Confirmación antes de cambiar perfil | ✅ DONE |
| T029 | Log persistente a archivo | ✅ DONE |
| T030 | Búsqueda en el log (Ctrl+F) | ✅ DONE |
| T031 | Export de perfiles | ✅ DONE |
| T032 | Autostart al login | ✅ DONE |
| T033 | IP pública en status bar | ✅ DONE |
| T034 | Ping/latency check pre-conexión | ✅ DONE |
| T035 | DNS leak check post-conexión | ✅ DONE |
| T036 | Logging con Python logging module | ✅ DONE |
| T037 | Import de perfil exportado (.zip) | ✅ DONE |
| T038 | Campo KeePass entry independiente | ✅ DONE |
| T039 | Renombrar y reagrupar acciones toolbar/hamburger | ✅ DONE |
| T040 | Marcar conexión activa en menú del tray | ✅ DONE |
| T041 | Migrar config a YAML | ✅ DONE |
| T042 | Pantalla de configuración (Settings) | ✅ DONE |
| T043 | Migrar CLI a Python | ✅ DONE |
| T044 | Columna KeePass entry en el tree | ✅ DONE |
| T045 | Atajos de teclado Add/Edit/Remove | ✅ DONE |
| T046 | Colores de estado en el log | ✅ DONE |
| T047 | Notificación con IP al conectar | ✅ DONE |
| T048 | Retry con backoff en auto-reconnect | ✅ DONE |
| T049 | Validar .ovpn antes de conectar | ✅ DONE |
| T050 | Backup de config.yaml antes de guardar | ✅ DONE |
| T051 | Última conexión exitosa por perfil | ✅ DONE |
| T052 | Abrir carpeta de configs en file manager | ✅ DONE |
| T053 | Abrir carpeta de logs en file manager | ✅ DONE |
| T054 | Doble-click en log copia la línea | ✅ DONE |
| T055 | Contador de perfiles en status bar | ✅ DONE |
| T056 | CLI --remove | ✅ DONE |
| T057 | CLI --edit | ✅ DONE |
| T058 | CLI --version | ✅ DONE |
| T059 | Ícono custom de la app | ✅ DONE |
| T060 | Splash screen mínimo | ✅ DONE |
| T061 | Fix crash menú hamburguesa | ✅ DONE |
| T062 | Expandir tests v2 | ✅ DONE |
| T063 | Build OpenVPN desde la GUI | ✅ DONE |
| T070 | Migrar import/export de perfiles a YAML + limpiar referencias legacy | ✅ DONE |

## Pendientes — Refactor y calidad

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T071 | Refactor app.py → lógica testeable sin GUI | ✅ DONE | app.py crece mucho; extraer lógica de negocio (import/export, conexión, etc.) a módulos puros testeables en CI sin pytest-qt ni display |

## Pendientes — Cross-platform (ambos SO)

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| L016 | Packaging RPM/Flatpak | ⚪ BACKLOG | Distribución más fácil en Linux |

## Pendientes — Windows Port

### Fase 1: Refactor cross-platform (preparación, sin romper Linux)

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T064 | Módulo platform.py — abstracción de rutas | ⚪ BACKLOG | Centralizar rutas XDG (Linux) vs %APPDATA% (Windows) |
| T065 | Abstracción de escalación de privilegios | ⚪ BACKLOG | pkexec (Linux) vs runas/UAC (Windows) |
| T066 | Abstracción de detección de binarios OpenVPN | ⚪ BACKLOG | /opt/ (Linux) vs Program Files (Windows) |
| T067 | Reemplazar curl/dig por Python stdlib | ⚪ BACKLOG | IP check y DNS check sin dependencias externas |
| T068 | Abstracción de autostart | ⚪ BACKLOG | .desktop (Linux) vs Registry/Startup folder (Windows) |
| T069 | Tests cross-platform | ⚪ BACKLOG | Asegurar que los tests no dependen de paths Linux |

### Fase 2: Soporte Windows

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| W001 | Rutas Windows (%APPDATA%, Program Files) | ⚪ BACKLOG | Config y binarios en ubicaciones Windows |
| W002 | Escalación de privilegios con UAC | ⚪ BACKLOG | Ejecutar OpenVPN como admin en Windows |
| W003 | Detección de instalaciones OpenVPN en Windows | ⚪ BACKLOG | Buscar en Program Files, registry, PATH |
| W004 | Descarga de binarios pre-compilados para Windows | ⚪ BACKLOG | En Windows no compilamos, descargamos instaladores oficiales |
| W005 | Autostart en Windows (Registry o Startup folder) | ⚪ BACKLOG | Arrancar al login en Windows |
| W006 | Iconos bundled (sin freedesktop theme) | ⚪ BACKLOG | Windows no tiene tema de iconos freedesktop |
| W007 | KeePassXC CLI en Windows | ⚪ BACKLOG | Detectar keepassxc-cli.exe en Program Files |
| W008 | CI para Windows (GitHub Actions) | ⚪ BACKLOG | Testear en Windows automáticamente |
| W009 | Instalador Windows (PyInstaller o NSIS) | ⚪ BACKLOG | Distribuir como .exe o .msi |
| W010 | Documentación Windows | ⚪ BACKLOG | Guía de instalación y uso en Windows |

## Desestimados

| ID | Tarea | Estado | Motivo |
|----|-------|--------|--------|
| T011 | Múltiples conexiones simultáneas | ❌ DESESTIMADO | No es necesario tener más de una VPN activa a la vez |
| T014 | Timeout/cache de master password KeePass | ❌ DESESTIMADO | Riesgo de seguridad: master password en memoria expone todas las credenciales de KeePass |

Estados: ⚪ BACKLOG → 📋 PROPOSAL → 🔵 ACTIVE → ✅ DONE

## Convención de IDs

- **Txxx** — Tareas cross-platform (ambos SO)
- **Lxxx** — Tareas Linux-only
- **Wxxx** — Tareas Windows-only

## Notas de priorización — Windows Port

- **Fase 1 (T064-T069)**: refactor del código actual para abstraer diferencias de plataforma. Se hace primero sin romper Linux. Cada tarea es independiente.
- **Fase 2 (W001-W010)**: implementación específica de Windows. Depende de Fase 1.
- **W004** es la diferencia más grande: en Windows no compilamos OpenVPN, descargamos binarios oficiales de https://openvpn.net/community-downloads/
- **W002** (UAC) es lo más complejo técnicamente
- **W009** (instalador) es lo último — primero que funcione, después empaquetar
