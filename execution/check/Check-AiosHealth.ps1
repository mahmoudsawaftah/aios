# Check-AiosHealth.ps1
# Comprehensive read-only health check for aios standards, projects, and memory.
# Safe to run anytime. Excludes vault/ and node_modules from recursive traversals.

[CmdletBinding()]
param()

$AiosRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..") | Select-Object -ExpandProperty Path
$VaultRoot = Join-Path $AiosRoot "vault"
$ProjectsRoot = Join-Path $AiosRoot "projects"
$MemoryIndex = Join-Path $VaultRoot "memory\MEMORY.md"

$Findings = [System.Collections.Generic.List[string]]::new()
$Warnings = [System.Collections.Generic.List[string]]::new()
$Passes = [System.Collections.Generic.List[string]]::new()

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Running aios Health Check: $AiosRoot" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Check Junction to moevault
if (Test-Path $VaultRoot) {
    $item = Get-Item $VaultRoot
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        $Passes.Add("Vault junction is active -> $(Get-Item $VaultRoot | Select-Object -ExpandProperty Target)")
    } else {
        $Warnings.Add("aios\vault exists but is NOT a junction.")
    }
} else {
    $Findings.Add("CRITICAL: aios\vault junction does not exist.")
}

# 2. Check MEMORY.md and Memory Notes Alignment
if (Test-Path $MemoryIndex) {
    $Passes.Add("Found MEMORY.md index.")
    $memContent = Get-Content $MemoryIndex -Raw
    
    # Extract markdown links [text](target.md)
    $matches = [regex]::Matches($memContent, '\[.*?\]\((.*?\.md)\)')
    $linkedFiles = @($matches | ForEach-Object { $_.Groups[1].Value })
    
    # Check each linked file resolves
    foreach ($lf in $linkedFiles) {
        $targetFile = Join-Path (Join-Path $VaultRoot "memory") $lf
        if (Test-Path $targetFile) {
            $Passes.Add("Memory link resolves: $lf")
        } else {
            $Findings.Add("Broken memory link in MEMORY.md: $lf does not exist.")
        }
    }
    
    # Check if there are memory notes not listed in MEMORY.md
    $actualMemFiles = Get-ChildItem (Join-Path $VaultRoot "memory") -Filter "*.md" | Where-Object Name -ne "MEMORY.md"
    foreach ($amf in $actualMemFiles) {
        if ($linkedFiles -notcontains $amf.Name) {
            $Warnings.Add("Orphan memory note: $($amf.Name) is not linked in MEMORY.md")
        }
    }
} else {
    $Findings.Add("CRITICAL: MEMORY.md missing at $MemoryIndex")
}

# 3. Check Projects vs INDEX.md
$IndexFile = Join-Path $ProjectsRoot "INDEX.md"
if (Test-Path $IndexFile) {
    $indexText = Get-Content $IndexFile -Raw
    $realProjects = Get-ChildItem $ProjectsRoot -Directory | Where-Object { $_.Name -ne "_template" }
    
    foreach ($p in $realProjects) {
        $pName = $p.Name
        $pPath = $p.FullName
        
        # Check registered in INDEX.md
        if ($indexText -notmatch [regex]::Escape($pName)) {
            $Findings.Add("Project '$pName' exists on disk but is MISSING from projects/INDEX.md")
        } else {
            $Passes.Add("Project '$pName' is registered in INDEX.md")
        }
        
        # Check Git remote
        $remote = (git -C $pPath remote get-url origin 2>$null)
        if (-not $remote) {
            $Findings.Add("Project '$pName' has NO GIT REMOTE! Work is at risk on local disk.")
        } else {
            $Passes.Add("Project '$pName' remote: $remote")
        }
        
        # Check uncommitted changes
        $uncommitted = (git -C $pPath status --porcelain 2>$null | Measure-Object).Count
        if ($uncommitted -gt 0) {
            $Warnings.Add("Project '$pName' has $uncommitted uncommitted changes.")
        }
        
        # Check unpushed commits
        $unpushed = (git -C $pPath rev-list --count "@{u}..HEAD" 2>$null)
        if ($unpushed -gt 0) {
            $Warnings.Add("Project '$pName' has $unpushed unpushed commits.")
        }
        
        # Check .env ignored
        if (Test-Path (Join-Path $pPath ".env")) {
            $ignored = (git -C $pPath check-ignore .env 2>$null)
            if (-not $ignored) {
                $Findings.Add("CRITICAL: '$pName\.env' is NOT ignored by its .gitignore!")
            }
        }
        if (Test-Path (Join-Path $pPath ".env.local")) {
            $ignoredLocal = (git -C $pPath check-ignore .env.local 2>$null)
            if (-not $ignoredLocal) {
                $Findings.Add("CRITICAL: '$pName\.env.local' is NOT ignored by its .gitignore!")
            }
        }
        
        # Check standard files
        if (-not (Test-Path (Join-Path $pPath "README.md"))) {
            $Warnings.Add("Project '$pName' is missing README.md")
        }
        if (-not (Test-Path (Join-Path $pPath "AGENTS.md"))) {
            $Warnings.Add("Project '$pName' is missing AGENTS.md pointer")
        }
        
        # Check vault note exists
        $vaultNote = Join-Path (Join-Path $VaultRoot "projects") "$pName.md"
        if (-not (Test-Path $vaultNote)) {
            $Warnings.Add("Project '$pName' has no corresponding vault note at $vaultNote")
        } else {
            $Passes.Add("Project '$pName' has matching vault note.")
        }
    }
} else {
    $Findings.Add("projects/INDEX.md missing.")
}

# 4. Check for Loose Files in aios Root
$allowedRootFiles = @(
    "README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md",
    ".env.example", ".gitignore", ".gitattributes"
)
$rootFiles = Get-ChildItem $AiosRoot -File -Force | Where-Object { $allowedRootFiles -notcontains $_.Name }
foreach ($rf in $rootFiles) {
    $Warnings.Add("Loose file in aios root: $($rf.Name) (move to raw/ or output/)")
}

# 5. Check Reminders Overdue
$RemindersDir = Join-Path $AiosRoot "reminders"
if (Test-Path $RemindersDir) {
    $today = Get-Date -Format "yyyy-MM-dd"
    $reminders = Get-ChildItem $RemindersDir -Filter "*.md" | Where-Object { $_.Name -ne "README.md" }
    foreach ($r in $reminders) {
        if ($r.Name -match '^(\d{4}-\d{2}-\d{2})') {
            $remDate = $matches[1]
            if ($remDate -lt $today) {
                $content = Get-Content $r.FullName -Raw
                if ($content -match 'STATUS:\s*OPEN|status:\s*open') {
                    $Findings.Add("Overdue reminder: $($r.Name) was due on $remDate and is still OPEN.")
                }
            }
        }
    }
}

# 6. Check aios Repository Unpushed Commits
$aiosUnpushed = (git -C $AiosRoot rev-list --count "@{u}..HEAD" 2>$null)
if ($aiosUnpushed -gt 0) {
    $Warnings.Add("aios repository has $aiosUnpushed unpushed commits.")
}

# Summary Report
Write-Host "`n--- Summary ---" -ForegroundColor Cyan
Write-Host "Passes:   $($Passes.Count)" -ForegroundColor Green
Write-Host "Warnings: $($Warnings.Count)" -ForegroundColor Yellow
Write-Host "Findings: $($Findings.Count)" -ForegroundColor Red

if ($Warnings.Count -gt 0) {
    Write-Host "`n[!] Warnings:" -ForegroundColor Yellow
    foreach ($w in $Warnings) { Write-Host " - $w" -ForegroundColor Yellow }
}

if ($Findings.Count -gt 0) {
    Write-Host "`n[x] Critical Findings:" -ForegroundColor Red
    foreach ($f in $Findings) { Write-Host " - $f" -ForegroundColor Red }
    exit 1
} else {
    Write-Host "`nHealth check PASSED clean." -ForegroundColor Green
    exit 0
}
