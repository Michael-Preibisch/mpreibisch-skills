import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (ROOT / "plugins/mpreibisch-codex", ROOT / "plugins/mpreibisch-claude")
SPEC = importlib.util.spec_from_file_location("validate", ROOT / "scripts/validate.py")
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)

CONTEXT_PHRASES = ("broader", "motivations", "constraints", "decision rationale", "intended outcome")
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".venv")


def run_validate(root):
    return subprocess.run([sys.executable, str(root / "scripts/validate.py")], capture_output=True, text=True)


class SkillInventoryTests(unittest.TestCase):
    def test_standards_skill_is_shipped_but_starts_no_handoff(self):
        self.assertIn("artifact-standards", validate.SKILLS)
        self.assertNotIn("artifact-standards", validate.CROSS_MODEL_SKILLS)
        self.assertNotIn("clear-writing", validate.CROSS_MODEL_SKILLS)
        self.assertTrue(validate.CROSS_MODEL_SKILLS < validate.SKILLS)

    def test_both_packages_ship_identical_standards_files(self):
        expected = {"SKILL.md", "assets/page-shell.html", "references/design-guidance.md"}
        contents = []
        for package in PACKAGES:
            skill = package / "skills/artifact-standards"
            found = {p.relative_to(skill).as_posix() for p in skill.rglob("*") if p.is_file()}
            self.assertEqual(found, expected, f"unexpected standards files in {package.name}")
            contents.append({name: (skill / name).read_bytes() for name in expected})
        self.assertEqual(contents[0], contents[1], "run scripts/sync_plugins.py")

    def test_standards_skill_names_no_host_only_dependency_in_its_description(self):
        for package in PACKAGES:
            frontmatter = (package / "skills/artifact-standards/SKILL.md").read_text(encoding="utf-8").split("---\n")[1]
            for banned in ("artifact-design", "artifact-diagramming", "Artifact tool", "Claude", "Codex"):
                self.assertNotIn(banned, frontmatter, f"{package.name}: description must stay host-neutral")

    def test_standards_resources_resolve_from_the_installed_skill_directory(self):
        with tempfile.TemporaryDirectory(prefix="relocated-package-") as temp:
            relocated = Path(temp) / "elsewhere/mpreibisch-codex"
            shutil.copytree(PACKAGES[0], relocated, ignore=IGNORE)
            skill = relocated / "skills/artifact-standards/SKILL.md"
            body = skill.read_text(encoding="utf-8")
            for link in ("assets/page-shell.html", "references/design-guidance.md", "../clear-writing/SKILL.md"):
                self.assertIn(f"]({link})", body, f"SKILL.md must link {link}")
                self.assertTrue((skill.parent / link).resolve().is_file(), f"{link} must resolve after relocation")

    def test_shipped_standards_files_carry_no_em_dash(self):
        # The skill text quotes the banned HTML entities inside code spans on purpose,
        # so only the literal character is banned everywhere. The page template, which
        # becomes page content, must carry neither the character nor an entity.
        for package in PACKAGES:
            for path in (package / "skills/artifact-standards").rglob("*"):
                if path.is_file():
                    self.assertNotIn("—", path.read_text(encoding="utf-8"), f"em dash in {path}")
            shell = (package / "skills/artifact-standards/assets/page-shell.html").read_text(encoding="utf-8")
            for banned in ("—", "&mdash;", "&#8212;"):
                self.assertNotIn(banned, shell, f"{package.name}: em dash in the page shell")


class PrReviewAskTests(unittest.TestCase):
    FILES = {"SKILL.md", "references/voice.md", "scripts/collect_prs.py"}

    def load_script(self):
        spec = importlib.util.spec_from_file_location(
            "collect_prs", PACKAGES[0] / "skills/pr-review-ask/scripts/collect_prs.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_both_packages_ship_identical_skill_files(self):
        contents = []
        for package in PACKAGES:
            skill = package / "skills/pr-review-ask"
            found = {p.relative_to(skill).as_posix() for p in skill.rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts}
            self.assertEqual(found, self.FILES, f"unexpected pr-review-ask files in {package.name}")
            contents.append({name: (skill / name).read_bytes() for name in self.FILES})
        self.assertEqual(contents[0], contents[1], "run scripts/sync_plugins.py")

    def test_description_stays_host_neutral(self):
        for package in PACKAGES:
            frontmatter = (package / "skills/pr-review-ask/SKILL.md").read_text(encoding="utf-8").split("---\n")[1]
            for banned in ("Claude", "Codex", "connector", "slack_send_message_draft"):
                self.assertNotIn(banned, frontmatter, f"{package.name}: description must stay host-neutral")

    def test_skill_text_carries_no_em_dash_and_never_sends(self):
        for package in PACKAGES:
            for name in self.FILES:
                text = (package / "skills/pr-review-ask" / name).read_text(encoding="utf-8")
                self.assertNotIn("\u2014", text, f"em dash in {package.name}/{name}")
            skill = (package / "skills/pr-review-ask/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("never call a send tool", skill)

    def test_script_help_runs_without_gh(self):
        for package in PACKAGES:
            result = subprocess.run([sys.executable, str(package / "skills/pr-review-ask/scripts/collect_prs.py"), "--help"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--outline", result.stdout)

    def test_parse_ref_accepts_every_documented_form(self):
        script = self.load_script()
        self.assertEqual(script.parse_ref("https://github.com/acme/repo/pull/12", None), ("acme/repo", 12))
        self.assertEqual(script.parse_ref("acme/repo#7", None), ("acme/repo", 7))
        self.assertEqual(script.parse_ref("#7", "acme/repo"), ("acme/repo", 7))
        self.assertEqual(script.parse_ref("7", "acme/repo"), ("acme/repo", 7))
        with self.assertRaises(ValueError):
            script.parse_ref("not-a-pr", "acme/repo")

    def test_build_stacks_nests_child_under_parent_and_keeps_independent_roots(self):
        script = self.load_script()
        def pr(number, base, head):
            return {"repo": "acme/repo", "number": number, "title": f"PR {number}", "draft": False,
                    "base": base, "head": head, "children": []}
        parent, child, grandchild, lone = pr(1, "main", "a"), pr(2, "a", "b"), pr(3, "b", "c"), pr(4, "main", "d")
        roots = script.build_stacks([child, lone, grandchild, parent])
        self.assertEqual([r["number"] for r in roots], [4, 1])
        self.assertEqual(child["stacked_on"], 1)
        self.assertEqual(grandchild["stacked_on"], 2)
        self.assertIsNone(lone["stacked_on"])
        outline = script.outline(roots)
        self.assertTrue(outline[2].startswith("    \u25e6"), outline)
        self.assertIn("(stacked on #2)", outline[3])

    def test_linear_patterns_find_keys_and_workspace_links(self):
        script = self.load_script()
        text = "fix(x): y [RES-14275] see https://linear.app/acme/issue/RES-14302/preserve"
        self.assertEqual(script.LINEAR_KEY.findall(text), ["RES-14275", "RES-14302"])
        self.assertEqual(script.LINEAR_LINK.findall(text), [("acme", "RES-14302")])


class ContextRuleScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="repo-copy-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, symlinks=True, ignore=IGNORE)

    def strip_phrases(self, skill):
        path = self.root / "plugins/mpreibisch-codex/skills" / skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        for phrase in CONTEXT_PHRASES:
            text = text.replace(phrase, "REMOVED")
        path.write_text(text, encoding="utf-8")
        shutil.copyfile(path, self.root / "plugins/mpreibisch-claude/skills" / skill / "SKILL.md")

    def test_unmodified_copy_passes(self):
        result = run_validate(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"{len(validate.SKILLS)} skills per host", result.stdout)

    def test_cross_model_skill_still_fails_without_its_context_phrases(self):
        self.strip_phrases("consensus")
        result = run_validate(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing context requirement", result.stderr)

    def test_standards_skill_needs_no_context_phrases(self):
        self.strip_phrases("artifact-standards")
        result = run_validate(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_standards_skill_fails_the_inventory(self):
        shutil.rmtree(self.root / "plugins/mpreibisch-codex/skills/artifact-standards")
        result = run_validate(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected skill set", result.stderr)

    def test_unsynced_standards_file_fails_package_parity(self):
        target = self.root / "plugins/mpreibisch-claude/skills/artifact-standards/references/design-guidance.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nDrifted.\n", encoding="utf-8")
        result = run_validate(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sync_plugins.py", result.stderr)

    def test_machine_path_in_a_shipped_html_asset_fails(self):
        # Assembled at runtime so this test file itself stays free of a machine path.
        home_path = "/" + "Users" + "/someone/pages/"
        for package in ("mpreibisch-codex", "mpreibisch-claude"):
            asset = self.root / "plugins" / package / "skills/artifact-standards/assets/page-shell.html"
            asset.write_text(asset.read_text(encoding="utf-8").replace(
                "author@example.com", home_path + "author@example.com"), encoding="utf-8")
        result = run_validate(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("machine-specific path", result.stderr)


if __name__ == "__main__":
    unittest.main()
