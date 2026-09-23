[CmdletBinding()]
param(
    [switch]$Restore,
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'Programs\Antigravity IDE')
)

$ErrorActionPreference = 'Stop'

$productPath = Join-Path $InstallRoot 'resources\app\product.json'
$workbenchPath = Join-Path $InstallRoot 'resources\app\out\vs\workbench\workbench.desktop.main.js'
$productBackupPath = "$productPath.codex-agent-original"
$workbenchBackupPath = "$workbenchPath.codex-agent-original"

foreach ($requiredPath in @($productPath, $workbenchPath)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required Antigravity file not found: $requiredPath"
    }
}

if ($Restore) {
    foreach ($backupPath in @($productBackupPath, $workbenchBackupPath)) {
        if (-not (Test-Path -LiteralPath $backupPath -PathType Leaf)) {
            throw "Backup not found: $backupPath"
        }
    }

    Copy-Item -LiteralPath $productBackupPath -Destination $productPath -Force
    Copy-Item -LiteralPath $workbenchBackupPath -Destination $workbenchPath -Force
    Write-Output 'Restored the original Antigravity product and workbench files.'
    Write-Output 'Fully restart Antigravity IDE to load the restored files.'
    exit 0
}

$productText = [System.IO.File]::ReadAllText($productPath)
$workbenchText = [System.IO.File]::ReadAllText($workbenchPath)

$productMarker = "`t`"extensionEnabledApiProposals`": {"
$productEntry = @"

		"openai.chatgpt": [
			"chatSessionsProvider",
			"languageModelProxy"
		],
"@

if ($productText -notmatch '"openai\.chatgpt"\s*:') {
    $productMarkerCount = ([regex]::Matches($productText, [regex]::Escape($productMarker))).Count
    if ($productMarkerCount -ne 1) {
        throw "Expected one product.json proposal marker, found $productMarkerCount."
    }
    $productText = $productText.Replace($productMarker, $productMarker + $productEntry)
}

$serviceMarker = 'var TCt=ui("agentSessions");'
$serviceRegistration = 'Bi(TCt,E6a,1);'

if (-not $workbenchText.Contains($serviceRegistration)) {
    $serviceMarkerCount = ([regex]::Matches($workbenchText, [regex]::Escape($serviceMarker))).Count
    if ($serviceMarkerCount -ne 1) {
        throw "Expected one agentSessions service marker, found $serviceMarkerCount."
    }
    $workbenchText = $workbenchText.Replace($serviceMarker, $serviceMarker + $serviceRegistration)
}

# Validate the product JSON before writing either patched file.
$null = $productText | ConvertFrom-Json

if (-not (Test-Path -LiteralPath $productBackupPath)) {
    Copy-Item -LiteralPath $productPath -Destination $productBackupPath
}
if (-not (Test-Path -LiteralPath $workbenchBackupPath)) {
    Copy-Item -LiteralPath $workbenchPath -Destination $workbenchBackupPath
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($productPath, $productText, $utf8NoBom)
[System.IO.File]::WriteAllText($workbenchPath, $workbenchText, $utf8NoBom)

$nodeCommand = Get-Command node -ErrorAction Stop
& $nodeCommand.Source --check $workbenchPath
if ($LASTEXITCODE -ne 0) {
    Copy-Item -LiteralPath $productBackupPath -Destination $productPath -Force
    Copy-Item -LiteralPath $workbenchBackupPath -Destination $workbenchPath -Force
    throw 'JavaScript syntax validation failed. Original files were restored.'
}

$verifiedProduct = Get-Content -Raw -LiteralPath $productPath | ConvertFrom-Json
$verifiedWorkbench = [System.IO.File]::ReadAllText($workbenchPath)
$proposals = @($verifiedProduct.extensionEnabledApiProposals.'openai.chatgpt')

if ($proposals -notcontains 'chatSessionsProvider' -or $proposals -notcontains 'languageModelProxy') {
    throw 'OpenAI proposed API permissions were not installed correctly.'
}
if (-not $verifiedWorkbench.Contains($serviceMarker + $serviceRegistration)) {
    throw 'The agentSessions service registration was not installed correctly.'
}

Write-Output 'Patched Antigravity Codex Agent integration successfully.'
Write-Output "Product backup: $productBackupPath"
Write-Output "Workbench backup: $workbenchBackupPath"
Write-Output 'Fully restart Antigravity IDE, then open New Codex Agent in the editor area.'
