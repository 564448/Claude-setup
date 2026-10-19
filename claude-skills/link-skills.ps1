<#
.SYNOPSIS
  Links every shippable skill in this repo into the folder Claude Code loads it from.

.DESCRIPTION
  Claude Code only discovers skills one level deep (<skills-dir>/<name>/SKILL.md), so the
  bucketed layout here (skills/<bucket>/<name>/) has to be flattened with directory junctions.
  Junctions need no admin rights or Developer Mode.

    general/     -> ~/.claude/skills           (user scope: available in every folder)
    cs/          -> <setup root>\.claude\skills   (project scope: only inside the setup root)
    project/     -> <setup root>\.claude\skills
    in-progress/ -> not linked
    deprecated/  -> not linked

  Also removes stale junctions that point into this repo but no longer match a shippable skill
  (e.g. a skill that was moved to deprecated/). Real folders are never deleted.

.PARAMETER DryRun
  Print what would change without touching anything.
#>
param([switch]$DryRun)

$ErrorActionPreference = 'Stop'
$repo   = $PSScriptRoot
$root   = (Resolve-Path "$repo\..").Path

$dest = @{
    'general' = Join-Path $env:USERPROFILE '.claude\skills'
    'cs'      = Join-Path $root '.claude\skills'
    'project' = Join-Path $root '.claude\skills'
}

function Get-JunctionTarget($path) {
    $item = Get-Item -LiteralPath $path -Force
    if ($item.LinkType -ne 'Junction' -and $item.LinkType -ne 'SymbolicLink') { return $null }
    return @($item.Target)[0]
}

function Remove-Junction($path) {
    # Directory.Delete on a junction removes only the link, never the target's contents.
    if ($DryRun) { Write-Host "would unlink $path"; return }
    [System.IO.Directory]::Delete($path, $false)
}

# Collect shippable skills and refuse duplicate names (flattening would make one silently win).
$skills = @{}
foreach ($bucket in $dest.Keys) {
    Get-ChildItem (Join-Path $repo "skills\$bucket") -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
        ForEach-Object {
            if ($skills.ContainsKey($_.Name)) {
                throw "Duplicate skill name '$($_.Name)' in skills\$bucket and skills\$($skills[$_.Name].Bucket)"
            }
            $skills[$_.Name] = [pscustomobject]@{ Bucket = $bucket; Source = $_.FullName }
        }
}

# Link each skill.
foreach ($name in ($skills.Keys | Sort-Object)) {
    $s      = $skills[$name]
    $target = Join-Path $dest[$s.Bucket] $name

    if (Test-Path -LiteralPath $target) {
        $current = Get-JunctionTarget $target
        if ($null -eq $current) {
            Write-Warning "skip ${name}: $target is a real folder, not a link. Move it into the repo or delete it, then re-run."
            continue
        }
        if ($current -eq $s.Source) { Write-Host "ok      $name"; continue }
        Remove-Junction $target
    }

    if ($DryRun) { Write-Host "would link $target -> $($s.Source)"; continue }
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    New-Item -ItemType Junction -Path $target -Target $s.Source | Out-Null
    Write-Host "linked  $name -> skills\$($s.Bucket)\$name"
}

# Prune links into this repo that are no longer shippable.
foreach ($dir in ($dest.Values | Sort-Object -Unique)) {
    if (-not (Test-Path $dir)) { continue }
    Get-ChildItem $dir -Directory -Force | ForEach-Object {
        $t = Get-JunctionTarget $_.FullName
        if ($t -and $t.StartsWith("$repo\", [StringComparison]::OrdinalIgnoreCase)) {
            $s = $skills[$_.Name]
            if (-not $s -or $s.Source -ne $t -or $dest[$s.Bucket] -ne $dir) {
                Remove-Junction $_.FullName
                if (-not $DryRun) { Write-Host "pruned  $($_.FullName) (was -> $t)" }
            }
        }
    }
}
