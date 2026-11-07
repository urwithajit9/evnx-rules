# Contributing to evnx-rules

## A rule for evnx itself, or for a pack?

**A rule for the evnx core** belongs in the
[evnx repository](https://github.com/urwithajit9/evnx) (`src/assets/rules.toml`), not
here. It must meet the inclusion rule: *the provider documents a fixed prefix, or a
fixed length and character set.* Generic secret shapes with no prefix stay with evnx's
entropy heuristic.

**Everything wider is a pack**, and lives here.

## Adding or changing a pack

1. Name the upstream source and its licence, and check it against
   [SOURCES.md](SOURCES.md). Put the licence text in `LICENSES/`.
2. Pin the upstream commit, and its file's sha256, in the pack header.
3. Convert with evnx itself, never by hand:
   `evnx scan rules add <upstream file> --format gitleaks`, then copy
   `.evnx/rules/<name>.toml` to `packs/` and replace its first four comment lines
   with the upstream header (see `packs/gitleaks.toml`).
4. Give every rule you write at least one `positive` and one `near_miss` value.
   No live credentials: build values from the documented format.
   ⓘ An **imported** pack is the exception: gitleaks keeps its examples in Go, not in
   its TOML, so `packs/gitleaks.toml` has none, and `evnx scan rules test` checks only
   that each rule compiles.
5. Run `evnx scan rules test packs/<name>.toml`.
6. Update the pack's `sha256` and `rules` in `index.toml`, in the same commit, and run
   `python3 -I scripts/check-index.py`.

CI runs steps 5 and 6, and adds the pack by name from a local copy of the catalogue,
the way a user would. A pull request that changes a pack without its hash does not
merge.

## Rule ids

Every rule needs an id, unique across evnx's own rules and every pack. An imported
rule gets the pack's name in front (`gitleaks-aws-access-token`), so it can never
collide with an evnx id.
