# External rule sources

Which outside secret-detection rule sets evnx-rules may take rules from, and how.
Checked against GitHub on 2026-10-31: licence from the repository's licence field,
rule counts from the files named. **Re-check the licence and pin a commit before
importing anything** — both drift.

How a source is used decides everything else:

- **Pack**: the rules are data (TOML/YAML), the licence allows redistribution, so
  `evnx scan rules add <file> --format <fmt>` converts them into a pack here, with the
  upstream licence notice kept in the pack header and the upstream commit pinned.
- **Port**: the rules live in code (Go, Python, C#). Individual regexes may be
  rewritten by hand into evnx TOML, with attribution in the rule's comment, when the
  licence is permissive.
- **Reference**: read for which providers exist and what their tokens look like; copy
  nothing.
- **Excluded**: the licence does not allow what a pack does.

## Packs — rules as data, permissive or share-alike licence

| Source | Licence | Rule file | Rules | Format | Notes |
|---|---|---|---|---|---|
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | MIT | `config/gitleaks.toml` | 222 | gitleaks TOML | **First pack** (`packs/gitleaks.toml`). Go RE2 syntax, close to Rust `regex`; rules that don't compile are listed and skipped by the importer |
| [betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) | MIT | `config/betterleaks.toml` | 474 | TOML (gitleaks fork) | Active, and the catalogue Kingfisher now imports from. Confirm the schema matches gitleaks' before reusing the importer |
| [praetorian-inc/noseyparker](https://github.com/praetorian-inc/noseyparker) | Apache-2.0 | `crates/noseyparker/data/default/builtin/rules/*.yml` | 87 files | YAML | ⚠️ **Archived.** Valuable for its `examples:` per rule, which map straight onto our `positive` fixtures. Import once, at a pinned commit; no updates will come |
| [mongodb/kingfisher](https://github.com/mongodb/kingfisher) | Apache-2.0 | `crates/kingfisher-rules/data/*.yml` | 5 own | YAML | Its own file holds only 5 connection-string password rules; the rest is imported from Betterleaks, so take those from Betterleaks directly |
| [mazen160/secrets-patterns-db](https://github.com/mazen160/secrets-patterns-db) | **CC-BY-SA-4.0** | `db/rules-stable.yml` | 1,610 | YAML | The "large" pack. ⚠️ Share-alike: the converted pack must itself be CC-BY-SA-4.0 with attribution, so it stays a separate, opt-in pack and never feeds the core. Expect noise; measure before listing it in the index |

## Port by hand — rules in code, permissive licence

| Source | Licence | Where | Worth taking |
|---|---|---|---|
| [google/osv-scalibr](https://github.com/google/osv-scalibr) (Veles) | Apache-2.0 | `veles/secrets/*` (59 detectors, Go) | Well-tested modern formats: Anthropic, Cursor, Deno, Bitwarden, GCP, crates.io |
| [microsoft/security-utilities](https://github.com/microsoft/security-utilities) | MIT | `src/Microsoft.Security.Utilities.Core` (C#) | Authoritative formats for Azure and Microsoft keys, including identifiable checksummed keys |
| [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) | Apache-2.0 | `detect_secrets/plugins/*.py` | A small set; mostly covered elsewhere. IBM Cloud and Cloudant are the unusual ones |
| [awslabs/git-secrets](https://github.com/awslabs/git-secrets) | Apache-2.0 | `git-secrets` (shell) | AWS only; already in the core |
| [sirwart/ripsecrets](https://github.com/sirwart/ripsecrets) | MIT | `src/matcher` (Rust) | Rust-syntax regexes, so a port is near-verbatim |
| [thoughtworks/talisman](https://github.com/thoughtworks/talisman) | MIT | `detector/pattern` (Go) | Few provider rules; its file-name rules (`id_rsa`, `.pem`) are the interesting part |
| [newrelic/rusty-hog](https://github.com/newrelic/rusty-hog) | Apache-2.0 | `src/` (Rust) | Small; mostly duplicates gitleaks |
| [eth0izzle/shhgit](https://github.com/eth0izzle/shhgit) | MIT | `config.yaml` | Unmaintained since 2025-02; file-name signatures only |

## Reference only

| Source | Why not more |
|---|---|
| [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | **AGPL-3.0**, and detectors are Go code that also verifies keys online. Use its detector list to find providers we lack; write our rules from the provider's own docs |
| [GitHub secret scanning patterns](https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns) | A list of providers and token types, no regexes. The best checklist for coverage gaps |
| [GitGuardian/ggshield](https://github.com/GitGuardian/ggshield) | MIT client, but detection runs on GitGuardian's servers; there are no rules in the repo |

## Excluded

| Source | Why |
|---|---|
| [semgrep/semgrep-rules](https://github.com/semgrep/semgrep-rules) | Semgrep Rules License v1.0 restricts redistribution and use in competing products |

## Rules for taking from any source

1. **Pin a commit**, never a branch. The pack header records the upstream URL, commit
   and licence; `rules.lock` records the pack's sha256.
2. **Keep the licence notice** in the pack header. CC-BY-SA material stays in its own
   pack under its own licence.
3. **Every imported rule gets fixtures** before it ships in the index: the upstream's
   examples where they exist (Nosey Parker, Betterleaks), otherwise values built from
   the provider's documented format. Never a live credential.
4. **Nothing imported enters the core.** The core is our own ~60 rules (v0.13.0 S1).
   A rule ported into the core is rewritten against the provider's documentation and
   credited in a comment.
