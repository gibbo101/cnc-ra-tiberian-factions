#!/usr/bin/env python3
"""Check docs/*.md against the rules in docs/README.md; exit 1 and list every failure.

Usage: docs_check.py [repo root]
"""
import re
import sys
from pathlib import Path

KINDS = ("Reference", "Design", "Parked", "Tracker")
STATUS = re.compile(r"^\*\*Status:\*\* (%s)\b" % "|".join(KINDS))
BANNED = [
    (re.compile(r"RESUME HERE", re.I), '"RESUME HERE"'),
    (re.compile("⭐"), "a star marker"),
    (re.compile(r"\[\["), "a [[memory link]]"),
    (re.compile(r"`(reference|project|feedback|spike)-[a-z0-9-]+(\.md)?`"), "a memory-file pointer"),
    (re.compile(r"\bCORRECTION\b"), 'a "CORRECTION" section'),
    (re.compile(r"\bLuke\b"), "a personal name"),
]
TODO_MAX_LINES = 300
CITATION = re.compile(r"`(?:docs/)?([A-Za-z0-9_.-]+\.md)`")


def status_line(lines):
    """The first non-blank line after the title, or '' if there is none."""
    seen_title = False
    for line in lines:
        if not seen_title:
            seen_title = line.startswith("# ")
            continue
        if line.strip():
            return line
    return ""


def check(root):
    docs = root / "docs"
    index = (docs / "README.md").read_text(encoding="utf-8") if (docs / "README.md").exists() else ""
    failures = []
    for path in sorted(docs.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        name = path.name
        if not STATUS.match(status_line(lines)):
            failures.append((name, "no **Status:** line (%s) under the title" % " / ".join(KINDS)))
        if name != "README.md" and "`%s`" % name not in index:
            failures.append((name, "not listed in docs/README.md"))
        for number, line in enumerate(lines, 1):
            for pattern, what in BANNED:
                if pattern.search(line):
                    failures.append((name, "line %d: %s" % (number, what)))
            for cited in CITATION.findall(line):
                if not (docs / cited).exists() and not (root / cited).exists():
                    failures.append((name, "line %d: cites `%s`, which does not exist" % (number, cited)))
        if name == "todo.md" and len(lines) > TODO_MAX_LINES:
            failures.append((name, "%d lines, over %d: move finished work out" % (len(lines), TODO_MAX_LINES)))
        if name == "known-issues.md":
            for number, line in enumerate(lines, 1):
                if line.startswith("#") and re.search(r"\b(FIXED|RESOLVED)\b", line):
                    failures.append((name, "line %d: a fixed entry; delete it" % number))
    return failures


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    failures = check(root)
    for name, message in failures:
        print("docs/%s: %s" % (name, message))
    if failures:
        print("docs_check: %d problem(s); the rules are in docs/README.md" % len(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
