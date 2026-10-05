#!/usr/bin/env python3
"""Check the comments in our code against the rules in CLAUDE.md; exit 1 and list every new failure.

Fails on a personal name, an ISO date, or a docs/<name>.md that does not exist, inside a comment of the DLL
source, the scripts, rules.ini or the shell scripts. Violations listed in scripts/code_check_baseline.txt are
known and tolerated; a baseline entry that no longer occurs is reported so it can be deleted.

Usage: code_check.py [repo root] [--write-baseline]
"""
import re
import sys
from pathlib import Path

RULES = [
    (re.compile(r"\bLuke\b", re.I), "a personal name"),
    (re.compile(r"\b20\d\d-\d\d-\d\d\b"), "a date"),
]
DOC_CITE = re.compile(r"(?<![\w/.-])docs/([A-Za-z0-9_.-]+\.md)\b")
CODE_GLOBS = ["redalert/*.cpp", "redalert/*.h", "redalert/*.inc", "common/*.cpp", "common/*.h"]
HASH_GLOBS = ["scripts/*.py", "scripts/*.sh", "*.sh"]
INI_FILES = ["resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini"]
BASELINE = "scripts/code_check_baseline.txt"


def c_comments(text):
    """(line number, comment text) for every // and /* */ comment in C or C++ source."""
    out, in_block = [], False
    for n, line in enumerate(text.splitlines(), 1):
        rest, parts = line, []
        while rest:
            if in_block:
                end = rest.find("*/")
                if end < 0:
                    parts.append(rest)
                    rest = ""
                else:
                    parts.append(rest[:end])
                    rest, in_block = rest[end + 2:], False
                continue
            line_c, block_c = rest.find("//"), rest.find("/*")
            if line_c >= 0 and (block_c < 0 or line_c < block_c):
                parts.append(rest[line_c + 2:])
                rest = ""
            elif block_c >= 0:
                rest, in_block = rest[block_c + 2:], True
            else:
                rest = ""
        if parts:
            out.append((n, " ".join(parts)))
    return out


def hash_comments(text, python):
    """(line number, comment text) for # comments, and for Python docstring lines."""
    out, in_doc = [], None
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if python and in_doc:
            out.append((n, line))
            if in_doc in line:
                in_doc = None
            continue
        if python:
            for quote in ('"""', "'''"):
                if stripped.startswith(quote) or stripped.startswith("r" + quote):
                    out.append((n, line))
                    if stripped.count(quote) == 1:
                        in_doc = quote
                    break
            else:
                if "#" in line:
                    out.append((n, line[line.index("#") + 1:]))
            continue
        if "#" in line and not stripped.startswith("#!"):
            out.append((n, line[line.index("#") + 1:]))
    return out


def ini_comments(text):
    return [(n, line.split(";", 1)[1]) for n, line in enumerate(text.splitlines(), 1) if ";" in line]


def violations(root):
    found = []
    files = []
    for g in CODE_GLOBS:
        files += [(p, "c") for p in sorted(root.glob(g))]
    for g in HASH_GLOBS:
        files += [(p, "py" if p.suffix == ".py" else "sh") for p in sorted(root.glob(g))]
    files += [(root / f, "ini") for f in INI_FILES if (root / f).exists()]
    for path, kind in files:
        text = path.read_text(errors="replace")
        if kind == "c":
            comments = c_comments(text)
        elif kind == "ini":
            comments = ini_comments(text)
        else:
            comments = hash_comments(text, kind == "py")
        rel = path.relative_to(root).as_posix()
        for n, comment in comments:
            for pattern, what in RULES:
                if pattern.search(comment):
                    found.append((rel, n, what, comment.strip()))
            for name in DOC_CITE.findall(comment):
                if not (root / "docs" / name).exists():
                    found.append((rel, n, "a missing doc (docs/%s)" % name, comment.strip()))
    return found


def key(v):
    """Baseline identity: file, rule and comment text, so moving a line doesn't break the match."""
    return "%s\t%s\t%s" % (v[0], v[2], " ".join(v[3].split()))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    found = violations(root)
    base_path = root / BASELINE
    if "--write-baseline" in sys.argv:
        base_path.write_text("".join(sorted(set(key(v) + "\n" for v in found))))
        print("wrote %d baseline entries to %s" % (len(set(map(key, found))), BASELINE))
        return 0
    baseline = set(base_path.read_text().splitlines()) if base_path.exists() else set()
    new = [v for v in found if key(v) not in baseline]
    gone = baseline - set(map(key, found))
    for rel, n, what, text in new:
        print("%s:%d: %s in a comment: %s" % (rel, n, what, text[:100]))
    for entry in sorted(gone):
        print("fixed, delete from %s: %s" % (BASELINE, entry.split("\t")[0] + " " + entry.split("\t")[1]))
    known = len(baseline) - len(gone)
    if new:
        print("code_check: %d new failure(s); %d known in the baseline" % (len(new), known), file=sys.stderr)
        return 1
    if known:
        print("code_check: clean apart from %d known baseline entries" % known)
    return 0


if __name__ == "__main__":
    sys.exit(main())
