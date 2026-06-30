<#
.SYNOPSIS
  Sync Petra-Lab-X skills into the local Cursor + Claude global skill directories.
  Idempotent: pulls latest, then replaces each ~/.cursor/skills/<name> and
  ~/.claude/skills/<name> with this repo's version.
#>
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
try { git -C $repoRoot pull --ff-only 2>$null } catch { Write-Warning "git pull skipped: $($_.Exception.Message)" }

$src = Join-Path $repoRoot "skills"
if (-not (Test-Path $src)) { Write-Error "No skills/ directory in $repoRoot"; exit 1 }

foreach ($target in @("$HOME\.cursor\skills", "$HOME\.claude\skills")) {
  New-Item -ItemType Directory -Force -Path $target | Out-Null
  Get-ChildItem $src -Directory | ForEach-Object {
    $dest = Join-Path $target $_.Name
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item $_.FullName -Destination $dest -Recurse -Force
    Write-Output ("synced -> " + $dest)
  }
}
Write-Output "Done. Restart/reload Cursor sessions to pick up new skills."
