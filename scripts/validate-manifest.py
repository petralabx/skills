#!/usr/bin/env python3
"""Validate manifest.json against the schema and against skills/ on disk.

The description of a skill lives in two places: SKILL.md frontmatter (read by the
Cursor/Claude agent picker) and manifest.json (read by the PLX Mission Control
skills directory). They are required to be byte-identical, because agents on
different surfaces otherwise get different guidance for the same skill.

Also enforces release hygiene: a change to the catalog or to any skill must bump
manifest.version, and a version that already has a v<version> tag cannot be
reused. Those two facts are checkable while the PR is open, which the old gitRef
reachability check never was — see check_release_hygiene.

Usage:
    python scripts/validate-manifest.py

Exits non-zero and prints every problem found.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "manifest.json")
SCHEMA = os.path.join(REPO, "schemas", "manifest.schema.json")

# A description that is only a YAML block-scalar marker means an extraction step
# copied the marker instead of the folded text. This is how seven descriptions
# were silently reduced to two characters (see PR #11).
BLOCK_SCALAR_MARKERS = {">", ">-", ">+", "|", "|-", "|+"}

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def read_json(path: str, label: str):
    try:
        return json.loads(io.open(path, encoding="utf-8").read())
    except Exception as exc:  # noqa: BLE001 - report any parse failure verbatim
        print(f"FATAL: cannot parse {label}: {exc}", file=sys.stderr)
        sys.exit(2)


def frontmatter(path: str, skill_id: str):
    """Return the parsed YAML frontmatter mapping, or None after recording why."""
    import yaml

    raw = io.open(path, encoding="utf-8").read()
    parts = raw.split("---", 2)
    if len(parts) < 3:
        fail(f"{skill_id}: SKILL.md has no YAML frontmatter delimited by ---")
        return None
    try:
        data = yaml.safe_load(parts[1])
    except Exception as exc:  # noqa: BLE001
        # An unquoted ": " inside a plain scalar is the classic cause here.
        fail(f"{skill_id}: SKILL.md frontmatter is not valid YAML ({type(exc).__name__}): {exc}")
        return None
    if not isinstance(data, dict):
        fail(f"{skill_id}: SKILL.md frontmatter is not a mapping")
        return None
    return data


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", REPO, *args], capture_output=True, text=True, encoding="utf-8"
    )


def check_no_gitref(manifest: dict) -> None:
    """The manifest must not carry a gitRef.

    A file cannot name the commit that contains it: the sha does not exist until
    the commit is made, so any value written here is stale by construction and
    every version bump ships one that lags. This field was stamped by hand and by
    the MC publish flow, and both produced refs that pointed at the tree *before*
    the one they described — a v1.3.1 commit advertised alongside a v1.4.0 tree.

    Provenance now comes from the ref a consumer actually fetched, and releases
    are marked by the v<version> tag this repo pushes on merge.
    """
    if "gitRef" in manifest:
        fail(
            "manifest.json must not contain gitRef. A manifest cannot name its own "
            "commit, so the value is always stale; provenance is the ref the "
            "consumer fetched, and the release marker is the v<version> tag."
        )


def check_release_hygiene(manifest: dict) -> None:
    """Touching the catalog requires a version bump, and versions are single-use.

    Neither fact needs the commit sha, so unlike the gitRef reachability check
    this replaces, both can be decided while the PR is still open.
    """
    if git("rev-parse", "--git-dir").returncode != 0:
        return  # not a git checkout (e.g. extracted tarball)
    if git("rev-parse", "--verify", "origin/main").returncode != 0:
        print("note: no origin/main ref — skipping release hygiene checks")
        return

    version = manifest.get("version", "")

    base_manifest = git("show", "origin/main:manifest.json")
    if base_manifest.returncode == 0:
        try:
            base_version = json.loads(base_manifest.stdout).get("version", "")
        except json.JSONDecodeError:
            base_version = ""

        # Diff the working tree against the merge base, not origin/main...HEAD.
        # The latter only sees committed work, which makes this check silently
        # inert in the case it matters most: an author running it before commit.
        merge_base = git("merge-base", "origin/main", "HEAD").stdout.strip() or "origin/main"
        changed = git("diff", "--name-only", merge_base, "--", "manifest.json", "skills/")
        touched = [line for line in changed.stdout.splitlines() if line.strip()]

        if touched and version and version == base_version:
            fail(
                f"version is still {version} but {len(touched)} catalog file(s) changed "
                f"(e.g. {touched[0]}). Consumers pin by version, so an unbumped release "
                "is invisible to them. Bump manifest.version."
            )
        if version and version != base_version:
            existing = git("rev-parse", "-q", "--verify", f"refs/tags/v{version}")
            if existing.returncode == 0:
                fail(
                    f"v{version} is already tagged at {existing.stdout.strip()[:12]}. A "
                    "released version is immutable — choose the next version instead."
                )


def main() -> int:
    manifest = read_json(MANIFEST, "manifest.json")
    check_no_gitref(manifest)
    check_release_hygiene(manifest)

    try:
        import jsonschema
    except ImportError:
        print("FATAL: jsonschema is required (pip install jsonschema pyyaml)", file=sys.stderr)
        return 2
    try:
        jsonschema.validate(manifest, read_json(SCHEMA, "manifest.schema.json"))
    except jsonschema.ValidationError as exc:
        fail(f"schema: {'/'.join(str(p) for p in exc.absolute_path) or '<root>'}: {exc.message}")

    skills = manifest.get("skills", [])

    ids = [s.get("id") for s in skills]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        fail(f"duplicate skill id in manifest: {dup}")

    for entry in skills:
        sid = entry.get("id", "<missing id>")
        content_path = entry.get("contentPath", "")

        if content_path.rstrip("/").split("/")[-1] != sid:
            fail(f"{sid}: contentPath {content_path!r} does not match the skill id")

        skill_dir = os.path.join(REPO, content_path.replace("/", os.sep).rstrip(os.sep))
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isdir(skill_dir):
            fail(f"{sid}: contentPath directory does not exist: {content_path}")
            continue
        if not os.path.isfile(skill_md):
            fail(f"{sid}: no SKILL.md in {content_path}")
            continue

        manifest_desc = (entry.get("description") or "").strip()
        if manifest_desc in BLOCK_SCALAR_MARKERS:
            fail(
                f"{sid}: manifest description is the literal YAML block-scalar marker "
                f"{manifest_desc!r} — copy the folded text, not the marker"
            )
        elif not manifest_desc:
            fail(f"{sid}: manifest description is empty")

        data = frontmatter(skill_md, sid)
        if data is None:
            continue

        if data.get("name") != sid:
            fail(f"{sid}: SKILL.md frontmatter name is {data.get('name')!r}, expected {sid!r}")

        skill_desc = (data.get("description") or "").strip()
        if not skill_desc:
            fail(f"{sid}: SKILL.md frontmatter description is empty")
        elif skill_desc != manifest_desc:
            fail(
                f"{sid}: description differs between SKILL.md and manifest.json.\n"
                f"      SKILL.md ({len(skill_desc)} chars): {skill_desc[:110]}\n"
                f"      manifest ({len(manifest_desc)} chars): {manifest_desc[:110]}"
            )

    # Every skills/<dir> must be catalogued, or it silently ships to nobody.
    skills_root = os.path.join(REPO, "skills")
    on_disk = {
        d for d in os.listdir(skills_root) if os.path.isdir(os.path.join(skills_root, d))
    }
    for orphan in sorted(on_disk - set(ids)):
        fail(f"skills/{orphan}/ exists on disk but has no manifest.json entry")

    for package in manifest.get("packages", []):
        for sid in package.get("skillIds", []):
            if sid not in ids:
                fail(f"package {package.get('id')}: skillId {sid!r} has no matching skill entry")

    if problems:
        print(f"manifest validation FAILED — {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(
        f"manifest validation passed: {len(skills)} skills, "
        f"version {manifest.get('version')}, descriptions match SKILL.md frontmatter"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
