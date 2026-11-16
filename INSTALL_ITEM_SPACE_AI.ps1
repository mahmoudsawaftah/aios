# item space AI — create or update a desktop shortcut. No admin rights required.
# Run from the AIOS repository: powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\INSTALL_ITEM_SPACE_AI.ps1
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'The desktop installer supports Windows only.'
}

$Root = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$Target = Join-Path $Root 'START_ITEM_SPACE_AI.cmd'
if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) {
    throw "Launcher is missing: $Target"
}

$Desktop = [Environment]::GetFolderPath('DesktopDirectory')
if ([string]::IsNullOrWhiteSpace($Desktop) -or -not (Test-Path -LiteralPath $Desktop)) {
    throw "Windows desktop location could not be resolved. Shortcut was not created."
}

$IconPath = Join-Path $Root '.factory-runtime\assets\item-space-ai.ico'
Push-Location -LiteralPath $Root
try {
    & python -m factory.branding --output $IconPath
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $IconPath -PathType Leaf)) {
        throw 'Could not create the desktop icon. Check your Python installation.'
    }
} finally {
    Pop-Location
}

$ShortcutPath = Join-Path $Desktop 'item space AI.lnk'
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.WorkingDirectory = $Root
$Shortcut.Description = 'item space AI - local Mission Control'
$Shortcut.WindowStyle = 7
$Shortcut.IconLocation = "$IconPath,0"
$Shortcut.Save()

Write-Host ''
Write-Host 'Desktop shortcut created successfully:' -ForegroundColor Green
Write-Host "  $ShortcutPath"
Write-Host 'Double-click item space AI to start the local server and open the dashboard.'
Write-Host 'Codex auto-run remains OFF unless separately and explicitly enabled.'
