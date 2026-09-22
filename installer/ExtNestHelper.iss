#define MyAppName "ExtNest Helper"
#define MyAppVersion "0.4.0"
#define MyAppPublisher "ExtNest"
#define MyAppExeName "ExtNestHost.exe"

[Setup]
AppId={{B1D6B9F4-0C9B-4B63-96A8-9C9CEFC48E82}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\ExtNest\NativeHost
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=ExtNestHelperSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "..\build\helper\ExtNestHost.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\helper\oauth-clients.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\helper\oauth-private.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\helper\git\*"; DestDir: "{app}\git"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host"; ValueType: string; ValueName: ""; ValueData: "{app}\com.extnest.host.json"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Google\Chrome\NativeMessagingHosts\com.extnest.host"; ValueType: string; ValueName: ""; ValueData: "{app}\com.extnest.host.json"; Flags: uninsdeletekey

[Run]
Filename: "{cmd}"; Parameters: "/C echo {{^"name^":^"com.extnest.host^",^"description^":^"ExtNest Native Messaging Host^",^"path^":^"{app}\ExtNestHost.exe^",^"type^":^"stdio^",^"allowed_origins^":^[^"chrome-extension://econfanmnmmcggpgdflcipmdlmkcbiag/^"^]^}} > ^"{app}\com.extnest.host.json^""; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: files; Name: "{app}\com.extnest.host.json"
