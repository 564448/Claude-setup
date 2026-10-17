<#
.SYNOPSIS
  Restores the Claude Code setup from this repo on a new Windows PC.

.DESCRIPTION
  Run from inside a clone that lives at C:\Knight (skill junctions and the memory folder name
  both depend on that path). Does not touch credentials: log in to Claude Code and gh yourself.

  1. links the self-written skills        (Project\claude-skills\link-skills.ps1)
  2. links the third-party skills         (.agents\skills\* -> .claude\skills)
  3. copies user-claude\ into ~\.claude   (existing files are backed up as *.bak, never overwritten)
  4. installs the plugins named in user-claude\settings.json, if the `claude` CLI is on PATH
#>
$ErrorActionPreference = 'Stop'
$knight = $PSScriptRoot
if ($knight -ne 'C:\Knight') { throw "Clone this repo to C:\Knight (currently at $knight)." }

& "$knight\Project\claude-skills\link-skills.ps1"

$projSkills = Join-Path $knight '.claude\skills'
New-Item -ItemType Directory -Force $projSkills | Out-Null
foreach ($s in Get-ChildItem "$knight\.agents\skills" -Directory) {
    $link = Join-Path $projSkills $s.Name
    if (-not (Test-Path $link)) { New-Item -ItemType Junction -Path $link -Target $s.FullName | Out-Null }
}

$claude = Join-Path $env:USERPROFILE '.claude'
$mem    = Join-Path $claude 'projects\C--Knight\memory'
New-Item -ItemType Directory -Force $claude, $mem | Out-Null
$copies = @(
    @{ From = "$knight\user-claude\settings.json";           To = "$claude\settings.json" },
    @{ From = "$knight\user-claude\statusline-command.sh";   To = "$claude\statusline-command.sh" }
) + (Get-ChildItem "$knight\user-claude\memory" -File | ForEach-Object { @{ From = $_.FullName; To = "$mem\$($_.Name)" } })
foreach ($c in $copies) {
    if ((Test-Path $c.To) -and ((Get-FileHash $c.To).Hash -ne (Get-FileHash $c.From).Hash)) {
        Copy-Item $c.To "$($c.To).bak" -Force
    }
    Copy-Item $c.From $c.To -Force
}

if (Get-Command claude -ErrorAction SilentlyContinue) {
    $settings = Get-Content "$knight\user-claude\settings.json" -Raw | ConvertFrom-Json
    foreach ($p in $settings.enabledPlugins.PSObject.Properties.Name) { claude plugin install $p }
} else {
    Write-Warning 'claude CLI not found: install Claude Code, then re-run this script to install plugins.'
}
Write-Host 'Done. Log in to Claude Code (/login) and run: gh auth login'
