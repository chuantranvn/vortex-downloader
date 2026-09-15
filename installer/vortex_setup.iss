; Inno Setup Script cho Vortex Downloader
; Đóng gói ứng dụng Desktop PySide6 + Microservices + Extension Chrome/Edge

#define MyAppName "Vortex Downloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Adjim Studio"
#define MyAppURL "https://github.com/chuantranvn/vortex-downloader"
#define MyAppExeName "VortexDownloader.exe"

[Setup]
AppId={{E88A1F8D-5F66-4F2A-949F-97217B79E66F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\installer_output
OutputBaseFilename=Vortex_Downloader_Setup
SetupIconFile=..\client\desktop_gui\assets\vortex_icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
VersionInfoVersion=1.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Vortex Downloader Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
CloseApplications=yes
CloseApplicationsFilter=*{#MyAppExeName}*
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog commandline
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "Tự động khởi động cùng Windows (Chạy ngầm ở khay hệ thống khi bật máy)"; GroupDescription: "Tùy chọn hệ thống:"

[Files]
Source: "..\dist\VortexDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Thư mục cài đặt {#MyAppName}"; Filename: "{app}"
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "VortexDownloader"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
