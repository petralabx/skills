#!/usr/bin/env python3
"""Validate manifest.json against the schema and against skills/ on disk.

The description of a skill lives in two places: SKILL.md frontmatter (read by the
Cursor/Claude agent picker) and manifest.json (read by the PLX Mission Control
skills directory). They are required to be byte-identical, because agents on
different surfaces otherwise get different guidance for the same skill.

Also checks that gitRef names a commit reachable from main, since this repo
squash-merges and a PR branch commit never enters main's history.

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


def check_gitref(manifest: dict) -> None:
    """gitRef must name a commit reachable from main.

    This repo squash-merges, so a PR branch commit never enters main's history.
    gitRef once pointed at one (2ffc785), leaving the published provenance
    pointer unresolvable from a fresh clone until PR #12 corrected it.
    """
    ref = manifest.get("gitRef")
    if not ref:
        return

    if git("rev-parse", "--git-dir").returncode != 0:
        return  # not a git checkout (e.g. extracted tarball); nothing to verify
    if git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        print("note: shallow clone — skipping gitRef reachability check")
        return
    if git("cat-file", "-e", ref + "^{commit}").returncode != 0:
        fail(f"gitRef {ref[:12]} is not a commit in this repository")
        return

    for base in ("origin/main", "main"):
        if git("rev-parse", "--verify", base).returncode != 0:
            continue
        if git("merge-base", "--is-ancestor", ref, base).returncode != 0:
            fail(
                f"gitRef {ref[:12]} is not reachable from {base}. This repo "
                "squash-merges, so a PR branch commit never enters main's history — "
                "stamp the squash commit instead."
            )
        return

    print("note: no local main ref — skipping gitRef reachability check")


def main() -> int:
    manifest = read_json(MANIFEST, "manifest.json")
    check_gitref(manifest)

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
