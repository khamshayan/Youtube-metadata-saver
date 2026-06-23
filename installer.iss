[Setup]
AppName=Youtube metadata saver
AppVersion=1.0
AppPublisher=Youtube metadata saver
DefaultDirName={autopf}\Youtube metadata saver
DefaultGroupName=Youtube metadata saver
OutputDir=installer_output
OutputBaseFilename=Youtube metadata saver Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=no
AllowNoIcons=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\Youtube metadata saver\Youtube metadata saver.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Youtube metadata saver\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Youtube metadata saver";   Filename: "{app}\Youtube metadata saver.exe"
Name: "{group}\Uninstall Youtube metadata saver"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Youtube metadata saver";   Filename: "{app}\Youtube metadata saver.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Youtube metadata saver.exe"; Description: "Launch Youtube metadata saver"; Flags: nowait postinstall skipifsilent
