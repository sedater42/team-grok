from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
RUNNER_PATH = ROOT / "skills" / "team-grok" / "scripts" / "run_grok.py"
SPEC = importlib.util.spec_from_file_location("team_grok_package_runner", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class TeamGrokPackageTests(unittest.TestCase):
    def test_release_versions_and_license_are_coherent(self) -> None:
        plugin = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        compatibility = json.loads((ROOT / "compatibility.json").read_text())
        self.assertEqual(plugin["version"], runner.RUNNER_VERSION)
        self.assertEqual(compatibility["team_grok_version"], runner.RUNNER_VERSION)
        self.assertEqual(plugin["license"], "Apache-2.0")
        self.assertTrue((ROOT / "LICENSE").is_file())

    def test_optional_luna_agent_is_exactly_identity_pinned(self) -> None:
        agent = (ROOT / "codex-agents" / "team-grok-luna-worker.toml").read_text()
        self.assertIn('name = "team_grok_luna_worker"', agent)
        self.assertIn('model = "gpt-5.6-luna"', agent)
        self.assertIn('model_reasoning_effort = "xhigh"', agent)

    def test_required_publication_files_exist(self) -> None:
        required = (
            "README.md", "LICENSE", "NOTICE", "SECURITY.md", "CHANGELOG.md",
            "CONTRIBUTING.md", "compatibility.json", "docs/privacy.md",
            "docs/threat-model.md", "docs/support-matrix.md", ".github/workflows/ci.yml",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_repository_contains_no_personal_absolute_paths(self) -> None:
        offenders = []
        personal_prefix = "/" + "Users" + "/"
        private_temp_prefix = "/" + "private" + "/var/folders/"
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path.suffix == ".pyc":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if personal_prefix in text or private_temp_prefix in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_publication_metadata_contains_no_personal_identity(self) -> None:
        plugin = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["author"]["name"], "Team Grok Contributors")
        self.assertEqual(plugin["interface"]["developerName"], "Team Grok Contributors")

        forbidden = (
            "Jacob" + " Hantla",
            "jacob" + "hantla",
            "/" + "Users" + "/",
        )
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path.suffix == ".pyc":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for value in forbidden:
                self.assertNotIn(value, text, f"personal identifier in {path}")


if __name__ == "__main__":
    unittest.main()
