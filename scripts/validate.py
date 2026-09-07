#!/usr/bin/env python3
"""Validate the repository offline with Python's standard library."""

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / "plugins/mpreibisch-codex"
CLAUDE = ROOT / "plugins/mpreibisch-claude"
CROSS_MODEL_SKILLS = {"consensus", "adversarial-review", "delegate-explore", "delegate-implement"}
SKILLS = CROSS_MODEL_SKILLS | {"clear-writing", "artifact-standards"}


def load_runner():
    spec = importlib.util.spec_from_file_location("cross_model", CODEX / "scripts/cross_model.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    runner = load_runner()
    require((ROOT / "AGENTS.md").is_file(), "missing repository authoring guidelines")
    claude_instructions = ROOT / "CLAUDE.md"
    require(claude_instructions.is_symlink(), "CLAUDE.md must be a symlink to AGENTS.md")
    require(claude_instructions.readlink() == Path("AGENTS.md"), "CLAUDE.md must use a relative AGENTS.md link")
    require((ROOT / "README.md").is_file(), "missing repository installation guide")
    model_defaults = runner.read_json(CODEX / "bridge/models.json")
    require(set(model_defaults) == {"codex", "claude"}, "missing target model defaults")
    for target, workflows in model_defaults.items():
        require(set(workflows) == {"default", "delegate-implement"}, f"invalid model workflows: {target}")
        for settings in workflows.values():
            runner.validate(settings, {"type": "object", "properties": {
                "model": {"type": "string", "minLength": 1},
                "effort": {"type": "string", "minLength": 1}},
                "required": ["model", "effort"], "additionalProperties": False})
    provenance = runner.read_json(ROOT / "provenance/clear-writing.json")
    expected_files = {entry["path"] for entry in provenance["files"]}
    for host, plugin, target in (("codex", CODEX, "claude"), ("claude", CLAUDE, "codex")):
        manifest = runner.read_json(plugin / f".{host}-plugin/plugin.json")
        runner.validate(manifest, runner.read_json(ROOT / f"schemas/{host}-plugin.schema.json"))
        require(manifest["name"] == plugin.name, "manifest name must match its directory")
        require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", manifest["version"]), "invalid release version")
        require(runner.read_json(plugin / "bridge/host.json") ==
                {"calling_host": host, "target_cli": target}, "wrong cross-model direction")
        actual = {p.name for p in (plugin / "skills").iterdir() if p.is_dir()}
        require(actual == SKILLS, f"unexpected skill set in {plugin.name}")
        for name in SKILLS:
            skill = plugin / "skills" / name / "SKILL.md"
            content = skill.read_text(encoding="utf-8")
            frontmatter = content.split("---\n", 2)
            require(len(frontmatter) == 3 and not frontmatter[0], f"missing frontmatter: {skill}")
            require(f"name: {name}\n" in frontmatter[1], f"wrong skill name: {skill}")
            require(re.search(r"^description: .+", frontmatter[1], re.M), f"missing description: {skill}")
            if name in CROSS_MODEL_SKILLS:
                for context in ("broader", "motivations", "constraints", "decision rationale", "intended outcome"):
                    require(context in content.replace("\n", " "), f"missing context requirement: {skill}: {context}")
        imported = plugin / "skills/clear-writing"
        actual_files = {p.relative_to(imported).as_posix() for p in imported.rglob("*") if p.is_file()}
        require(actual_files == expected_files, "clear-writing import inventory mismatch")
        for entry in provenance["files"]:
            data = (imported / entry["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == entry["sha256"], "upstream SHA-256 mismatch")
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            require(blob == entry["git_blob"], "upstream Git blob mismatch")
        for path in plugin.rglob("*"):
            require(not path.is_symlink(), f"package cannot depend on symlinks: {path}")
            if path.suffix == ".md":
                for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    if "://" in link or link.startswith("#"):
                        continue
                    resolved = (path.parent / link.split("#")[0]).resolve()
                    require(resolved.is_relative_to(plugin), f"link leaves package: {path}: {link}")
                    require(resolved.exists(), f"missing package link: {path}: {link}")
    for directory in ("skills", "scripts", "bridge"):
        def inventory(plugin):
            return {p.relative_to(plugin) for p in (plugin / directory).rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts
                    and p.relative_to(plugin).as_posix() != "bridge/host.json"}
        require(inventory(CODEX) == inventory(CLAUDE), f"package inventory drift: {directory}")
        for relative in inventory(CODEX):
            require((CODEX / relative).read_bytes() == (CLAUDE / relative).read_bytes(),
                    f"shared runtime drift: {relative}; run scripts/sync_plugins.py")
    codex_market = runner.read_json(ROOT / ".agents/plugins/marketplace.json")
    claude_market = runner.read_json(ROOT / ".claude-plugin/marketplace.json")
    require(codex_market["name"] == claude_market["name"] == "mpreibisch-skills", "marketplace name mismatch")
    require(len(codex_market["plugins"]) == len(claude_market["plugins"]) == 1, "unexpected marketplace entries")
    entry = codex_market["plugins"][0]
    require(entry == {"name": CODEX.name, "source": {"source": "local", "path": "./plugins/" + CODEX.name},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": "Productivity"}, "invalid Codex marketplace entry")
    entry = claude_market["plugins"][0]
    require(entry["name"] == CLAUDE.name and entry["source"] == "./plugins/" + CLAUDE.name,
            "invalid Claude marketplace source")
    for plugin in (CODEX, CLAUDE):
        runner.validate(runner.read_json(plugin / "bridge/request.example.json"),
                        runner.read_json(plugin / "bridge/request.schema.json"))
    # Platform-specific absolute home paths must never enter a published package.
    machine_path = re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/|[A-Za-z]:\\Users\\[^\\]+\\")
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "__pycache__", ".venv"} for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix in {".md", ".py", ".json", ".mjs", ".html"}:
            require(not machine_path.search(path.read_text(encoding="utf-8")), f"machine-specific path: {path}")
    print(f"Both manifests, marketplaces, {len(SKILLS)} skills per host, package parity, "
          "links, portability, and upstream hashes passed.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        sys.exit(1)
