; Inno Setup script of the Windows installer. It is compiled by `poetry run rss-build --win`,
; which passes AppVersion, SourceDir (PyInstaller output), OutputDir, OutputName and RootDir.

#ifndef AppVersion
  #error AppVersion must be given, e.g. ISCC /DAppVersion=2.0.0
#endif

[Setup]
; Do not change the AppId: it identifies the app for upgrades and for the uninstaller
AppId={{8F4B2C6E-3D1A-4E7B-9A52-6C0D7E1F3B84}
AppName=RSS-ISLANDR
AppVersion={#AppVersion}
AppVerName=RSS-ISLANDR {#AppVersion}
AppPublisher=CERTH
AppPublisherURL=https://github.com/GMECH7/rss_islandr
DefaultDirName={autopf}\RSS-ISLANDR
DefaultGroupName=RSS-ISLANDR
DisableProgramGroupPage=yes
; Installs for the current user without administrator rights, unless the user chooses "for all users"
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile={#RootDir}\LICENSE
SetupIconFile={#RootDir}\rss_islandr\static\islandr.ico
UninstallDisplayIcon={app}\islandr.exe
OutputDir={#OutputDir}
OutputBaseFilename={#OutputName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\RSS-ISLANDR"; Filename: "{app}\islandr.exe"
Name: "{autodesktop}\RSS-ISLANDR"; Filename: "{app}\islandr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\islandr.exe"; Description: "{cm:LaunchProgram,RSS-ISLANDR}"; Flags: nowait postinstall skipifsilent
