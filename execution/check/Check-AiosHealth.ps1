# Read-only control repository check. Never traverses products, vault or archives.
[CmdletBinding()]
param()

$AiosRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Required = @(
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "README.md", "README_FACTORY.md",
    "projects\INDEX.md", "projects\_template\AGENTS.md",
    "docs\AIOS_SOFTWARE_FACTORY.md", "docs\HYBRID_DELIVERY_METHODOLOGY.md",
    "governance\SECURITY_AND_APPROVALS.md", "factory\cli.py",
    "scripts\audit_legacy_projects.py"
)
$Failures = 0
foreach ($Relative in $Required) {
    if (Test-Path -LiteralPath (Join-Path $AiosRoot $Relative) -PathType Leaf) {
        Write-Host "PASS: $Relative"
    } else {
        Write-Host "FAIL: missing $Relative"
        $Failures++
    }
}
if (Test-Path -LiteralPath (Join-Path $AiosRoot "vault\memory\MEMORY.md") -PathType Leaf) {
    Write-Host "Optional memory index is available; contents were not scanned."
} else {
    Write-Warning "Optional memory index is unavailable. No external data was created."
}
Write-Host "Products are external. Only registry/template metadata was inspected."
Write-Host "Run README.md unit tests and legacy audit for full verification."
if ($Failures -gt 0) { exit 1 }
exit 0
