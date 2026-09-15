#!/usr/bin/env python3
"""Fetch PR facts with `gh` and arrange them into stacks.

Usage: collect_prs.py [--repo OWNER/NAME] [--outline] REF [REF ...]

A REF is a PR URL, `#123`, `123`, or `OWNER/NAME#123`. Bare numbers resolve against
`--repo`, else the repository of the current directory. The JSON output has the facts
the message needs: title, URL, base and head branches, draft state, requested reviewers,
Linear keys found in the title, body, or branch, and a forest of stacks. `--outline`
prints a plain nested list instead, for a quick look.
"""

import argparse
import json
import re
import subprocess
import sys

FIELDS = "number,title,url,body,baseRefName,headRefName,isDraft,state,author,reviewRequests"
LINEAR_KEY = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d+)\b")
LINEAR_LINK = re.compile(r"https://linear\.app/([a-z0-9-]+)/issue/([A-Z][A-Z0-9]{1,9}-\d+)")
URL_REF = re.compile(r"https://github\.com/([^/\s]+/[^/\s]+)/pull/(\d+)")
SHORT_REF = re.compile(r"^(?:([^/\s#]+/[^/\s#]+))?#?(\d+)$")


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"command failed: {' '.join(args)}")
    return result.stdout


def current_repo():
    return run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).strip()


def parse_ref(ref, default_repo):
    match = URL_REF.search(ref)
    if match:
        return match.group(1), int(match.group(2))
    match = SHORT_REF.match(ref.strip())
    if match:
        return match.group(1) or default_repo, int(match.group(2))
    raise ValueError(f"not a PR reference: {ref}")


def fetch(repo, number):
    data = json.loads(run(["gh", "pr", "view", str(number), "--repo", repo, "--json", FIELDS]))
    text = " ".join([data["title"], data.get("body") or "", data["headRefName"]])
    links = {key: f"https://linear.app/{workspace}/issue/{key}" for workspace, key in LINEAR_LINK.findall(text)}
    keys = sorted({*LINEAR_KEY.findall(text), *links})
    reviewers = []
    for request in data.get("reviewRequests") or []:
        reviewers.append(request.get("login") or request.get("name") or request.get("slug") or "")
    return {
        "repo": repo,
        "number": data["number"],
        "title": data["title"],
        "url": data["url"],
        "body": data.get("body") or "",
        "base": data["baseRefName"],
        "head": data["headRefName"],
        "draft": data["isDraft"],
        "state": data["state"],
        "author": (data.get("author") or {}).get("login", ""),
        "reviewers": [name for name in reviewers if name],
        "linear_keys": keys,
        "linear_links": links,
        "children": [],
    }


def build_stacks(prs):
    """A PR whose base branch is another listed PR's head branch nests under it."""
    by_head = {}
    for pr in prs:
        by_head.setdefault((pr["repo"], pr["head"]), pr)
    roots = []
    for pr in prs:
        parent = by_head.get((pr["repo"], pr["base"]))
        if parent is not None and parent is not pr:
            pr["stacked_on"] = parent["number"]
            parent["children"].append(pr)
        else:
            pr["stacked_on"] = None
            roots.append(pr)
    return roots


def outline(nodes, depth=0):
    lines = []
    for node in nodes:
        marker = "•" if depth == 0 else "◦"
        suffix = f" (stacked on #{node['stacked_on']})" if node["stacked_on"] else ""
        draft = " [draft]" if node.get("draft") else ""
        lines.append(f"{'    ' * depth}{marker} {node['title']} (#{node['number']}){draft}{suffix}")
        lines.extend(outline(node["children"], depth + 1))
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", help="OWNER/NAME for bare PR numbers")
    parser.add_argument("--outline", action="store_true", help="print a nested text outline instead of JSON")
    parser.add_argument("refs", nargs="+")
    args = parser.parse_args()

    default_repo = args.repo
    prs, errors, seen = [], [], set()
    for ref in args.refs:
        try:
            if default_repo is None and not URL_REF.search(ref) and "/" not in ref:
                default_repo = current_repo()
            repo, number = parse_ref(ref, default_repo)
            if (repo, number) in seen:
                continue
            seen.add((repo, number))
            prs.append(fetch(repo, number))
        except (RuntimeError, ValueError) as error:
            errors.append({"ref": ref, "error": str(error)})

    roots = build_stacks(prs)
    workspaces = sorted({url.split("/")[3] for pr in prs for url in pr["linear_links"].values()})
    if args.outline:
        print("\n".join(outline(roots)))
        for item in errors:
            print(f"! {item['ref']}: {item['error']}", file=sys.stderr)
    else:
        json.dump({"stacks": roots, "linear_workspaces": workspaces, "errors": errors}, sys.stdout, indent=2)
        print()
    sys.exit(1 if errors and not prs else 0)


if __name__ == "__main__":
    main()
