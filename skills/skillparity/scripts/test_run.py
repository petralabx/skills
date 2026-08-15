#!/usr/bin/env python3
"""Unit tests for skillparity source resolution."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import run as skillparity


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _init_repo(root: Path, origin: str | None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "skills").mkdir()
    _git(root, "init")
    if origin:
        _git(root, "remote", "add", "origin", origin)
    return root


class SourceResolutionTests(unittest.TestCase):
    def test_rejects_non_git_parent_with_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_home_cursor = Path(tmp) / ".cursor"
            (fake_home_cursor / "skills").mkdir(parents=True)
            self.assertFalse(skillparity.is_petralabx_skills_repo(fake_home_cursor))
            source, note = skillparity.find_skills_source(
                containing=fake_home_cursor,
                candidates=(),
            )
            self.assertIsNone(source)
            self.assertIn("petralabx/skills", note)

    def test_rejects_empty_origin_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_repo(Path(tmp) / "no-origin", origin=None)
            self.assertEqual(skillparity.origin_slug(repo), "")
            self.assertFalse(skillparity.is_petralabx_skills_repo(repo))

    def test_rejects_legacy_plx_cursor_skills_origin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_repo(
                Path(tmp) / "legacy",
                origin="https://github.com/taylorvalton/plx-cursor-skills.git",
            )
            self.assertFalse(skillparity.is_petralabx_skills_repo(repo))

    def test_accepts_petralabx_skills_origin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _init_repo(
                Path(tmp) / "skills-checkout",
                origin="https://github.com/petralabx/skills.git",
            )
            self.assertTrue(skillparity.is_petralabx_skills_repo(repo))
            source, note = skillparity.find_skills_source(containing=repo)
            self.assertEqual(source, repo)
            self.assertEqual(note, "skill checkout containing skillparity")

    def test_rejects_dest_overlapping_source(self) -> None:
        home_cursor = Path.home() / ".cursor"
        self.assertTrue(skillparity.source_overlaps_dest(home_cursor))
        self.assertFalse(skillparity.is_petralabx_skills_repo(home_cursor))

    def test_prefers_checkout_that_contains_skillparity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            older = _init_repo(
                Path(tmp) / "older",
                origin="https://github.com/petralabx/skills.git",
            )
            newer = _init_repo(
                Path(tmp) / "newer",
                origin="https://github.com/petralabx/skills.git",
            )
            (newer / "skills" / "skillparity").mkdir()
            (newer / "skills" / "skillparity" / "SKILL.md").write_text(
                "# skillparity\n",
                encoding="utf-8",
            )
            source, _note = skillparity.find_skills_source(
                containing=Path(tmp) / "not-a-repo",
                candidates=(older, newer),
            )
            self.assertEqual(source, newer)


if __name__ == "__main__":
    unittest.main()
