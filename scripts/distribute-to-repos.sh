#!/usr/bin/env bash
# Distribute plx-engineering-core skills into consumer repos' .cursor/skills/
# so Cursor Cloud's / picker (project-scoped) lists them.
#
# Usage:
#   scripts/distribute-to-repos.sh [--dry-run|--check] [--repos repo1,repo2]
#   SKILLS_DISTRIBUTE_LOCAL_ROOTS=1 scripts/distribute-to-repos.sh
#     # use sibling checkouts under ../<repo> instead of cloning
#
# Default consumer set (excludes agentic-swarm which carries a richer local set,
# skills itself, and test-perms-check scratch):
#   plx-customer-portal (base: staging)
#   PLX_MC (base: main)
#   1hr-after, local-inference, for-and-against, furgenics (base: main)
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
src="$repo_root/skills"
manifest="$repo_root/manifest.json"
org="${SKILLS_DISTRIBUTE_ORG:-petralabx}"
branch="${SKILLS_DISTRIBUTE_BRANCH:-cursor/skills-dist-v162-d767}"
package_version="${SKILLS_DISTRIBUTE_VERSION:-}"
dry_run=0
check_only=0
repos_csv=""
use_local_roots=0
if [[ "${SKILLS_DISTRIBUTE_LOCAL_ROOTS:-0}" == "1" ]]; then
  use_local_roots=1
fi
declare -A BASE_MAP=(
  [plx-customer-portal]=staging
  [PLX_MC]=main
  [1hr-after]=main
  [local-inference]=main
  [for-and-against]=main
  [furgenics]=main
)
# Portal keeps intentional overlays on these package skills (extras + customized
# package files). Other consumers only preserve unexpected consumer-only files.
PORTAL_OVERLAY_SKILLS=(capabilities-deck autonomous-verifier mc-sync)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=1; shift ;;
    --check) check_only=1; shift ;;
    --repos) repos_csv="$2"; shift 2 ;;
    --local-roots) use_local_roots=1; shift ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

[[ -d "$src" ]] || { echo "missing $src" >&2; exit 1; }
[[ -f "$manifest" ]] || { echo "missing $manifest" >&2; exit 1; }
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

if [[ -z "$package_version" ]]; then
  package_version="$(
    "${python_cmd[@]}" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("version", "unknown"))' \
      "$manifest"
  )"
fi

mapfile -t PACKAGE_SKILLS < <(
  "${python_cmd[@]}" -c '
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
pkg = next(p for p in data.get("packages", []) if p.get("id") == "plx-engineering-core")
for skill_id in pkg.get("skillIds", []):
    print(skill_id)
' "$manifest"
)
[[ "${#PACKAGE_SKILLS[@]}" -gt 0 ]] || {
  echo "no skillIds found for plx-engineering-core in $manifest" >&2
  exit 1
}

if [[ -n "$repos_csv" ]]; then
  IFS=',' read -r -a REPOS <<< "$repos_csv"
else
  REPOS=("${!BASE_MAP[@]}")
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

is_portal_overlay_skill() {
  local name="$1"
  local s
  for s in "${PORTAL_OVERLAY_SKILLS[@]}"; do
    [[ "$s" == "$name" ]] && return 0
  done
  return 1
}

# Copy catalog skill into consumer, preserving unexpected consumer-only files
# (and, for portal overlay skills, restoring pre-existing customized package files).
sync_skill_dir() {
  local skill_id="$1"
  local dest_skills="$2"
  local preserve_overlays="$3" # 1 for portal
  local catalog="$src/$skill_id"
  local target="$dest_skills/$skill_id"
  local snap="$workdir/snap-$skill_id"

  [[ -d "$catalog" ]] || {
    echo "catalog skill missing: $catalog" >&2
    return 1
  }

  rm -rf "$snap"
  if [[ -d "$target" ]]; then
    mkdir -p "$snap"
    # Snapshot relative paths + bytes (and modes via cp -a).
    (cd "$target" && tar -cf - .) | (cd "$snap" && tar -xf -)
  fi

  rm -rf "$target"
  mkdir -p "$dest_skills"
  cp -a "$catalog" "$target"

  if [[ ! -d "$snap" ]]; then
    return 0
  fi

  # Restore unexpected consumer-only files always.
  while IFS= read -r -d '' rel; do
    rel="${rel#./}"
    [[ -n "$rel" ]] || continue
    if [[ ! -e "$catalog/$rel" ]]; then
      mkdir -p "$(dirname "$target/$rel")"
      cp -a "$snap/$rel" "$target/$rel"
    elif [[ "$preserve_overlays" -eq 1 ]] && is_portal_overlay_skill "$skill_id"; then
      # Restore customized package files for known portal overlays.
      if ! cmp -s "$snap/$rel" "$catalog/$rel"; then
        mkdir -p "$(dirname "$target/$rel")"
        cp -a "$snap/$rel" "$target/$rel"
      fi
    fi
  done < <(cd "$snap" && find . -type f -print0)
}

write_readme() {
  local dest="$1"
  local repo="$2"
  local base="$3"
  if [[ "$repo" == "plx-customer-portal" ]]; then
    cat > "$dest/.cursor/skills/README.md" <<EOF
# Project skills (synced from petralabx/skills)

These skills are the **plx-engineering-core** package from
[petralabx/skills](https://github.com/petralabx/skills) **v${package_version}**.

Cursor Cloud's "/" skill picker is **project-scoped**: it enumerates
".cursor/skills/" in this repo. User-global "~/.cursor/skills" alone does
not populate "/".

**Branch base:** these project skills ship on **"staging"**, not "master"
("master" is the live-release branch and is stale for the skills pack). If a
checkout of "master" shows no ".cursor/skills/", that is expected — verify
"origin/staging" before concluding anything is missing or opening a re-seed PR.

**Do not edit package skills here as the source of truth.** Update
petralabx/skills, then re-run scripts/distribute-to-repos.sh.

Portal overlays under capabilities-deck/ and autonomous-verifier/, and the
customized mc-sync/SKILL.md, are preserved across syncs.

scripts/audit-skill-metadata.mjs gates the frontmatter of every skill here on
each PR — an unparseable description leaves the skill visible but undescribed,
so the agent silently stops invoking it. See
docs/runbooks/CLOUD-AGENT-ENVIRONMENT.md.

Synced via scripts/distribute-to-repos.sh from petralabx/skills@v${package_version}
on base branch ${base}.
EOF
  else
    cat > "$dest/.cursor/skills/README.md" <<EOF
# Project skills (synced from petralabx/skills)

These skills are the **plx-engineering-core** package from
[petralabx/skills](https://github.com/petralabx/skills) **v${package_version}**.

Cursor Cloud's "/" skill picker is **project-scoped**: it enumerates
".cursor/skills/" in this repo. User-global "~/.cursor/skills" alone does
not populate "/".

**Do not edit skills here as the source of truth.** Update petralabx/skills,
then re-run scripts/distribute-to-repos.sh.

Synced via scripts/distribute-to-repos.sh from petralabx/skills@v${package_version}
on base branch ${base}.
EOF
  fi
}

for repo in "${REPOS[@]}"; do
  base="${BASE_MAP[$repo]:-main}"
  echo "=== $org/$repo (base=$base) ==="
  if [[ "$dry_run" -eq 1 ]]; then
    echo "DRY-RUN: would sync ${#PACKAGE_SKILLS[@]} package skills into $org/$repo:.cursor/skills (branch=$branch)"
    continue
  fi

  dest=""
  if [[ "$use_local_roots" -eq 1 ]]; then
    # Prefer sibling under the multi-root workspace (.. /repos/<name>).
    for candidate in \
      "$repo_root/../$repo" \
      "/agent/repos/$repo" \
      "$PWD/../$repo"; do
      if [[ -d "$candidate/.git" ]]; then
        dest="$(cd "$candidate" && pwd)"
        break
      fi
    done
    [[ -n "$dest" ]] || {
      echo "local root missing for $repo" >&2
      exit 1
    }
    git -C "$dest" fetch origin "$base" --depth 1
    git -C "$dest" checkout -B "$branch" "origin/$base"
  else
    dest="$workdir/$repo"
    gh repo clone "$org/$repo" "$dest" -- --depth 1 --branch "$base"
    git -C "$dest" checkout -B "$branch"
  fi

  if [[ "$check_only" -eq 1 ]]; then
    parity_args=("$repo_root/scripts/check-consumer-parity.py" --consumer-root "$dest")
    if [[ "$repo" == "plx-customer-portal" ]]; then
      parity_args+=(--allow-extra-consumer-files)
      for s in "${PORTAL_OVERLAY_SKILLS[@]}"; do
        parity_args+=(--allow-content-diff-skill "$s")
      done
    fi
    "${python_cmd[@]}" "${parity_args[@]}"
    continue
  fi

  mkdir -p "$dest/.cursor/skills"
  preserve_overlays=0
  if [[ "$repo" == "plx-customer-portal" ]]; then
    preserve_overlays=1
  fi

  for skill_id in "${PACKAGE_SKILLS[@]}"; do
    sync_skill_dir "$skill_id" "$dest/.cursor/skills" "$preserve_overlays"
  done

  write_readme "$dest" "$repo" "$base"

  # Force-add: consumer *.log / similar ignores must not drop catalog fixtures
  # (e.g. vmc-autopilot-oneshot/**/commands.log) or mode parity breaks.
  git -C "$dest" add -f .cursor/skills

  parity_args=("$repo_root/scripts/check-consumer-parity.py" --consumer-root "$dest")
  if [[ "$repo" == "plx-customer-portal" ]]; then
    parity_args+=(--allow-extra-consumer-files)
    for s in "${PORTAL_OVERLAY_SKILLS[@]}"; do
      parity_args+=(--allow-content-diff-skill "$s")
    done
  fi
  "${python_cmd[@]}" "${parity_args[@]}"

  git -C "$dest" add -f .cursor/skills
  if git -C "$dest" diff --cached --quiet; then
    echo "no changes"
    continue
  fi
  git -C "$dest" commit -m "chore(skills): sync plx-engineering-core v${package_version}"
  git -C "$dest" push -u origin "$branch"
  echo "pushed $org/$repo@$branch — open/update PR against $base"
done
