from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


RUNNER_PATH = Path(__file__).parents[1] / "scripts" / "run_grok.py"
SKILL_ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("team_grok_runner", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class TeamGrokRunnerTests(unittest.TestCase):
    @staticmethod
    def route_fixture() -> dict:
        return {
            "requested_model": "grok-4.6",
            "requested_effort": "xhigh",
            "config_paths_checked": [],
            "config_fingerprints_before": [],
            "subscription_authenticated": True,
            "authentication_route": "grok.com subscription",
        }

    def test_receipt_requires_exact_success_line_after_heading(self) -> None:
        staged_path = "/tmp/team-grok-stage/workspace/sources/001-source.txt"
        handoff = {
            "embedded_context_files": [{"context_id": "context-file-001"}],
            "staged_context_paths": [{"path": staged_path, "type": "file"}],
        }
        failures = (
            f"I saw - OPENED: {staged_path}\n## Context receipt\nNo receipt.\n",
            f"## Context receipt\n```text\n- OPENED: {staged_path}\n```\n",
            f"## Context receipt\n~~~text\n- OPENED: {staged_path}\n~~~\n",
            f"## Context receipt\n    - OPENED: {staged_path}\n",
            (
                "## Context receipt\n"
                "- EMBEDDED: context-file-001\n"
                f"- OPENED: {staged_path}\n"
                f"- ACCESS DENIED: {staged_path}\n"
            ),
        )
        for value in failures:
            with self.subTest(value=value):
                with self.assertRaises(runner.TeamGrokError):
                    runner.verify_context_receipt({"text": value}, dict(handoff))

        accepted = dict(handoff)
        runner.verify_context_receipt(
            {"text": (
                "## Context receipt\n"
                "- EMBEDDED: context-file-001\n"
                f"- OPENED: {staged_path}\n"
            )},
            accepted,
        )
        self.assertTrue(accepted["context_receipt_success_lines_verified"])

    def test_sanitized_environment_is_allowlisted_and_disables_telemetry(self) -> None:
        source_env = {
            "HOME": "/tmp/example-home",
            "PATH": "/usr/bin:/bin",
            "XAI_API_KEY": "must-not-pass",
            "GROK_CONFIG": "/tmp/config",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://telemetry.example",
            "OPENAI_API_KEY": "must-not-pass",
            "UNRELATED_SECRET": "must-not-pass",
        }
        with mock.patch.dict(os.environ, source_env, clear=True):
            child_env, removed = runner.sanitized_environment()

        self.assertEqual(child_env["HOME"], source_env["HOME"])
        for name in ("XAI_API_KEY", "GROK_CONFIG", "OPENAI_API_KEY", "UNRELATED_SECRET"):
            self.assertNotIn(name, child_env)
        self.assertIn("XAI_API_KEY", removed)
        self.assertIn("GROK_CONFIG", removed)
        self.assertIn("OTEL_EXPORTER_OTLP_ENDPOINT", removed)
        for name in (
            "GROK_MEMORY", "GROK_SUBAGENTS", "GROK_WORKFLOWS",
            "GROK_TELEMETRY_ENABLED", "GROK_TELEMETRY_TRACE_UPLOAD", "GROK_EXTERNAL_OTEL",
        ):
            self.assertEqual(child_env[name], "0")
        with self.assertRaisesRegex(runner.TeamGrokError, "XAI_API_KEY"):
            runner.reject_api_environment(removed)
        runner.reject_api_environment(["GROK_MEMORY", "OTEL_EXPORTER_OTLP_ENDPOINT"])
        with mock.patch.dict(os.environ, {"HOME": "/tmp/home"}, clear=True):
            self.assertEqual(runner.run_environment(False)["GROK_WEB_FETCH"], "0")
            self.assertNotIn("GROK_WEB_FETCH", runner.run_environment(True))

    def test_model_policy_selects_newest_and_rejects_downgrade(self) -> None:
        models = ["grok-4.5", "grok-4.6", "grok-4.7"]
        self.assertEqual(runner.select_subscription_model(models, "auto"), "grok-4.7")
        self.assertEqual(runner.select_subscription_model(models, "grok-4.7"), "grok-4.7")
        with self.assertRaisesRegex(runner.TeamGrokError, "downgrade"):
            runner.select_subscription_model(models, "grok-4.6")

    def test_api_configuration_variants_are_rejected(self) -> None:
        variants = (
            '"api_key" = "secret"\n',
            'model."grok-4.6"."env_key" = "XAI_API_KEY"\n',
            'settings = { "base_url" = "https://api.x.ai" }\n',
            '["model"."grok-4.6"]\nname = "grok-4.6"\n',
            '[[model."grok-4.6"]]\nname = "grok-4.6"\n',
        )
        for content in variants:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                config = Path(directory) / "config.toml"
                config.write_text(content, encoding="utf-8")
                with mock.patch.object(runner, "CONFIG_PATHS", ()):
                    with self.assertRaisesRegex(runner.TeamGrokError, "API/provider"):
                        runner.reject_api_model_overrides([config])

    def test_public_v1_parser_has_no_bash_allow_option(self) -> None:
        help_text = runner.build_parser().format_help()
        self.assertNotIn("--allow ", help_text)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            runner.build_parser().parse_args([
                "run", "--prompt-file", "/tmp/prompt", "--cwd", "/tmp",
                "--no-additional-context", "--allow", "Bash(*)",
            ])

    def test_staging_isolated_generic_and_hash_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory).resolve()
            source = cwd / "source.txt"
            source.write_text("original\n", encoding="utf-8")
            verified = runner.verify_source_paths([source])
            stage_root, stage_cwd, staged, _before = runner.copy_context_sources(cwd, verified)
            try:
                staged_path = Path(staged[0]["path"])
                self.assertEqual(staged_path.parent.name, "sources")
                self.assertEqual(staged[0]["context_id"], "context-001")
                self.assertEqual(staged[0]["sha256"], verified[0]["sha256"])
                staged_path.write_text("candidate\n", encoding="utf-8")
                self.assertEqual(source.read_text(encoding="utf-8"), "original\n")
                self.assertEqual(staged_path.read_text(encoding="utf-8"), "candidate\n")
                self.assertTrue((stage_root / runner.STAGE_MARKER).is_file())
                self.assertEqual(stage_cwd, stage_root / "workspace")
            finally:
                shutil.rmtree(stage_root, ignore_errors=True)

    def test_source_symlinks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            target.write_text("data", encoding="utf-8")
            link = root / "link.txt"
            link.symlink_to(target)
            with self.assertRaisesRegex(runner.TeamGrokError, "symlink"):
                runner.verify_source_paths([link])

            source_dir = root / "tree"
            source_dir.mkdir()
            (source_dir / "escape").symlink_to(target)
            with self.assertRaisesRegex(runner.TeamGrokError, "symlink"):
                runner.verify_source_paths([source_dir])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation requires POSIX")
    def test_nested_fifo_is_rejected_without_opening(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fifo = root / "pipe"
            os.mkfifo(fifo)
            with self.assertRaisesRegex(runner.TeamGrokError, "non-regular"):
                runner.verify_source_paths([root])

    def test_hardlinks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            target.write_text("data", encoding="utf-8")
            link = root / "hardlink.txt"
            os.link(target, link)
            with self.assertRaisesRegex(runner.TeamGrokError, "hard-linked"):
                runner.verify_source_paths([link])
            with self.assertRaisesRegex(runner.TeamGrokError, "hard-linked"):
                runner.read_utf8(link, "Context file")

    def test_sensitive_prompt_context_and_source_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (".env.local", "auth.json", "private.pem"):
                path = root / name
                path.write_text("secret", encoding="utf-8")
                with self.subTest(name=name):
                    with self.assertRaises(runner.TeamGrokError):
                        runner.read_utf8(path, "Context file")
                    with self.assertRaises(runner.TeamGrokError):
                        runner.verify_source_paths([path])

    def test_high_confidence_secret_content_is_rejected_in_ordinary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ordinary.py"
            path.write_text(
                "XAI_" + "API_KEY='" + "xai-" + "abcdefghijklmnopqrstuvwxyz1234567890'\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(runner.TeamGrokError, "high-confidence credential"):
                runner.verify_source_paths([path])
            with self.assertRaisesRegex(runner.TeamGrokError, "high-confidence credential"):
                runner.read_utf8(path, "Context file")

    def test_overlapping_context_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "child.txt"
            child.write_text("data", encoding="utf-8")
            with self.assertRaisesRegex(runner.TeamGrokError, "Overlapping"):
                runner.verify_source_paths([root, child])

    def test_default_and_configured_memory_roots_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            configured = Path(directory) / "codex-home"
            memory_file = configured / "memories" / "raw.md"
            memory_file.parent.mkdir(parents=True)
            memory_file.write_text("private", encoding="utf-8")
            with mock.patch.dict(os.environ, {"CODEX_HOME": str(configured)}, clear=False):
                with self.assertRaisesRegex(runner.TeamGrokError, "raw Codex memory"):
                    runner.verify_source_paths([memory_file])

    def test_effective_prompt_omits_original_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompt = root / "brief.md"
            context = root / "curated.md"
            source = root / "source.txt"
            prompt.write_text("Do the bounded work.", encoding="utf-8")
            context.write_text("Important context.", encoding="utf-8")
            source.write_text("Source data.", encoding="utf-8")
            verified = runner.verify_source_paths([source])
            stage_root, _stage_cwd, staged, _before = runner.copy_context_sources(root, verified)
            effective = None
            try:
                effective, handoff = runner.build_handoff_prompt(
                    prompt, [context], verified, staged, [], []
                )
                text = effective.read_text(encoding="utf-8")
                self.assertNotIn(str(context), text)
                self.assertNotIn(str(source), text)
                self.assertIn("context-file-001", text)
                self.assertEqual(effective.stat().st_mode & 0o777, 0o600)
                self.assertEqual(handoff["embedded_context_files"][0]["path"], str(context))
            finally:
                if effective is not None:
                    effective.unlink(missing_ok=True)
                shutil.rmtree(stage_root, ignore_errors=True)

    def test_stage_inspect_cleanup_and_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "source.txt"
            source.write_text("data", encoding="utf-8")
            verified = runner.verify_source_paths([source])
            stage_root, stage_cwd, _staged, _before = runner.copy_context_sources(root, verified)
            inspected = runner.inspect_stage(stage_cwd)
            self.assertEqual(inspected["status"], "preserved")
            cleaned = runner.cleanup_stage(stage_root)
            self.assertEqual(cleaned["status"], "cleaned")
            self.assertFalse(stage_root.exists())
            with self.assertRaises(runner.TeamGrokError):
                runner.cleanup_stage(root)

    def test_version_parser_and_model_floor(self) -> None:
        self.assertEqual(runner.parse_semver("grok 1.0.5 (abc) [stable]"), (1, 0, 5))
        with self.assertRaisesRegex(runner.TeamGrokError, "older than"):
            runner.select_subscription_model(["grok-4.5"], "auto")

    def test_cli_capability_probe_fails_closed(self) -> None:
        complete = "\n".join(f"      {flag} <VALUE>" for flag in runner.REQUIRED_HELP_FLAGS)
        self.assertEqual(set(runner.verify_cli_help(complete)), runner.REQUIRED_HELP_FLAGS)
        with self.assertRaisesRegex(runner.TeamGrokError, "missing required"):
            runner.verify_cli_help("      --model <MODEL>\n")

    def test_inspect_configuration_schema_drift_fails_closed(self) -> None:
        malformed = {
            "hooks": "ACTIVE BUT NEW SCHEMA",
            "plugins": [],
            "mcpServers": [],
            "lspServers": [],
            "permissions": "ACTIVE",
        }
        completed = subprocess.CompletedProcess(
            ["grok", "inspect", "--json"], 0, stdout=json.dumps(malformed), stderr=""
        )
        with mock.patch.object(runner, "run_command", return_value=completed):
            with self.assertRaisesRegex(runner.TeamGrokError, "incompatible hooks schema"):
                runner.inspect_configuration(
                    Path("/fake/grok"), Path("/tmp"), {}, 30, []
                )

    def test_external_compat_nested_schema_and_unknown_surfaces_fail_closed(self) -> None:
        baseline = {
            "hooks": [], "plugins": [], "mcpServers": [], "lspServers": [],
            "permissions": {"loaded": 0}, "projectInstructions": [],
            "configSources": {"layers": []}, "skills": [],
        }
        cells = (
            {"vendor": "cursor", "surface": "skills", "enabled": "true"},
            {"vendor": "cursor", "surface": "skills", "enabled": 1},
            {"vendor": "cursor", "surface": "skills", "enabled": None},
            {"vendor": "cursor", "surface": "skillsV2", "enabled": True},
        )
        for cell in cells:
            payload = {
                **baseline,
                "externalCompat": {"remoteSettingsLoaded": False, "cells": [cell]},
            }
            completed = subprocess.CompletedProcess(
                ["grok", "inspect", "--json"], 0, stdout=json.dumps(payload), stderr=""
            )
            with self.subTest(cell=cell), mock.patch.object(
                runner, "run_command", return_value=completed
            ), self.assertRaises(runner.TeamGrokError):
                runner.inspect_configuration(Path("/fake/grok"), Path("/tmp"), {}, 30, [])

    def test_external_compat_remote_settings_fail_closed(self) -> None:
        payload = {
            "hooks": [], "plugins": [], "mcpServers": [], "lspServers": [],
            "permissions": {"loaded": 0}, "projectInstructions": [],
            "configSources": {"layers": []}, "skills": [],
            "externalCompat": {"remoteSettingsLoaded": True, "cells": []},
        }
        completed = subprocess.CompletedProcess(
            ["grok", "inspect", "--json"], 0, stdout=json.dumps(payload), stderr=""
        )
        with mock.patch.object(
            runner, "run_command", return_value=completed
        ), self.assertRaisesRegex(runner.TeamGrokError, "remote settings are loaded"):
            runner.inspect_configuration(Path("/fake/grok"), Path("/tmp"), {}, 30, [])

    def test_parse_models_and_exclusive_usage_evidence(self) -> None:
        default, available = runner.parse_models(
            "You are logged in with grok.com.\nDefault model: grok-4.7\n"
            "Available models:\n  * grok-4.7 (default)\n  - grok-4.6\n"
        )
        self.assertEqual(default, "grok-4.7")
        self.assertEqual(available, ["grok-4.7", "grok-4.6"])
        accepted = runner.validate_model_usage(
            {"grok-4.7-build": {"modelCalls": 1}}, "grok-4.7"
        )
        self.assertIn("grok-4.7-build", accepted)
        for invalid in (
            {"grok-4.7-build": {"modelCalls": True}},
            {"grok-4.7-build": {"inputTokens": -1}},
            {"grok-4.7": {"modelCalls": 1}, "grok-4.6": {"modelCalls": 1}},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(runner.TeamGrokError):
                runner.validate_model_usage(invalid, "grok-4.7")

    def test_unsupported_platform_fails_before_binary_execution(self) -> None:
        with mock.patch.object(runner.sys, "platform", "linux"):
            with self.assertRaisesRegex(runner.TeamGrokError, "macOS only"):
                runner.resolve_binary()

    def test_embedded_luna_fallback_is_self_contained_and_identity_pinned(self) -> None:
        fallback = (SKILL_ROOT / "references" / "luna-fallback.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("$team-luna", skill.casefold())
        self.assertIn("model: gpt-5.6-luna", fallback)
        self.assertIn("reasoning_effort: xhigh", fallback)
        self.assertIn("fork_turns: none", fallback)
        self.assertIn("Use one Luna attempt", fallback)

    def test_read_only_lane_contract_with_fake_cli(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompt = root / "brief.md"
            context = root / "context.md"
            source = root / "source.txt"
            prompt.write_text("Review the source.", encoding="utf-8")
            context.write_text("Use exact evidence.", encoding="utf-8")
            source.write_text("data", encoding="utf-8")

            def fake_run(command, _env, _cwd, _timeout, _heartbeat=None):
                self.assertEqual(command[command.index("--model") + 1], "grok-4.6")
                self.assertEqual(command[command.index("--reasoning-effort") + 1], "xhigh")
                self.assertEqual(command[command.index("--sandbox") + 1], "strict")
                self.assertEqual(command[command.index("--tools") + 1], "Read,Grep")
                self.assertIn("--no-subagents", command)
                self.assertIn("--no-memory", command)
                self.assertIn("--no-auto-update", command)
                self.assertIn("--disable-web-search", command)
                effective = Path(command[command.index("--prompt-file") + 1])
                prompt_text = effective.read_text(encoding="utf-8")
                staged = next(
                    line.split("`", 2)[1]
                    for line in prompt_text.splitlines()
                    if line.startswith("- `") and "context-001" in line
                )
                payload = {
                    "stopReason": "end_turn",
                    "modelUsage": {
                        "grok-4.6-build": {"inputTokens": 10, "outputTokens": 5, "modelCalls": 1}
                    },
                    "text": (
                        "Verified result.\n## Context receipt\n"
                        "- EMBEDDED: context-file-001\n"
                        f"- OPENED: {staged}\n"
                    ),
                }
                return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

            args = SimpleNamespace(
                cwd=root,
                prompt_file=prompt,
                context_file=[context],
                context_path=[source],
                no_additional_context=False,
                max_turns=4,
                model="auto",
                mode="read-only",
                writable_path=[],
                must_read_path=[],
                context_complete=True,
                record_dir=root / "records",
                allow_web=False,
                deny=[],
                timeout=30,
            )
            with mock.patch.object(runner, "preflight", return_value=self.route_fixture()), mock.patch.object(
                runner, "run_command", side_effect=fake_run
            ), mock.patch.object(runner, "reject_api_model_overrides", return_value=[]):
                result = runner.run_lane(args, Path("/fake/grok"))
            self.assertEqual(result["team_grok"]["status"], "completed_unaccepted")
            self.assertTrue(result["team_grok"]["handoff"]["context_receipt_success_lines_verified"])
            self.assertFalse(result["team_grok"]["bash_available"])

    def test_workspace_lane_preserves_only_stage_and_cleanup_works(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompt = root / "brief.md"
            source = root / "source.txt"
            prompt.write_text("Edit the source.", encoding="utf-8")
            source.write_text("original", encoding="utf-8")

            def fake_run(command, _env, cwd, _timeout, _heartbeat=None):
                staged = cwd / "sources" / "001-source.txt"
                staged.write_text("candidate", encoding="utf-8")
                payload = {
                    "stopReason": "end_turn",
                    "modelUsage": {"grok-4.6": {"modelCalls": 1}},
                    "text": f"Edited.\n## Context receipt\n- OPENED: {staged}\n",
                }
                return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

            args = SimpleNamespace(
                cwd=root,
                prompt_file=prompt,
                context_file=[],
                context_path=[source],
                no_additional_context=False,
                max_turns=4,
                model="auto",
                mode="workspace",
                writable_path=[source],
                must_read_path=[],
                context_complete=True,
                record_dir=root / "records",
                allow_web=False,
                deny=[],
                timeout=30,
            )
            with mock.patch.object(runner, "preflight", return_value=self.route_fixture()), mock.patch.object(
                runner, "run_command", side_effect=fake_run
            ), mock.patch.object(runner, "reject_api_model_overrides", return_value=[]):
                result = runner.run_lane(args, Path("/fake/grok"))
            stage = Path(result["team_grok"]["staging"]["staged_cwd"])
            try:
                self.assertEqual(source.read_text(encoding="utf-8"), "original")
                self.assertEqual((stage / "sources" / "001-source.txt").read_text(), "candidate")
                self.assertEqual(result["team_grok"]["staging"]["changes"]["modified"], ["sources/001-source.txt"])
            finally:
                runner.cleanup_stage(stage)

    def test_context_completeness_is_required_before_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompt = root / "brief.md"
            prompt.write_text("Self-contained task.", encoding="utf-8")
            args = SimpleNamespace(
                cwd=root,
                prompt_file=prompt,
                context_file=[],
                context_path=[],
                no_additional_context=True,
                max_turns=1,
                model="auto",
                mode="read-only",
                writable_path=[],
                must_read_path=[],
                context_complete=False,
                record_dir=None,
                allow_web=False,
                deny=[],
                timeout=30,
            )
            with self.assertRaisesRegex(runner.TeamGrokError, "context-complete"):
                runner.run_lane(args, Path("/fake/grok"))

    def test_workspace_write_allowlist_rejects_extra_stage_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            writable = root / "writable.txt"
            readonly = root / "readonly.txt"
            writable.write_text("a", encoding="utf-8")
            readonly.write_text("b", encoding="utf-8")
            verified = runner.verify_source_paths([writable, readonly])
            stage_root, stage_cwd, staged, before = runner.copy_context_sources(root, verified)
            try:
                Path(staged[0]["path"]).write_text("changed", encoding="utf-8")
                Path(staged[1]["path"]).write_text("also changed", encoding="utf-8")
                changes = runner.compare_tree_states(before, runner.tree_state(stage_cwd))
                scoped = runner.map_scoped_paths(
                    {str(writable)}, verified, staged, "writable"
                )
                offenders = runner.unexpected_stage_changes(changes, scoped, stage_cwd)
                self.assertEqual(offenders, ["modified:sources/002-readonly.txt"])
            finally:
                shutil.rmtree(stage_root, ignore_errors=True)

    def test_hidden_stage_paths_are_detected_and_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "a.txt"
            source.write_text("a", encoding="utf-8")
            verified = runner.verify_source_paths([source])
            stage_root, stage_cwd, staged, before = runner.copy_context_sources(root, verified)
            try:
                hidden = stage_cwd / ".grok" / "hidden.txt"
                hidden.parent.mkdir()
                hidden.write_text("out of scope", encoding="utf-8")
                changes = runner.compare_tree_states(before, runner.tree_state(stage_cwd))
                scoped = runner.map_scoped_paths(
                    {str(source)}, verified, staged, "writable"
                )
                offenders = runner.unexpected_stage_changes(changes, scoped, stage_cwd)
                self.assertIn("created:.grok", offenders)
                self.assertIn("created:.grok/hidden.txt", offenders)
            finally:
                shutil.rmtree(stage_root, ignore_errors=True)

    def test_durable_proof_status_history_and_immutable_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            records = root / "records"
            run_id = "00000000-0000-0000-0000-000000000001"
            run_dir = runner.prepare_run_record(records, run_id)
            runner.update_run_status(
                run_dir, run_id, "running", started_at_unix=123, heartbeat=True
            )
            runner.update_run_status(run_dir, run_id, "running", heartbeat=True)
            self.assertEqual(
                runner.run_status(run_dir)["status"]["started_at_unix"], 123
            )
            payload = {
                "text": "candidate",
                "team_grok": {
                    "run_id": run_id,
                    "status": "completed_unaccepted",
                    "authentication_route": "grok.com subscription",
                    "requested_model": "grok-4.6",
                    "requested_effort": "xhigh",
                    "mode": "read-only",
                    "handoff": {
                        "context_coverage_attested_by_sol": True,
                        "context_receipt_success_lines_verified": True,
                    },
                    "staging": {
                        "original_sources_unchanged": True,
                        "changes": {"created": [], "modified": [], "deleted": []},
                    },
                },
            }
            runner.write_proof_pack(run_dir, payload)
            runner.update_run_status(run_dir, run_id, "completed_unaccepted")
            self.assertEqual(runner.run_status(run_dir)["status"]["status"], "completed_unaccepted")
            self.assertEqual(len(runner.list_runs(records)["runs"]), 1)
            note = root / "decision-note.md"
            note.write_text("Independent checks passed.", encoding="utf-8")
            decision = runner.record_decision(run_dir, "accepted", note)
            self.assertEqual(decision["decision"], "accepted")
            self.assertEqual(runner.run_status(run_dir)["decision"]["decision"], "accepted")
            with self.assertRaisesRegex(runner.TeamGrokError, "already recorded"):
                runner.record_decision(run_dir, "rejected", None)
            self.assertIn("Sol decision: `accepted`", (run_dir / runner.PROOF_PACK).read_text())

    def test_preflight_failure_is_recorded_before_staging(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompt = root / "brief.md"
            records = root / "records"
            prompt.write_text("Self-contained task.", encoding="utf-8")
            args = SimpleNamespace(
                cwd=root,
                prompt_file=prompt,
                context_file=[],
                context_path=[],
                writable_path=[],
                must_read_path=[],
                no_additional_context=True,
                context_complete=True,
                max_turns=1,
                model="auto",
                mode="read-only",
                record_dir=records,
                allow_web=False,
                deny=[],
                timeout=30,
            )
            with mock.patch.object(
                runner, "preflight", side_effect=runner.TeamGrokError("auth failed")
            ), self.assertRaisesRegex(runner.TeamGrokError, "auth failed"):
                runner.run_lane(args, Path("/fake/grok"))
            history = runner.list_runs(records)["runs"]
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["status"]["status"], "failed")
            self.assertEqual(history[0]["status"]["phase"], "preflight_or_staging")

    def test_binary_resolution_failure_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompt = root / "brief.md"
            records = root / "records"
            prompt.write_text("Self-contained task.", encoding="utf-8")
            args = SimpleNamespace(
                cwd=root, prompt_file=prompt, context_file=[], context_path=[],
                writable_path=[], must_read_path=[], no_additional_context=True,
                context_complete=True, max_turns=1, model="auto", mode="read-only",
                record_dir=records, allow_web=False, deny=[], timeout=30,
            )
            with mock.patch.object(
                runner, "resolve_binary", side_effect=runner.TeamGrokError("binary failed")
            ), self.assertRaisesRegex(runner.TeamGrokError, "binary failed"):
                runner.run_lane(args, None)
            history = runner.list_runs(records)["runs"]
            self.assertEqual(history[0]["status"]["status"], "failed")

    def test_record_directory_must_not_overlap_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "source"
            source.mkdir()
            (source / "data.txt").write_text("data", encoding="utf-8")
            prompt = root / "brief.md"
            prompt.write_text("Review.", encoding="utf-8")
            args = SimpleNamespace(
                cwd=root, prompt_file=prompt, context_file=[], context_path=[source],
                writable_path=[], must_read_path=[], no_additional_context=False,
                context_complete=True, max_turns=1, model="auto", mode="read-only",
                record_dir=source / "records", allow_web=False, deny=[], timeout=30,
            )
            with self.assertRaisesRegex(runner.TeamGrokError, "must not overlap"):
                runner.run_lane(args, Path("/fake/grok"))

    def test_descendant_and_new_workspace_write_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repo = root / "repo"
            repo.mkdir()
            (repo / "src").mkdir()
            editable = repo / "src" / "edit.py"
            readonly = repo / "src" / "read.py"
            new_test = repo / "tests" / "test_new.py"
            editable.write_text("old", encoding="utf-8")
            readonly.write_text("keep", encoding="utf-8")
            verified = runner.verify_source_paths([repo])
            allowed = runner.verify_writable_paths(
                "workspace", [editable, new_test], verified
            )
            stage_root, stage_cwd, staged, before = runner.copy_context_sources(root, verified)
            try:
                scoped = runner.map_scoped_paths(allowed, verified, staged, "writable")
                staged_repo = Path(staged[0]["path"])
                (staged_repo / "src" / "edit.py").write_text("new", encoding="utf-8")
                (staged_repo / "tests").mkdir()
                (staged_repo / "tests" / "test_new.py").write_text("test", encoding="utf-8")
                changes = runner.compare_tree_states(before, runner.tree_state(stage_cwd))
                self.assertEqual(runner.unexpected_stage_changes(changes, scoped, stage_cwd), [])
                (staged_repo / "src" / "read.py").write_text("bad", encoding="utf-8")
                changes = runner.compare_tree_states(before, runner.tree_state(stage_cwd))
                self.assertIn(
                    "modified:sources/001-repo/src/read.py",
                    runner.unexpected_stage_changes(changes, scoped, stage_cwd),
                )
            finally:
                shutil.rmtree(stage_root, ignore_errors=True)

    def test_candidate_diff_uses_anonymous_context_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            original = root / "original.txt"
            staged = root / "staged.txt"
            original.write_text("old\n", encoding="utf-8")
            staged.write_text("new\n", encoding="utf-8")
            patch = runner.candidate_diff([
                {
                    "context_id": "context-001",
                    "source_path": str(original),
                    "path": str(staged),
                    "type": "file",
                }
            ])
            self.assertIn("--- a/context-001", patch)
            self.assertIn("+new", patch)
            self.assertNotIn(str(root), patch)

    def test_decision_rejects_noncompleted_or_unbound_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            records = Path(directory) / "records"
            run_id = "00000000-0000-0000-0000-000000000002"
            run_dir = runner.prepare_run_record(records, run_id)
            runner.write_private_json(run_dir / runner.RUN_RECORD, {"team_grok": {}})
            runner.write_private_json(run_dir / "changes.json", {})
            (run_dir / "diff.patch").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(runner.TeamGrokError, "completed_unaccepted"):
                runner.record_decision(run_dir, "accepted", None)


if __name__ == "__main__":
    unittest.main()
