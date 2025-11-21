; Inno Setup Script para Procesador de Facturas REGGIS
; Genera un instalador profesional para Windows
;
; USO:
;   1. Compilar ejecutable: pyinstaller build/build_windows.spec
;   2. Abrir este archivo en Inno Setup Compiler
;   3. Compilar (Build → Compile)
;
; RESULTADO:
;   installer_output/BogotaSAE_v2.0.0_Setup.exe

[Setup]
; Información de la aplicación
AppName=Procesador de Facturas Electrónicas REGGIS
AppVersion=2.0.0
AppPublisher=Sistema REGGIS
AppPublisherURL=https://github.com/InteligenciaCorreagro/bogota-sae
AppSupportURL=https://github.com/InteligenciaCorreagro/bogota-sae/issues
AppUpdatesURL=https://github.com/InteligenciaCorreagro/bogota-sae/releases
AppCopyright=Copyright (C) 2025 Sistema REGGIS

; Identificador único de la aplicación (generar nuevo GUID si es necesario)
AppId={{B5E8F3A9-4C2D-4E1A-9B8D-7F3E6A2C8D5F}

; Configuración de instalación
DefaultDirName={autopf}\BogotaSAE
DefaultGroupName=Procesador de Facturas REGGIS
AllowNoIcons=yes
; LicenseFile=..\LICENSE
; InfoBeforeFile=..\README.md
OutputDir=installer_output
OutputBaseFilename=BogotaSAE_v2.0.0_Setup

; Compresión
Compression=lzma2/max
SolidCompression=yes

; Configuración visual
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Configuración de privilegios
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Arquitectura
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Versión mínima de Windows (Windows 10)
MinVersion=10.0

; Desinstalador
UninstallDisplayIcon={app}\BogotaSAE.exe
UninstallDisplayName=Procesador de Facturas REGGIS

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Ejecutable principal
Source: "..\dist\BogotaSAE.exe"; DestDir: "{app}"; Flags: ignoreversion

; Plantilla Excel (si existe)
Source: "..\Plantilla_REGGIS.xlsx"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist; AfterInstall: SetReadOnly(ExpandConstant('{app}\Plantilla_REGGIS.xlsx'), False)

; Documentación
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "..\README_DEPLOYMENT.md"; DestDir: "{app}"; Flags: ignoreversion

; Icono (descomentar si tienes un icono)
; Source: "..\build\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Menú Inicio
Name: "{group}\Procesador de Facturas REGGIS"; Filename: "{app}\BogotaSAE.exe"
Name: "{group}\{cm:UninstallProgram,Procesador de Facturas REGGIS}"; Filename: "{uninstallexe}"
Name: "{group}\Documentación"; Filename: "{app}\README.md"

; Escritorio (opcional)
Name: "{autodesktop}\Procesador de Facturas REGGIS"; Filename: "{app}\BogotaSAE.exe"; Tasks: desktopicon

; Quick Launch (opcional, solo versiones antiguas de Windows)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Procesador de Facturas REGGIS"; Filename: "{app}\BogotaSAE.exe"; Tasks: quicklaunchicon

[Run]
; Ejecutar aplicación después de instalación
Filename: "{app}\BogotaSAE.exe"; Description: "{cm:LaunchProgram,Procesador de Facturas REGGIS}"; Flags: nowait postinstall skipifsilent

[Code]
// Función para quitar atributo de solo lectura
procedure SetReadOnly(FileName: String; ReadOnly: Boolean);
var
  Attributes: Integer;
begin
  Attributes := GetFileAttributes(FileName);
  if ReadOnly then
    SetFileAttributes(FileName, Attributes or FILE_ATTRIBUTE_READONLY)
  else
    SetFileAttributes(FileName, Attributes and not FILE_ATTRIBUTE_READONLY);
end;

// Verificar si ya está instalada una versión anterior
function InitializeSetup(): Boolean;
var
  OldVersion: String;
  UninstallKey: String;
begin
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B5E8F3A9-4C2D-4E1A-9B8D-7F3E6A2C8D5F}_is1';

  if RegQueryStringValue(HKLM, UninstallKey, 'DisplayVersion', OldVersion) then
  begin
    if MsgBox('Ya existe una versión instalada (' + OldVersion + ').' + #13#10 +
              '¿Desea desinstalarla antes de continuar?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Aquí podría ejecutarse el desinstalador automáticamente
      Result := True;
    end
    else
      Result := True;
  end
  else
    Result := True;
end;

[UninstallDelete]
; Eliminar archivos generados por la aplicación
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\Resultados_*"

[Registry]
; Asociación de archivos (opcional)
; Descomentar para asociar archivos .xml con la aplicación
; Root: HKCR; Subkey: ".xml\OpenWithProgids"; ValueType: string; ValueName: "BogotaSAE.XMLFile"; ValueData: ""; Flags: uninsdeletevalue
; Root: HKCR; Subkey: "BogotaSAE.XMLFile"; ValueType: string; ValueName: ""; ValueData: "Factura Electrónica XML"; Flags: uninsdeletekey
; Root: HKCR; Subkey: "BogotaSAE.XMLFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\BogotaSAE.exe,0"
; Root: HKCR; Subkey: "BogotaSAE.XMLFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\BogotaSAE.exe"" ""%1"""
