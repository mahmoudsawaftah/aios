# Sync-Aios.ps1
# Safe staging, secret-scanning, committing, and pushing for aios standards layer.
# Refuses to run if credentials, projects, comms, or vault are staged.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)

$AiosRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..") | Select-Object -ExpandProperty Path
Set-Location $AiosRoot

Write-Host ">>> Preparing to sync aios standards to origin..." -ForegroundColor Cyan

# 1. Stage changes
git -C $AiosRoot add -A

# 2. Check staged files against boundary rules
$staged = git -C $AiosRoot diff --name-only --cached
$violations = @()

foreach ($file in $staged) {
    if ($file -match '^vault/') {
        $violations += "Vault file staged: $file (vault junction must never be committed)"
    }
    if ($file -match '^comms/') {
        $violations += "Communications file staged: $file (comms/ is confidential)"
    }
    if ($file -match '^\.env|\.env\.') {
        $violations += "Secret file staged: $file (.env files must never be committed)"
    }
    if ($file -match '^projects/' -and $file -notmatch '^projects/(README\.md|INDEX\.md|_template/)') {
        $violations += "Project code file staged: $file (projects are independent repos)"
    }
}

if ($violations.Count -gt 0) {
    Write-Host "ABORTED: Boundary violations detected in staged files:" -ForegroundColor Red
    foreach ($v in $violations) { Write-Host " - $v" -ForegroundColor Red }
    git -C $AiosRoot reset
    exit 1
}

# 3. Secret Pattern Scan
Write-Host ">>> Scanning staged diff for secret patterns..." -ForegroundColor Cyan
$secretPattern = 'password|passwd|secret|api[_-]?key|token|BEGIN .*PRIVATE KEY|AKIA[0-9A-Z]{16}'
$diff = git -C $AiosRoot diff --cached
$secretMatches = $diff | Select-String -Pattern $secretPattern -CaseSensitive:$false

if ($secretMatches) {
    Write-Host "ABORTED: Potential secrets detected in staged diff:" -ForegroundColor Red
    $secretMatches | Select-Object -First 5 | ForEach-Object { Write-Host " Match: $($_.Line)" -ForegroundColor Red }
    git -C $AiosRoot reset
    exit 1
}

# 4. Check if there are changes to commit
$status = git -C $AiosRoot status --porcelain
if (-not $status) {
    Write-Host "No changes to commit. Everything is up to date." -ForegroundColor Green
    exit 0
}

# 5. Commit & Push
Write-Host ">>> Committing with message: '$Message'..." -ForegroundColor Cyan
git -C $AiosRoot commit -m "$Message"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed." -ForegroundColor Red
    exit 1
}

Write-Host ">>> Pushing to origin main..." -ForegroundColor Cyan
git -C $AiosRoot push origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host ">>> Successfully pushed aios standards to origin main!" -ForegroundColor Green
} else {
    Write-Host "Push failed. Check remote repository status." -ForegroundColor Yellow
}
