# Item Space AI -> Codex CLI + supported IDE MCP setup. No admin privileges.
# Run only after reviewing the local MCP server code.
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$Mcp = Join-Path $Root "scripts\item_space_mcp.py"
if (-not (Test-Path -LiteralPath $Mcp -PathType Leaf)) { throw "MCP script missing." }
$Python = Get-Command python -ErrorAction Stop
$Codex = Get-Command codex -ErrorAction Stop
Write-Host "Item Space AI MCP server: $Mcp"
Write-Host "Python executable: $($Python.Source)"
Write-Host "Codex executable: $($Codex.Source)"

# Avoid overwriting any existing server or user's shared Codex config.
& codex mcp get item-space-ai *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Warning "MCP server item-space-ai already registered. Not overwriting it."
    & codex mcp list
    exit 0
}

& codex mcp add item-space-ai -- $Python.Source $Mcp
if ($LASTEXITCODE -ne 0) { throw "Codex MCP registration failed. Inspect codex mcp --help." }
Write-Host ""
Write-Host "Item Space AI MCP registered." -ForegroundColor Green
Write-Host "Restart Codex CLI / Codex IDE extension inside Antigravity."
Write-Host "Verify: codex mcp list"
Write-Host "Tell Codex: Use item-space-ai MCP to submit this project idea and track its task."
Write-Host "The separate queue worker must be started for autonomous execution."
