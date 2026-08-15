#!/usr/bin/env python3
"""Detect the PLX skills install plane for this runtime/machine and apply it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILLS_REPO = SKILL_DIR.parents[1]
HOME = Path.home()

OPERATOR_SYNC_TARGETS = (
    HOME / ".cursor" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".grok" / "skills",
    HOME / ".agents" / "skills",
    HOME / ".hermes" / "skills",
)

CANARIES = ("skillparity", "grill-with-docs")


def env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def is_cursor_cloud() -> bool:
    if Path("/agent/repos").is_dir():
        return True
    return any(
        os.environ.get(key)
        for key in (
            "CLOUD_AGENT_WORKSPACE_ROOT",
            "CLOUD_AGENT_DEPENDENCY_WORKSPACE",
            "CURSOR_CLOUD_AGENT",
        )
    )


def detect_runtime() -> str:
    if is_cursor_cloud():
        return "cursor-cloud"
    # Cursor session vars beat a machine that also has Hermes/Grok installed.
    if os.environ.get("CURSOR_TRACE_ID") or os.environ.get("CURSOR_AGENT"):
        return "cursor"
    if env_truthy("CLAUDECODE") or os.environ.get("CLAUDE_CODE"):
        return "claude"
    if os.environ.get("HERMES_HOME") or "hermes" in os.environ.get("TERM_PROGRAM", "").lower():
        return "hermes"
    if (HOME / ".cursor").is_dir():
        return "cursor"
    return "unknown"


def detect_machine() -> str:
    if is_cursor_cloud():
        return "cursor-cloud-vm"
    signals = [
        HOME.name.lower() == "vince",
        (HOME / "agentic-swarm").is_dir(),
        (HOME / ".hermes").is_dir(),
        (HOME / ".grok").is_dir(),
    ]
    if any(signals):
        return "operator-workstation"
    return "contributor-laptop"


def choose_plane(runtime: str, machine: str) -> tuple[str, str]:
    if machine == "cursor-cloud-vm" or runtime == "cursor-cloud":
        return "cloud-lock", "Cursor Cloud environment detected."
    if machine == "operator-workstation":
        return (
            "operator-sync",
            "Operator workstation signals present; sync all five home skill dirs.",
        )
    return (
        "company-bootstrap",
        "Contributor laptop; install the PLX_MC-pinned company catalog into Cursor and Claude.",
    )


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def origin_slug(repo: Path) -> str:
    result = git(repo, "config", "--get", "remote.origin.url")
    if result.returncode != 0:
        return ""
    url = result.stdout.strip().replace("\\", "/")
    for prefix in ("https://github.com/", "git@github.com:"):
        if prefix in url:
            slug = url.split(prefix, 1)[1]
            return slug.removesuffix(".git")
    return url


def first_existing(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.is_dir():
            return path
    return None


def find_skills_source() -> tuple[Path | None, str]:
    if (SKILLS_REPO / "skills").is_dir() and origin_slug(SKILLS_REPO) in {
        "petralabx/skills",
        "",
    }:
        return SKILLS_REPO, "skill checkout containing skillparity"
    candidates = [
        HOME / "petra-lab-x-skills",
        HOME / ".cursor" / "worktrees" / "skills-skillparity",
        HOME / ".cursor" / "worktrees" / "skills-parity-sync",
        Path("/agent/repos/skills"),
        HOME / "plx-cursor-skills",
    ]
    for path in candidates:
        if not (path / "skills").is_dir():
            continue
        slug = origin_slug(path)
        if slug == "taylorvalton/plx-cursor-skills":
            continue
        if slug in {"petralabx/skills", ""}:
            return path, f"found {path}"
    return None, "no petralabx/skills checkout with a skills/ tree"


def find_plx_mc() -> Path | None:
    return first_existing(
        [
            HOME / "PLX_MC",
            Path("/agent/repos/PLX_MC"),
            SKILLS_REPO.parent / "PLX_MC",
        ]
    )


def find_swarm() -> Path | None:
    return first_existing(
        [
            Path("/agent/repos/agentic-swarm"),
            HOME / "agentic-swarm",
        ]
    )


def copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def apply_operator_sync(source: Path) -> dict:
    src = source / "skills"
    written: list[str] = []
    for target in OPERATOR_SYNC_TARGETS:
        target.mkdir(parents=True, exist_ok=True)
        for skill_dir in sorted(p for p in src.iterdir() if p.is_dir()):
            dest = target / skill_dir.name
            copy_tree(skill_dir, dest)
            written.append(str(dest))
    return {"written": len(written), "targets": [str(p) for p in OPERATOR_SYNC_TARGETS]}


def apply_company_bootstrap(plx_mc: Path) -> dict:
    if os.name == "nt":
        script = plx_mc / "scripts" / "bootstrap-company-skills.ps1"
        cmd = ["powershell", "-NoProfile", "-File", str(script)]
    else:
        script = plx_mc / "scripts" / "bootstrap-company-skills.sh"
        cmd = ["bash", str(script)]
    if not script.is_file():
        raise FileNotFoundError(f"bootstrap script missing: {script}")
    result = subprocess.run(cmd, cwd=str(plx_mc), text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"bootstrap exited {result.returncode}")
    return {"command": cmd, "cwd": str(plx_mc)}


def apply_cloud_lock(swarm: Path) -> dict:
    script = swarm / "scripts" / "install-cloud-agent-skills.sh"
    if not script.is_file():
        raise FileNotFoundError(f"cloud installer missing: {script}")
    result = subprocess.run(["bash", str(script)], cwd=str(swarm), text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"cloud lock installer exited {result.returncode}")
    return {"command": [str(script)], "cwd": str(swarm)}


def canaries() -> dict[str, dict[str, bool]]:
    report: dict[str, dict[str, bool]] = {}
    for target in OPERATOR_SYNC_TARGETS:
        report[str(target)] = {
            name: (target / name / "SKILL.md").is_file() for name in CANARIES
        }
    return report


def catalog_pin(plx_mc: Path | None) -> dict[str, str]:
    if plx_mc is None:
        return {}
    catalog = plx_mc / "config" / "skills-catalog.json"
    if not catalog.is_file():
        return {}
    try:
        data = json.loads(catalog.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {
        "pinTag": data.get("pinTag") or "",
        "pinSha": data.get("pinSha") or "",
        "sourceRepo": data.get("sourceRepo") or "",
        "catalogPath": str(catalog),
    }


def build_plan() -> dict:
    runtime = detect_runtime()
    machine = detect_machine()
    plane, reason = choose_plane(runtime, machine)
    skills_source, source_note = find_skills_source()
    plx_mc = find_plx_mc()
    swarm = find_swarm()
    blockers: list[str] = []
    if plane == "operator-sync" and skills_source is None:
        blockers.append(source_note)
    if plane == "company-bootstrap" and plx_mc is None:
        blockers.append("PLX_MC checkout not found")
    if plane == "cloud-lock" and swarm is None:
        blockers.append("agentic-swarm checkout not found for cloud lock installer")
    if plane == "cloud-lock" and skills_source is None:
        blockers.append(
            "petralabx/skills is not a sibling checkout; attach it to the Cloud environment"
        )
    head = ""
    if skills_source is not None:
        head_result = git(skills_source, "rev-parse", "--short", "HEAD")
        if head_result.returncode == 0:
            head = head_result.stdout.strip()
    return {
        "runtime": runtime,
        "machine": machine,
        "plane": plane,
        "reason": reason,
        "skillsSource": str(skills_source) if skills_source else None,
        "skillsSourceNote": source_note,
        "skillsHead": head,
        "plxMc": str(plx_mc) if plx_mc else None,
        "swarm": str(swarm) if swarm else None,
        "pin": catalog_pin(plx_mc),
        "blockers": blockers,
        "newSessionRequired": True,
    }


def apply(plan: dict) -> dict:
    plane = plan["plane"]
    if plane == "operator-sync":
        return apply_operator_sync(Path(plan["skillsSource"]))
    if plane == "company-bootstrap":
        return apply_company_bootstrap(Path(plan["plxMc"]))
    if plane == "cloud-lock":
        return apply_cloud_lock(Path(plan["swarm"]))
    raise RuntimeError(f"unknown plane: {plane}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detect-only", action="store_true")
    args = parser.parse_args()
    plan = build_plan()
    if args.detect_only:
        plan["canaries"] = canaries()
        print(json.dumps(plan, indent=2))
        return 1 if plan["blockers"] else 0
    if plan["blockers"]:
        plan["applied"] = False
        plan["canaries"] = canaries()
        print(json.dumps(plan, indent=2))
        return 2
    try:
        plan["result"] = apply(plan)
        plan["applied"] = True
    except Exception as exc:  # noqa: BLE001 - surface the install failure
        plan["applied"] = False
        plan["error"] = str(exc)
        plan["canaries"] = canaries()
        print(json.dumps(plan, indent=2))
        return 1
    plan["canaries"] = canaries()
    print(json.dumps(plan, indent=2))
    print("Start a new session to load the skills.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
