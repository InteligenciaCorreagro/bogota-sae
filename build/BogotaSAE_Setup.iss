; Instalador Windows para Bogota SAE (Inno Setup 6)
; Sincronizar MyAppVersion con src/core/version.py
;
; Compilar:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\BogotaSAE_Setup.iss
; O ejecutar build\build_windows_release.ps1 (genera el EXE y luego el Setup si ISCC existe).

#define MyAppName "Bogota SAE"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "CORREAGRO"
#define MyAppExeName "BogotaSAE.exe"

[Setup]
AppId={{B1C4E8F2-9A3D-4E7B-9C5D-2E8F1A4B6C9D}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=BogotaSAE_Setup_{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\release\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
