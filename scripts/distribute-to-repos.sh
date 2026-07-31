#!/usr/bin/env bash
# Distribute plx-engineering-core skills into consumer repos' .cursor/skills/
# so Cursor Cloud's / picker (project-scoped) lists them.
#
# Usage:
#   scripts/distribute-to-repos.sh [--dry-run|--check] [--repos repo1,repo2]
#
# Default consumer set (excludes agentic-swarm which carries a richer local set,
# skills itself, and test-perms-check scratch):
#   plx-customer-portal (base: staging)
#   PLX_MC (base: main)
#   1hr-after, local-inference, for-and-against, furgenics (base: main)
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
src="$repo_root/skills"
org="${SKILLS_DISTRIBUTE_ORG:-petralabx}"
branch="${SKILLS_DISTRIBUTE_BRANCH:-chore/cursor-skills-plx-engineering-core}"
dry_run=0
check_only=0
repos_csv=""
declare -A BASE_MAP=(
  [plx-customer-portal]=staging
  [PLX_MC]=main
  [1hr-after]=main
  [local-inference]=main
  [for-and-against]=main
  [furgenics]=main
)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=1; shift ;;
    --check) check_only=1; shift ;;
    --repos) repos_csv="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

[[ -d "$src" ]] || { echo "missing $src" >&2; exit 1; }
[[ "$dry_run" -eq 0 || "$check_only" -eq 0 ]] || {
  echo "--dry-run and --check cannot be combined" >&2
  exit 64
}

python_cmd=()
if command -v python3 >/dev/null 2>&1 && python3 -c "import sys" >/dev/null 2>&1; then
  python_cmd=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -c "import sys" >/dev/null 2>&1; then
  python_cmd=(py -3)
elif command -v python >/dev/null 2>&1 && python -c "import sys" >/dev/null 2>&1; then
  python_cmd=(python)
else
  echo "python3/python is required for consumer parity checks" >&2
  exit 2
fi

if [[ -n "$repos_csv" ]]; then
  IFS=',' read -r -a REPOS <<< "$repos_csv"
else
  REPOS=("${!BASE_MAP[@]}")
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

for repo in "${REPOS[@]}"; do
  base="${BASE_MAP[$repo]:-main}"
  echo "=== $org/$repo (base=$base) ==="
  if [[ "$dry_run" -eq 1 ]]; then
    echo "DRY-RUN: would copy $(ls -1 "$src" | wc -l) skills into $org/$repo:.cursor/skills"
    continue
  fi
  dest="$workdir/$repo"
  gh repo clone "$org/$repo" "$dest" -- --depth 1 --branch "$base"
  if [[ "$check_only" -eq 1 ]]; then
    "${python_cmd[@]}" "$repo_root/scripts/check-consumer-parity.py" \
      --consumer-root "$dest"
    continue
  fi
  git -C "$dest" checkout -B "$branch"
  mkdir -p "$dest/.cursor/skills"
  for d in "$src"/*/; do
    name="$(basename "$d")"
    rm -rf "$dest/.cursor/skills/$name"
    cp -R "$d" "$dest/.cursor/skills/$name"
  done
  "${python_cmd[@]}" "$repo_root/scripts/check-consumer-parity.py" \
    --consumer-root "$dest"
  cat > "$dest/.cursor/skills/README.md" <<EOF
# Project skills (synced from petralabx/skills)

These skills are the **plx-engineering-core** package from
[petralabx/skills](https://github.com/petralabx/skills).

Cursor Cloud's \`/\` skill picker is **project-scoped**: it enumerates
\`.cursor/skills/\` in this repo. User-global \`~/.cursor/skills\` alone does
not populate \`/\`.

**Do not edit skills here as the source of truth.** Update petralabx/skills,
then re-run \`scripts/distribute-to-repos.sh\`.
EOF
  git -C "$dest" add .cursor/skills
  if git -C "$dest" diff --cached --quiet; then
    echo "no changes"
    continue
  fi
  git -C "$dest" commit -m "chore(skills): seed plx-engineering-core into .cursor/skills"
  git -C "$dest" push -u origin "$branch"
  echo "pushed $org/$repo@$branch — open/update PR against $base"
done
