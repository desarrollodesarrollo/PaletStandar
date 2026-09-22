; Instalador de Calculadora de Sumas
; Genera un instalador de Windows con el aspecto/flujo clasico:
; Bienvenida -> Carpeta de destino -> Componentes -> Progreso -> Finalizar
;
; Requiere NSIS (https://nsis.sourceforge.io/) y el ejecutable Windows ya
; construido con PyInstaller (ver build_installer.bat, que hace ambos pasos).

!include "MUI2.nsh"

; --- Informacion general ---
Name "Calculadora de Sumas"
OutFile "CalculadoraSumasSetup.exe"
InstallDir "$PROGRAMFILES64\CalculadoraSumas"
InstallDirRegKey HKLM "Software\CalculadoraSumas" "InstallDir"
RequestExecutionLevel admin

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Calculadora de Sumas"
VIAddVersionKey "FileDescription" "Instalador de Calculadora de Sumas"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "LegalCopyright" "PaletStandar"

; --- Interfaz (Modern UI 2, el look estandar de los instaladores de Windows) ---
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!define MUI_WELCOMEPAGE_TITLE "Bienvenido al instalador de Calculadora de Sumas"
!define MUI_WELCOMEPAGE_TEXT "Este asistente instalara Calculadora de Sumas en tu equipo.$\r$\n$\r$\nHaz clic en Siguiente para continuar."

!define MUI_FINISHPAGE_RUN "$INSTDIR\CalculadoraSumas.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Ejecutar Calculadora de Sumas"
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Crear acceso directo en el escritorio"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateDesktopShortcutIfChecked

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "Spanish"

; --- Seccion principal: instala la aplicacion ---
Section "Calculadora de Sumas (requerido)" SecCore
  SectionIn RO
  SetOutPath "$INSTDIR"

  File "dist_windows\calculadora_gui.exe"
  Rename "$INSTDIR\calculadora_gui.exe" "$INSTDIR\CalculadoraSumas.exe"

  WriteRegStr HKLM "Software\CalculadoraSumas" "InstallDir" "$INSTDIR"

  ; Acceso directo en el Menu Inicio
  CreateDirectory "$SMPROGRAMS\Calculadora de Sumas"
  CreateShortCut "$SMPROGRAMS\Calculadora de Sumas\Calculadora de Sumas.lnk" "$INSTDIR\CalculadoraSumas.exe"
  CreateShortCut "$SMPROGRAMS\Calculadora de Sumas\Desinstalar.lnk" "$INSTDIR\Uninstall.exe"

  ; Desinstalador
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Entrada en "Agregar o quitar programas"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "DisplayName" "Calculadora de Sumas"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "InstallLocation" "$\"$INSTDIR$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "DisplayIcon" "$\"$INSTDIR\CalculadoraSumas.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "Publisher" "PaletStandar"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "DisplayVersion" "1.0.0"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas" \
    "NoRepair" 1
SectionEnd

; --- Seccion opcional: acceso directo en el escritorio ---
Section "Acceso directo en el escritorio" SecDesktop
  CreateShortCut "$DESKTOP\Calculadora de Sumas.lnk" "$INSTDIR\CalculadoraSumas.exe"
SectionEnd

Function CreateDesktopShortcutIfChecked
  CreateShortCut "$DESKTOP\Calculadora de Sumas.lnk" "$INSTDIR\CalculadoraSumas.exe"
FunctionEnd

; --- Desinstalador ---
Section "Uninstall"
  Delete "$INSTDIR\CalculadoraSumas.exe"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"

  Delete "$SMPROGRAMS\Calculadora de Sumas\Calculadora de Sumas.lnk"
  Delete "$SMPROGRAMS\Calculadora de Sumas\Desinstalar.lnk"
  RMDir "$SMPROGRAMS\Calculadora de Sumas"
  Delete "$DESKTOP\Calculadora de Sumas.lnk"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraSumas"
  DeleteRegKey HKLM "Software\CalculadoraSumas"
SectionEnd
