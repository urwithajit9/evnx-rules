#!/usr/bin/env python3
"""Every pack in index.toml exists, hashes to its listed sha256, and holds the
listed number of rules; every file in packs/ is listed. Exit 1 on any mismatch.

Usage: python3 -I scripts/check-index.py   (from the repository root)
"""
import hashlib
import pathlib
import sys
import tomllib

root = pathlib.Path(__file__).resolve().parent.parent
index = tomllib.loads((root / "index.toml").read_text(encoding="utf-8"))
problems = []
if index.get("version") != 1:
    problems.append("index.toml: version must be 1")
listed = set()
for p in index.get("pack", []):
    path = root / p["path"]
    listed.add(path.resolve())
    if not path.is_file():
        problems.append(f"{p['name']}: {p['path']} does not exist")
        continue
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != p["sha256"]:
        problems.append(f"{p['name']}: sha256 is {sha}, index.toml says {p['sha256']}")
    rules = len(tomllib.loads(data.decode("utf-8")).get("rules", []))
    if rules != p["rules"]:
        problems.append(f"{p['name']}: {rules} rules, index.toml says {p['rules']}")
for f in sorted((root / "packs").glob("*.toml")):
    if f.resolve() not in listed:
        problems.append(f"{f.relative_to(root)} is not listed in index.toml")
for line in problems:
    print(line, file=sys.stderr)
print(f"index.toml: {len(index.get('pack', []))} pack(s), {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
