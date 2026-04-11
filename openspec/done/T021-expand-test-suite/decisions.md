# Decisions — T021: Expandir batería de tests

## D1: No testear VPNLauncher completo

**Alternativas:** Testear toda la GUI, testear solo ProfileDialog, no testear GUI
**Decisión:** Solo ProfileDialog
**Justificación:** VPNLauncher requiere mocking de QProcess, pkexec, subprocess, tray — demasiado complejo para el valor que aporta ahora. ProfileDialog es autocontenido y testeable.

## D2: Usar qtbot de pytest-qt para ProfileDialog

**Alternativas:** Instanciar sin qtbot, usar qtbot
**Decisión:** Usar qtbot
**Justificación:** Maneja el event loop y cleanup automáticamente.
