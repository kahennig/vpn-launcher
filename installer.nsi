; NSIS installer for ovpn-launcher
; Requires: dist/ovpn-launcher.exe from PyInstaller

!include "MUI2.nsh"

Name "VPN Launcher"
OutFile "dist\ovpn-launcher-setup.exe"
InstallDir "$LOCALAPPDATA\ovpn-launcher"
RequestExecutionLevel admin

; UI
!define MUI_ICON "share\icons\ovpn-launcher.ico"
!define MUI_UNICON "share\icons\ovpn-launcher.ico"
!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\ovpn-launcher.exe"
    File "share\icons\ovpn-launcher.ico"

    ; Start menu shortcut
    CreateDirectory "$SMPROGRAMS\VPN Launcher"
    CreateShortcut "$SMPROGRAMS\VPN Launcher\VPN Launcher.lnk" "$INSTDIR\ovpn-launcher.exe" "" "$INSTDIR\ovpn-launcher.ico"
    CreateShortcut "$SMPROGRAMS\VPN Launcher\Uninstall.lnk" "$INSTDIR\uninstall.exe"

    ; Desktop shortcut
    CreateShortcut "$DESKTOP\VPN Launcher.lnk" "$INSTDIR\ovpn-launcher.exe" "" "$INSTDIR\ovpn-launcher.ico"

    ; Uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Add/Remove Programs entry
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "DisplayName" "VPN Launcher"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "DisplayIcon" "$INSTDIR\ovpn-launcher.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "Publisher" "Andreas Hennig"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher" "NoRepair" 1
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\ovpn-launcher.exe"
    Delete "$INSTDIR\ovpn-launcher.ico"
    Delete "$INSTDIR\uninstall.exe"
    RMDir "$INSTDIR"

    Delete "$SMPROGRAMS\VPN Launcher\VPN Launcher.lnk"
    Delete "$SMPROGRAMS\VPN Launcher\Uninstall.lnk"
    RMDir "$SMPROGRAMS\VPN Launcher"
    Delete "$DESKTOP\VPN Launcher.lnk"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ovpn-launcher"
SectionEnd
