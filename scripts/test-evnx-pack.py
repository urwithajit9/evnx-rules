#!/usr/bin/env python3
"""Check packs/evnx.toml's GitHub App installation token rule against tokens
built from parts, so no realistic token is ever committed.

Usage: python3 -I scripts/test-evnx-pack.py   (from the repository root)
"""
import base64
import json
import pathlib
import re
import sys
import tomllib

root = pathlib.Path(__file__).resolve().parent.parent
pack = tomllib.loads((root / "packs/evnx.toml").read_text(encoding="utf-8"))
rule = {r["id"]: r for r in pack["rules"]}["evnx-github-app-installation-token"]
new = re.compile(rule["regex"])
classic = re.compile(r"(?:ghu|ghs)_[0-9a-zA-Z]{36}")  # the mirrored upstream rule


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


# ghs_<appid>_<header>.<payload>.<signature>, about 520 characters.
header = b64u(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
payload = b64u(json.dumps({"x": "y" * 90}).encode())
signature = b64u(bytes(range(256)))
token = "ghs_" + "123456" + "_" + ".".join([header, payload, signature])
classic_token = "ghs_" + "A1b2C3d4" * 4 + "wxyz"
assert 480 < len(token) < 580 and token.count(".") == 2, len(token)

failures = []


def check(label, ok):
    if not ok:
        failures.append(label)


m = new.search(token)
check("new-format token matches whole", bool(m) and m.group(0) == token)
for tail in (".", ",", ")", "'"):
    m = new.search(f"token {token}{tail}")
    check(f"trailing {tail!r} not swallowed", bool(m) and m.group(0) == token)
m = new.search(f"GITHUB_TOKEN={token}")
check("matches in an assignment", bool(m) and m.group(0) == token)
check("classic token not matched by the new rule", new.search(classic_token) is None)
check("classic rule still matches the classic token", classic.search(classic_token) is not None)
check("classic rule does not match the new form", classic.search(token) is None)
for text in ("plain text", "ghs_ is a prefix", "ghs_123456_aaaa.bbbb", "ghs_abc_aaaa.bbbb.cccc"):
    check(f"no match on {text!r}", new.search(text) is None)

for f in failures:
    print("FAIL:", f, file=sys.stderr)
print(f"evnx pack: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
