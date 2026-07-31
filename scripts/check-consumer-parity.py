#!/usr/bin/env python3
"""Compare catalog skills with a consumer repository's project skill copies."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files_below(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


def git_root(path: Path) -> Path | None:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def git_index_modes(repo: Path | None) -> dict[str, str]:
    if repo is None:
        return {}
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--stage", "-z"],
        capture_output=True,
    )
    if result.returncode != 0:
        return {}
    modes: dict[str, str] = {}
    for record in result.stdout.decode("utf-8").split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        modes[path] = metadata.split(" ", 1)[0]
    return modes


def package_skill_ids(manifest: Path, package_id: str) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    package = next(
        (item for item in data.get("packages", []) if item.get("id") == package_id),
        None,
    )
    if package is None:
        raise ValueError(f"package not found in {manifest}: {package_id}")
    return list(package.get("skillIds", []))


def compare_skill(
    source: Path,
    consumer: Path,
    skill_id: str,
    source_repo: Path | None,
    consumer_repo: Path | None,
    source_modes: dict[str, str],
    consumer_modes: dict[str, str],
) -> list[str]:
    source_dir = source / skill_id
    consumer_dir = consumer / ".cursor" / "skills" / skill_id
    if not source_dir.is_dir():
        return [f"{skill_id}: source directory missing: {source_dir}"]
    if not consumer_dir.is_dir():
        return [f"{skill_id}: consumer directory missing: {consumer_dir}"]

    source_files = files_below(source_dir)
    consumer_files = files_below(consumer_dir)
    problems = [
        f"{skill_id}: consumer file missing: {relative}"
        for relative in sorted(source_files.keys() - consumer_files.keys())
    ]
    problems.extend(
        f"{skill_id}: unexpected consumer file: {relative}"
        for relative in sorted(consumer_files.keys() - source_files.keys())
    )
    problems.extend(
        f"{skill_id}: content differs: {relative}"
        for relative in sorted(source_files.keys() & consumer_files.keys())
        if digest(source_files[relative]) != digest(consumer_files[relative])
    )
    for relative in sorted(source_files.keys() & consumer_files.keys()):
        if source_repo is None:
            continue
        source_path = source_files[relative].resolve().relative_to(source_repo).as_posix()
        source_mode = source_modes.get(source_path)
        if source_mode is None:
            continue
        if consumer_repo is None:
            problems.append(f"{skill_id}: consumer is not a Git checkout: {relative}")
            continue
        consumer_path = (
            consumer_files[relative].resolve().relative_to(consumer_repo).as_posix()
        )
        consumer_mode = consumer_modes.get(consumer_path)
        if consumer_mode is None:
            problems.append(f"{skill_id}: consumer file is not tracked: {relative}")
        elif consumer_mode != source_mode:
            problems.append(
                f"{skill_id}: mode differs: {relative} "
                f"(source {source_mode}, consumer {consumer_mode})"
            )
    return problems


def run_check(
    source: Path, consumer: Path, manifest: Path, package_id: str, skill_ids: list[str]
) -> int:
    selected = skill_ids or package_skill_ids(manifest, package_id)
    source_repo = git_root(source)
    consumer_repo = git_root(consumer)
    source_modes = git_index_modes(source_repo)
    consumer_modes = git_index_modes(consumer_repo)
    problems = [
        problem
        for skill_id in selected
        for problem in compare_skill(
            source,
            consumer,
            skill_id,
            source_repo,
            consumer_repo,
            source_modes,
            consumer_modes,
        )
    ]
    if problems:
        print("consumer skill parity failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"consumer skill parity passed: {len(selected)} skill(s)")
    return 0


def selftest() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "catalog" / "skills"
        consumer = root / "consumer"
        manifest = root / "catalog" / "manifest.json"
        source_skill = source / "demo"
        consumer_skill = consumer / ".cursor" / "skills" / "demo"
        source_skill.mkdir(parents=True)
        consumer_skill.mkdir(parents=True)
        (source_skill / "SKILL.md").write_text("canonical\n", encoding="utf-8")
        (source_skill / "reference.md").write_text("reference\n", encoding="utf-8")
        (source_skill / "run.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        (consumer_skill / "SKILL.md").write_text("stale\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "packages": [
                        {"id": "plx-engineering-core", "skillIds": ["demo"]}
                    ]
                }
            ),
            encoding="utf-8",
        )
        for repo in (root / "catalog", consumer):
            subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root / "catalog"),
                "update-index",
                "--chmod=+x",
                "skills/demo/run.sh",
            ],
            check=True,
        )

        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--source-root",
            str(source),
            "--consumer-root",
            str(consumer),
            "--manifest",
            str(manifest),
        ]
        red = subprocess.run(command, capture_output=True, text=True)
        print(f"selftest RED exit={red.returncode}")
        if red.returncode != 1 or "content differs" not in red.stderr:
            print(red.stdout, end="")
            print(red.stderr, end="", file=sys.stderr)
            print("selftest failed: stale consumer did not fail as expected", file=sys.stderr)
            return 1

        shutil.rmtree(consumer_skill)
        shutil.copytree(source_skill, consumer_skill)
        subprocess.run(["git", "-C", str(consumer), "add", "-A"], check=True)
        mode_red = subprocess.run(command, capture_output=True, text=True)
        print(f"selftest MODE_RED exit={mode_red.returncode}")
        if mode_red.returncode != 1 or "mode differs" not in mode_red.stderr:
            print(mode_red.stdout, end="")
            print(mode_red.stderr, end="", file=sys.stderr)
            print(
                "selftest failed: non-executable consumer did not fail as expected",
                file=sys.stderr,
            )
            return 1

        subprocess.run(
            [
                "git",
                "-C",
                str(consumer),
                "update-index",
                "--chmod=+x",
                ".cursor/skills/demo/run.sh",
            ],
            check=True,
        )
        green = subprocess.run(command, capture_output=True, text=True)
        print(f"selftest GREEN exit={green.returncode}")
        if green.returncode != 0:
            print(green.stdout, end="")
            print(green.stderr, end="", file=sys.stderr)
            print("selftest failed: synced consumer did not pass", file=sys.stderr)
            return 1

    print("consumer parity selftest passed")
    return 0


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=repo_root / "skills")
    parser.add_argument("--consumer-root", type=Path)
    parser.add_argument("--manifest", type=Path, default=repo_root / "manifest.json")
    parser.add_argument("--package-id", default="plx-engineering-core")
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    if args.consumer_root is None:
        parser.error("--consumer-root is required unless --selftest is used")
    try:
        return run_check(
            args.source_root,
            args.consumer_root,
            args.manifest,
            args.package_id,
            args.skill,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"consumer skill parity error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
