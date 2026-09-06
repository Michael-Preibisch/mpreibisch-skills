import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/mpreibisch-codex"
SPEC = importlib.util.spec_from_file_location("runner", PLUGIN / "scripts/cross_model.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cross-model-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace with spaces"
        self.workspace.mkdir()
        self.request = runner.read_json(PLUGIN / "bridge/request.example.json")
        self.request["scope"]["workspace"] = str(self.workspace)
        self.response = {"status": "complete", "summary": "No request IDs found in the supplied scope.",
                         "evidence": [], "uncertainties": ["Input code was not supplied."],
                         "observations": [], "recommendations": [],
                         "coverage": "Supplied input only.", "artifact": "No call path can be verified."}

    def test_every_context_field_is_required(self):
        for key in self.request["context"]:
            for invalid in (None, "", "   "):
                request = copy.deepcopy(self.request)
                if invalid is None:
                    del request["context"][key]
                else:
                    request["context"][key] = invalid
                with self.subTest(key=key, invalid=invalid), self.assertRaises(ValueError):
                    runner.prepare(request)

    def test_read_only_rejects_writes_commands_and_external_effects(self):
        for field, value in [("write_paths", ["src"]), ("external_side_effects", ["Push a branch"])]:
            request = copy.deepcopy(self.request)
            request["scope"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                runner.prepare(request)
        self.request["task"]["verification_commands"] = ["pytest"]
        with self.assertRaises(ValueError):
            runner.prepare(self.request)

    def test_implementation_requires_write_scope(self):
        self.request["skill"] = "delegate-implement"
        with self.assertRaises(ValueError):
            runner.prepare(self.request)
        self.request["scope"]["write_paths"] = ["src/input", "tests/input"]
        self.request["task"]["verification_commands"] = ["python3 -m unittest discover -s tests/input"]
        self.assertTrue(runner.prepare(self.request)[1])

    def test_rejects_traversal_absolute_and_symlink_escape(self):
        for path in ("../outside", str(self.root), "src/**"):
            self.request["scope"]["read_paths"] = [path]
            with self.subTest(path=path), self.assertRaises(ValueError):
                runner.prepare(self.request)
        if os.name != "nt":
            (self.workspace / "escape").symlink_to(self.root, target_is_directory=True)
            self.request["scope"]["read_paths"] = ["escape"]
            with self.assertRaises(ValueError):
                runner.prepare(self.request)

    def test_verification_rules_cannot_inject_shell_or_permission_patterns(self):
        self.request["skill"] = "delegate-implement"
        self.request["scope"]["write_paths"] = ["src"]
        for command in ("pytest; git push", "pytest && deploy", "pytest $(whoami)",
                        "pytest *", "pytest),Bash(*)", "pytest\nrm -rf tmp"):
            self.request["task"]["verification_commands"] = [command]
            with self.subTest(command=command), self.assertRaises(ValueError):
                runner.prepare(self.request)

    def test_consensus_initial_independence_and_default_round_cap(self):
        self.request["skill"] = "consensus"
        self.request["exchange"]["phase"] = "assess"
        del self.request["exchange"]["max_rounds"]
        runner.prepare(self.request)
        self.assertEqual(self.request["exchange"]["max_rounds"], 3)
        self.request["exchange"]["candidate_conclusion"] = "The caller prefers A."
        with self.assertRaises(ValueError):
            runner.prepare(self.request)

    def position(self, agent):
        return {"agent": agent, "conclusion": "Use A.", "assumptions": [], "evidence_ids": [],
                "confidence": "medium", "alternatives": [], "disagreements": [], "changed_beliefs": []}

    def test_consensus_exchange_bounds_and_attribution(self):
        self.request["skill"] = "consensus"
        self.request["exchange"].update(phase="exchange", round=1,
                                         positions=[self.position("codex"), self.position("claude")])
        runner.prepare(self.request)
        for value in (0, 4, True):
            self.request["exchange"]["round"] = value
            with self.subTest(round=value), self.assertRaises(ValueError):
                runner.prepare(self.request)
        self.request["exchange"]["round"] = 1
        self.request["exchange"]["positions"] = [self.position("codex")]
        with self.assertRaises(ValueError):
            runner.prepare(self.request)

    def test_unearned_consensus_endorsement_is_rejected(self):
        self.request["skill"] = "consensus"
        self.request["exchange"].update(phase="exchange", round=1, candidate_conclusion="Use A.")
        schema = runner.read_json(PLUGIN / "bridge/responses/consensus.schema.json")
        response = {"status": "complete", "summary": "Agreed", "evidence": [], "uncertainties": [],
                    "position": self.position("claude"), "agrees_with_candidate": True,
                    "candidate_conclusion": "Use B."}
        with self.assertRaises(ValueError):
            runner.validate_response(response, schema, self.request, "claude")
        response["candidate_conclusion"] = "Use A."
        runner.validate_response(response, schema, self.request, "claude")
        response["position"]["disagreements"] = [{"id": "D1", "claim": "A fails.",
            "rationale": "A loses state.", "evidence_ids": [], "resolution_needed": "Resolve state loss.", "material": True}]
        with self.assertRaises(ValueError):
            runner.validate_response(response, schema, self.request, "claude")

    def test_evidence_references_must_resolve(self):
        self.response["observations"] = [{"claim": "A thing happened.", "evidence_ids": ["missing"]}]
        with self.assertRaises(ValueError):
            runner.validate_response(self.response, runner.read_json(PLUGIN / "bridge/responses/delegate-explore.schema.json"), self.request, "claude")

    def test_command_permissions_and_explicit_model(self):
        schema = PLUGIN / "bridge/responses/delegate-explore.schema.json"
        claude = runner.build_command("claude", self.request, self.root, schema)
        self.assertIn("Read,Glob,Grep", claude)
        self.assertIn("dontAsk", claude)
        self.assertNotIn("Bash", claude[claude.index("--tools") + 1])
        codex = runner.build_command("codex", self.request, self.root, schema, "user-chosen-model")
        self.assertEqual(codex[codex.index("--sandbox") + 1], "read-only")
        self.assertEqual(codex[codex.index("--model") + 1], "user-chosen-model")
        self.assertIn("never", codex)
        self.assertIn("--ignore-user-config", codex)
        self.request["skill"] = "delegate-implement"
        self.request["task"]["verification_commands"] = ["pytest tests/input"]
        impl = runner.build_command("claude", self.request, self.root, schema)
        self.assertIn("Bash(pytest tests/input)", impl[impl.index("--allowedTools") + 1])
        impl = runner.build_command("codex", self.request, self.root, schema)
        self.assertEqual(impl[impl.index("--sandbox") + 1], "workspace-write")

    def invoke_stub(self, host, behavior="success", status="complete", timeout=10):
        if os.name == "nt":
            self.skipTest("Executable stub scripts use a POSIX shebang; request tests are portable.")
        binary_dir = self.root / (host + "-bin")
        binary_dir.mkdir(exist_ok=True)
        target = "claude" if host == "codex" else "codex"
        stub = binary_dir / target
        response = {**self.response, "status": status}
        stub.write_text("#!" + sys.executable + "\n" +
            "import json,sys,time\nfrom pathlib import Path\n" +
            "prompt=sys.stdin.read()\n" +
            "Path(" + repr(str(self.root / "received.txt")) + ").write_text(prompt)\n" +
            ("time.sleep(30)\n" if behavior == "timeout" else "") +
            ("sys.exit(7)\n" if behavior == "exit" else "") +
            "response=" + repr(response) + "\n" +
            ("print('not json')\n" if behavior == "malformed" else
             "print(json.dumps({'is_error':" + repr(behavior == "cli_error") + ", 'structured_output':response}))\n"
             if target == "claude" else
             "Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(json.dumps(response))\n"),
            encoding="utf-8")
        stub.chmod(0o700)
        request_file = self.root / "request.json"
        runner.write_json(request_file, self.request)
        output = self.root / (host + "-" + behavior + "-" + status)
        env = {**os.environ, "PATH": str(binary_dir) + os.pathsep + os.environ.get("PATH", "")}
        result = subprocess.run([sys.executable, str(ROOT / "plugins" / ("mpreibisch-" + host) / "scripts/cross_model.py"),
                                 "--request", str(request_file), "--output-dir", str(output),
                                 "--timeout", str(timeout)], capture_output=True, text=True, env=env, timeout=15)
        return result, output

    def test_both_cli_transports_deliver_context_and_extract_json(self):
        for host in ("codex", "claude"):
            with self.subTest(host=host):
                result, output = self.invoke_stub(host)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(runner.read_json(output / "response.json"), self.response)
                received = (self.root / "received.txt").read_text()
                for value in self.request["context"].values():
                    self.assertIn(value, received)
                self.assertEqual(output.stat().st_mode & 0o077, 0)

    def test_cli_failures_never_produce_success(self):
        for behavior in ("exit", "malformed", "cli_error"):
            with self.subTest(behavior=behavior):
                result, output = self.invoke_stub("codex", behavior)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((output / "response.json").exists())

    def test_blocked_peer_response_is_preserved_with_nonzero_exit(self):
        result, output = self.invoke_stub("codex", status="blocked")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(runner.read_json(output / "response.json")["status"], "blocked")

    def test_timeout_leaves_failure_artifact(self):
        result, output = self.invoke_stub("codex", "timeout", timeout=1)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(runner.read_json(output / "failure.json")["status"], "incomplete")

    def test_output_directory_cannot_overwrite_or_enter_workspace(self):
        request_file = self.root / "request.json"
        runner.write_json(request_file, self.request)
        for output in (self.root, self.workspace / "scratch"):
            result = subprocess.run([sys.executable, str(PLUGIN / "scripts/cross_model.py"),
                "--request", str(request_file), "--output-dir", str(output), "--dry-run"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
