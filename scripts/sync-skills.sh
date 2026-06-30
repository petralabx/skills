#!/usr/bin/env bash
# Sync Petra-Lab-X skills into the local Cursor + Claude global skill directories.
# Idempotent: pulls latest, then replaces each ~/.cursor/skills/<name> and
# ~/.claude/skills/<name> with this repo's version.
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
git -C "$repo_root" pull --ff-only 2>/dev/null || echo "git pull skipped"
src="$repo_root/skills"
[ -d "$src" ] || { echo "No skills/ directory in $repo_root"; exit 1; }

for target in "$HOME/.cursor/skills" "$HOME/.claude/skills"; do
  mkdir -p "$target"
  for d in "$src"/*/; do
    [ -d "$d" ] || continue
    name="$(basename "$d")"
    rm -rf "$target/$name"
    cp -R "$d" "$target/$name"
    echo "synced -> $target/$name"
  done
done
echo "Done. Restart/reload Cursor sessions to pick up new skills."
