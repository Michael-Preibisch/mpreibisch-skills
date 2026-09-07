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
