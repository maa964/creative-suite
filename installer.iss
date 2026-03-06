[Setup]
AppName=Creative Suite
AppVersion=1.0.0
DefaultDirName={autopf}\Creative Suite
DefaultGroupName=Creative Suite
OutputDir=dist\installer
OutputBaseFilename=CreativeSuite_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\launcher.exe

[Files]
Source: "dist\launcher\launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\launcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Creative Suite"; Filename: "{app}\launcher.exe"
Name: "{commondesktop}\Creative Suite"; Filename: "{app}\launcher.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
