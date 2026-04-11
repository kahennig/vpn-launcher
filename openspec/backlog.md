# Backlog OpenSpec

> Actualizado: 2026-04-10

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

## Prioridad Alta — Migración de config (bloquea otras tareas)

La migración a YAML es prerequisito para la pantalla de configuración y simplifica
la extensibilidad futura. Conviene hacerla primero.

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T041 | Migrar config a YAML | ✅ DONE | Prerequisito para T042, T043 |
| T042 | Pantalla de configuración (Settings) | ✅ DONE | Requiere T041 |
| T043 | Migrar CLI a Python | ✅ DONE | Requiere T041 |

## Prioridad Alta — UX inmediata

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T044 | Columna KeePass entry en el tree | ✅ DONE | — |
| T045 | Atajos de teclado Add/Edit/Remove | ✅ DONE | — |
| T046 | Colores de estado en el log | ✅ DONE | — |
| T047 | Notificación con IP al conectar | ✅ DONE | — |

## Prioridad Media — Robustez

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T048 | Retry con backoff en auto-reconnect | ✅ DONE | — |
| T049 | Validar .ovpn antes de conectar | ✅ DONE | — |
| T050 | Backup de config.yaml antes de guardar | ✅ DONE | — |

## Prioridad Media — Funcionalidad

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T051 | Última conexión exitosa por perfil | ✅ DONE | — |
| T052 | Abrir carpeta de configs en Dolphin | ✅ DONE | — |
| T053 | Abrir carpeta de logs en Dolphin | ✅ DONE | — |
| T054 | Doble-click en log copia la línea | ✅ DONE | — |
| T055 | Contador de perfiles en status bar | ✅ DONE | — |

## Prioridad Media-Baja — CLI

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T056 | CLI --remove | ✅ DONE | — |
| T057 | CLI --edit | ✅ DONE | — |
| T058 | CLI --version | ✅ DONE | Implementado en T043 |

## Prioridad Baja — Visual e infra

| ID | Tarea | Estado | Justificación |
|----|-------|--------|---------------|
| T059 | Ícono custom de la app | ✅ DONE | SVG escudo con candado |
| T060 | Splash screen mínimo | ✅ DONE | QSplashScreen con ícono custom |
| T061 | Fix crash menú hamburguesa | ✅ DONE | Defer _rebuild_tray_menu con QTimer.singleShot |
| T016 | Packaging RPM/Flatpak | ⚪ BACKLOG | Distribución más fácil |

## Desestimados

| ID | Tarea | Estado | Motivo |
|----|-------|--------|--------|
| T011 | Múltiples conexiones simultáneas | ❌ DESESTIMADO | No es necesario tener más de una VPN activa a la vez |
| T014 | Timeout/cache de master password KeePass | ❌ DESESTIMADO | Riesgo de seguridad: master password en memoria expone todas las credenciales de KeePass |

Estados: ⚪ BACKLOG → 📋 PROPOSAL → 🔵 ACTIVE → ✅ DONE

## Notas de priorización

- **T041-T043** van primero porque la migración a YAML desbloquea settings y CLI en Python
- **T044-T047** son mejoras de UX rápidas que se pueden hacer en paralelo o antes de T041
- **T048-T050** mejoran robustez sin cambios grandes
- **T051-T055** funcionalidad nice-to-have
- **T056-T058** CLI depende de T043 (migración CLI a Python)
- **T059-T060** look propio de la app
- **T014, T016** siguen siendo complejos
- **T011** desestimado — no se necesita más de una VPN activa
