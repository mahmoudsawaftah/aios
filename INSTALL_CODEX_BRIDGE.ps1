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

# Query the successful LIST endpoint rather than GET for a missing server.
# On Windows PowerShell 5.1, a nonzero native command writing to stderr
# becomes NativeCommandError when $ErrorActionPreference = 'Stop'.
# The absence of a server is expected on first installation.
$RawList = & $Codex.Source mcp list --json
if ($LASTEXITCODE -ne 0) {
    throw "Could not list Codex MCP servers."
}
try {
    $Servers = @($RawList | ConvertFrom-Json)
} catch {
    throw "Codex MCP list returned invalid JSON."
}
$Existing = @($Servers | Where-Object { $_ -and $_.name -eq 'item-space-ai' })
if ($Existing.Count -gt 0) {
    Write-Warning "MCP server item-space-ai already registered. Not overwriting it."
    & $Codex.Source mcp list
    exit 0
}

& $Codex.Source mcp add item-space-ai -- $Python.Source $Mcp
if ($LASTEXITCODE -ne 0) { throw "Codex MCP registration failed. Inspect codex mcp --help." }

$VerifyRaw = & $Codex.Source mcp list --json
if ($LASTEXITCODE -ne 0) {
    throw "Codex MCP registration may have succeeded, but verification failed."
}
$VerifyServers = @($VerifyRaw | ConvertFrom-Json)
if (@($VerifyServers | Where-Object { $_ -and $_.name -eq 'item-space-ai' }).Count -ne 1) {
    throw "Codex MCP server item-space-ai was not found after registration."
}
Write-Host ""
Write-Host "Item Space AI MCP registered." -ForegroundColor Green
Write-Host "Restart Codex CLI / Codex IDE extension inside Antigravity."
Write-Host "Verify: codex mcp list"
Write-Host "Tell Codex: Use item-space-ai MCP to submit this project idea and track its task."
Write-Host "The separate queue worker must be started for autonomous execution."
