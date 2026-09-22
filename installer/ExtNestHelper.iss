#define MyAppName "ExtNest Helper"
#define MyAppVersion "0.5.0"
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
CloseApplications=no
RestartApplications=no

[Files]
Source: "..\build\helper\ExtNestHost.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\helper\oauth-clients.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\helper\oauth-private.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\helper\com.extnest.host.template.json"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host"; ValueType: string; ValueName: ""; ValueData: "{app}\com.extnest.host.json"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Google\Chrome\NativeMessagingHosts\com.extnest.host"; ValueType: string; ValueName: ""; ValueData: "{app}\com.extnest.host.json"; Flags: uninsdeletekey

[UninstallDelete]
Type: files; Name: "{app}\com.extnest.host.json"

[Code]
function JsonEscape(Value: String): String;
begin
  Result := Value;
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  TemplatePath: String;
  ManifestPath: String;
  HostPath: String;
  RawJson: AnsiString;
  Json: String;
begin
  if CurStep = ssPostInstall then
  begin
    TemplatePath := ExpandConstant('{app}\com.extnest.host.template.json');
    ManifestPath := ExpandConstant('{app}\com.extnest.host.json');
    HostPath := ExpandConstant('{app}\ExtNestHost.exe');

    if not LoadStringFromFile(TemplatePath, RawJson) then
      RaiseException('Falha ao ler o template do Native Host.');

    Json := String(RawJson);
    StringChangeEx(Json, '__EXTNEST_HOST_PATH__', JsonEscape(HostPath), True);

    if not SaveStringToFile(ManifestPath, AnsiString(Json), False) then
      RaiseException('Falha ao criar o manifest do ExtNest Native Host.');

    DeleteFile(TemplatePath);
  end;
end;
