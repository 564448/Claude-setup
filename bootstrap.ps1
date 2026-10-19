<#
.SYNOPSIS
  Restores the Claude Code setup from this repo on a new Windows PC.

.DESCRIPTION
  Run from inside the clone (e.g. C:\Knight\Claude, the setup root); the work folders are expected
  in its parent folder (e.g. C:\Knight, the work root). Does not touch credentials: log in to
  Claude Code and gh yourself.

  1. links the self-written skills        (claude-skills\link-skills.ps1)
  2. links the third-party skills         (.agents\skills\* -> .claude\skills)
  3. copies user-claude\ into ~\.claude   (existing files are backed up as *.bak, never overwritten)
  4. lets Claude reach the work folders   (permissions.additionalDirectories)
  5. installs the plugins named in user-claude\settings.json, if the `claude` CLI is on PATH
#>
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$work = Split-Path $root -Parent

& "$root\claude-skills\link-skills.ps1"

$projSkills = Join-Path $root '.claude\skills'
New-Item -ItemType Directory -Force $projSkills | Out-Null
foreach ($s in Get-ChildItem "$root\.agents\skills" -Directory) {
    $link = Join-Path $projSkills $s.Name
    if (-not (Test-Path $link)) { New-Item -ItemType Junction -Path $link -Target $s.FullName | Out-Null }
}

$claude = Join-Path $env:USERPROFILE '.claude'
# Claude Code names a project's memory folder after its path, every non-alphanumeric char -> "-".
$mem    = Join-Path $claude ('projects\' + ($root -replace '[^A-Za-z0-9]', '-') + '\memory')
New-Item -ItemType Directory -Force $claude, $mem | Out-Null
$copies = @(
    @{ From = "$root\user-claude\settings.json";           To = "$claude\settings.json" },
    @{ From = "$root\user-claude\statusline-command.sh";   To = "$claude\statusline-command.sh" }
) + (Get-ChildItem "$root\user-claude\memory" -File -Recurse | ForEach-Object {
    @{ From = $_.FullName; To = Join-Path $mem $_.FullName.Substring("$root\user-claude\memory\".Length) } })
foreach ($c in $copies) {
    New-Item -ItemType Directory -Force (Split-Path $c.To) | Out-Null
    if ((Test-Path $c.To) -and ((Get-FileHash $c.To).Hash -ne (Get-FileHash $c.From).Hash)) {
        Copy-Item $c.To "$($c.To).bak" -Force
    }
    Copy-Item $c.From $c.To -Force
}

$userSettings = "$claude\settings.json"
$json = Get-Content $userSettings -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $json.permissions) { $json | Add-Member -NotePropertyName permissions -NotePropertyValue ([pscustomobject]@{}) }
if (-not $json.permissions.additionalDirectories) {
    $json.permissions | Add-Member -NotePropertyName additionalDirectories -NotePropertyValue @()
}
if ($json.permissions.additionalDirectories -notcontains $work) {
    $json.permissions.additionalDirectories = @($json.permissions.additionalDirectories) + $work
    [System.IO.File]::WriteAllText($userSettings, ($json | ConvertTo-Json -Depth 20), (New-Object System.Text.UTF8Encoding $false))
}

if (Get-Command claude -ErrorAction SilentlyContinue) {
    $settings = Get-Content "$root\user-claude\settings.json" -Raw | ConvertFrom-Json
    foreach ($p in $settings.enabledPlugins.PSObject.Properties.Name) { claude plugin install $p }
} else {
    Write-Warning 'claude CLI not found: install Claude Code, then re-run this script to install plugins.'
}
Write-Host 'Done. Log in to Claude Code (/login) and run: gh auth login'
