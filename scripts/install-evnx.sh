#!/usr/bin/env bash
# Put an evnx that has `evnx scan rules test` on PATH, for CI.
#
# The latest release, checked against its published .sha256. Until a release
# has `scan rules` (v0.13.0), build evnx's main branch instead, so this
# repository's CI works before and after that release.
set -euo pipefail

bin="${RUNNER_TEMP:-/tmp}/evnx-bin"
mkdir -p "$bin"
base=https://github.com/urwithajit9/evnx/releases/latest/download
asset=evnx-x86_64-unknown-linux-musl.tar.gz
work=$(mktemp -d)
curl -fsSL -o "$work/$asset" "$base/$asset"
curl -fsSL -o "$work/$asset.sha256" "$base/$asset.sha256"
want=$(cut -d' ' -f1 < "$work/$asset.sha256")
got=$(sha256sum "$work/$asset" | cut -d' ' -f1)
if [ "$want" != "$got" ]; then
    echo "evnx release download does not match its .sha256" >&2
    exit 1
fi
tar -xzf "$work/$asset" -C "$work"
# The tarball holds one file, named after the target, not `evnx`.
install -m 0755 "$work/evnx-x86_64-unknown-linux-musl" "$bin/evnx"

# ⚠️ Not `scan rules test --help`: an evnx before 0.13 reads `rules` and
# `test` as paths and prints scan's own help, exit 0. It rejects `--json`.
if ! "$bin/evnx" scan rules list --json >/dev/null 2>&1; then
    echo "the latest release ($("$bin/evnx" --version)) has no \`scan rules\`; building evnx main"
    cargo install --git https://github.com/urwithajit9/evnx --branch main --locked \
        --features net --root "$work/build" evnx
    install -m 0755 "$work/build/bin/evnx" "$bin/evnx"
fi
echo "$bin" >> "${GITHUB_PATH:-/dev/null}"
"$bin/evnx" --version
