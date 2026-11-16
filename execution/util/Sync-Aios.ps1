# Legacy entry point retained as a read-only review helper.
# Publication is a separate owner-approved action; no staging or remote operations.
[CmdletBinding()]
param([string]$Message)

$AiosRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Write-Host "Read-only AIOS review. No files will be staged, committed or pushed."
if ($Message) {
    Write-Host "The legacy Message parameter is accepted but no commit will be created."
}
git -C $AiosRoot status --short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git -C $AiosRoot diff --stat
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git -C $AiosRoot diff --check
exit $LASTEXITCODE
