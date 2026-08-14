<#
.SYNOPSIS
  Sync Petra-Lab-X skills into local global skill directories for Cursor, Claude,
  Grok, Hermes, and .agents. Idempotent: pulls latest, then replaces each
  ~/.cursor/skills/<name>, ~/.claude/skills/<name>, ~/.grok/skills/<name>,
  ~/.agents/skills/<name>, and ~/.hermes/skills/<name> with this repo's version.

  git pull --ff-only is fail-closed: a dirty or diverged clone must not silently
  install a stale catalog.
#>
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
git -C $repoRoot pull --ff-only

$src = Join-Path $repoRoot "skills"
if (-not (Test-Path $src)) { Write-Error "No skills/ directory in $repoRoot"; exit 1 }

foreach ($target in @(
  "$HOME\.cursor\skills",
  "$HOME\.claude\skills",
  "$HOME\.grok\skills",
  "$HOME\.agents\skills",
  "$HOME\.hermes\skills"
)) {
  New-Item -ItemType Directory -Force -Path $target | Out-Null
  Get-ChildItem $src -Directory | ForEach-Object {
    $dest = Join-Path $target $_.Name
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item $_.FullName -Destination $dest -Recurse -Force
    Write-Output ("synced -> " + $dest)
  }
}
Write-Output "Done. Restart/reload Cursor sessions to pick up new skills."
