#!/usr/bin/env bash
# Sync Petra-Lab-X skills into local global skill directories for Cursor, Claude,
# Grok, Hermes, and .agents. Idempotent: pulls latest, then replaces each
# ~/.cursor/skills/<name>, ~/.claude/skills/<name>, ~/.grok/skills/<name>,
# ~/.agents/skills/<name>, and ~/.hermes/skills/<name> with this repo's version.
#
# git pull --ff-only is fail-closed: a dirty or diverged clone must not silently
# install a stale catalog.
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
git -C "$repo_root" pull --ff-only
src="$repo_root/skills"
[ -d "$src" ] || { echo "No skills/ directory in $repo_root"; exit 1; }

for target in \
  "$HOME/.cursor/skills" \
  "$HOME/.claude/skills" \
  "$HOME/.grok/skills" \
  "$HOME/.agents/skills" \
  "$HOME/.hermes/skills"
do
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
