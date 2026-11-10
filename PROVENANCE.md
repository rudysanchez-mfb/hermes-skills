# Provenance

This document records the source material and changes made for publication.

## Source

The original two skills were curated from a private Hermes agent skills
directory operated by the copyright holder:

- `scope-fence/SKILL.md`
- `storage-space-check/SKILL.md`
- `storage-space-check/scripts/check_storage.py`

They were read from the private host read-only over SSH (`BatchMode`, forwarding
disabled) and staged into a clean, allowlisted tree. No file in the source
location was modified, moved, or deleted.

## What was included

The initial release included only the two skill directories named above.
A later release added the eight curated skills listed in the next section.
No other files from the private skills tree were copied. The ancillary
`references/` and `scripts/` directories that accompanied some of the later
skills were deliberately not published; dangling references to them were
removed or replaced with self-contained guidance.

## Changes made for publication

### New repository scaffolding (not in the source)
`README.md`, `LICENSE`, `NOTICE`, and `PROVENANCE.md` were written for this
release and are not part of the source skills. `tests/test_check_storage.py`
is a new, stdlib-only `unittest` suite exercising the checker's record
arithmetic and CLI exit codes; it is repo-level test scaffolding, not skill
content, and is not part of the installable skill.

### `scope-fence/SKILL.md`
Copied verbatim. Its text contained no personal identifiers, host names, IP
addresses, file paths, or private infrastructure references, so no edits were
needed to make it publishable.

### `storage-space-check/SKILL.md`
Edited to remove environment-specific material while preserving every
substantive instruction:

- Removed references to a private, environment-specific evidence-gate plugin
  and its internal naming. The useful behavior was kept as a generic
  **Evidence gate** section: run the checker and keep its output, and require
  `available_bytes == 0` before claiming byte-level exhaustion.
- Removed a user-specific absolute script path and replaced it with a relative,
  location-independent reference (`ABSOLUTE_SKILL_DIR/scripts/...` resolved
  from the skill's own directory).
- Removed a named host and its specific candidate mount paths; the procedure
  now says to pass the specific paths to assess and verify them live.
- Removed a named private filesystem, generalizing the inode-accounting
  observation to "some exFAT filesystems".
- Replaced the user's name with "the user" in the cleanup-reconciliation
  guidance.
- Generalized a product-specific wording ("Plex") to "media-server" in one
  bullet.

All arithmetic rules, scope limits, reporting guidance, and diagnostic
procedure were preserved.

### `storage-space-check/scripts/check_storage.py`
Rewritten as a self-contained, portable script:

- Adds a `#!/usr/bin/env python3` shebang and a module docstring.
- Has **no** hard-coded paths and no dependency on any private configuration
  file. Every path is supplied on the command line.
- Preserves the exact arithmetic and JSON field names of the original.
- Handles an unreadable path per-path (reports the error on stderr, continues
  to other paths, exits non-zero) instead of aborting the whole run.
- Confirmed read-only: it only calls `os.statvfs` and never writes to,
  creates, or deletes anything on the measured paths.

## Second release: eight curated skills

Eight additional skills were curated from the same private Hermes agent skills
directory, read from the private host read-only over SSH (`BatchMode`,
forwarding disabled). No file in the source location was modified, moved, or
deleted.

Source paths and published destinations:

- `adversarial-verify/SKILL.md` -> `skills/adversarial-verify/SKILL.md`
- `plan-gate/SKILL.md` -> `skills/plan-gate/SKILL.md`
- `ruthless-editor/SKILL.md` -> `skills/ruthless-editor/SKILL.md`
- `memory-hygiene/SKILL.md` -> `skills/memory-hygiene/SKILL.md`
- `devops/hermes-cron-pitfalls/SKILL.md` -> `skills/hermes-cron-pitfalls/SKILL.md`
- `devops/hermes-core-change-safety/SKILL.md` -> `skills/hermes-core-change-safety/SKILL.md`
- `devops/hermes-compression-monitoring/SKILL.md` -> `skills/hermes-compression-monitoring/SKILL.md`
- `devops/hermes-relay-ops/SKILL.md` -> `skills/hermes-relay-ops/SKILL.md`

### Sanitization performed on the eight skills

Every published file was reviewed and edited to remove material that was
specific to the private environment while preserving the operational
instruction:

- **Absolute home paths.** Every `/home/<actual-user>/...` path was replaced
  with a neutral placeholder (`/home/<user>/...`) or with `$HERMES_HOME` /
  `~/.hermes/...` where the text already used a home-relative convention. A
  note was added where the placeholder must be substituted for the absolute
  path to work (notably the `$HOME`-override pitfall in `hermes-cron-pitfalls`).
- **Host and network identifiers.** No hostnames or LAN IP addresses remain.
  Loopback addresses (`127.0.0.1`, `localhost`) were kept only where they are
  part of the technical procedure and identify no private host.
- **Personal names and incident references.** References to the operator by
  name were replaced with "the operator" / "the user". Named private scripts,
  job names, session IDs, and one-off incident dates were generalized into
  representative examples; the technical failure mode and fix were retained.
- **Frontmatter.** Each of the eight new `SKILL.md` files was normalized to a
  clean `name` + `description` block (the two original skills already had
  one). The `name` matches the published directory name for all ten skills.
  Source-specific `version`, `author`, `license`, `platforms`, `category`, and
  `metadata.related_skills` keys were dropped where they referenced skills that
  are not part of this tap or conflicted with the repository's Apache-2.0
  licensing.
- **Dangling references.** The skills referenced ancillary `references/*.md`
  files and `scripts/*.py` helpers that were not published in this release.
  Those pointers were removed or rewritten as self-contained instructions, so
  no published link points at a file that does not exist. Where a tool or
  service name was specific to the private stack, the guidance was generalized
  to the equivalent generic workflow (for example, "an email-provider REST
  fallback" rather than a named private script).
- **No secrets.** No API keys, tokens, passwords, private keys, or credential
  fragments were copied. The source files contained at most redacted
  credential-shaped examples; those were removed rather than published.

## Verification performed

- Frontmatter parsed for all ten `SKILL.md` files (`name`, `description`
  present; `name` matches its directory).
- Relative Markdown links in `README.md` and `PROVENANCE.md` resolve to files
  in this repository; no published skill points at an unpublished reference or
  script file.
- The full `skills/` tree was scanned for personal names, absolute user-home
  paths, hostnames, LAN IP addresses, credential-shaped strings, and private
  key material; none remain.
- The stdlib `unittest` suite still passes (`python3 -m unittest discover -s
  tests -v`).
- `storage-space-check`'s relative script reference resolves to an existing
  file inside the skill, and `check_storage.py` compiles and runs against
  temporary fixtures, including a permissions-restricted (non-writable)
  directory, with no files created or modified on the measured paths.

## Rights and provenance caveats

- **No upstream authorship assumption.** The source files carried only a
  `name`/`description` frontmatter block and no author, copyright, or license
  metadata. That absence is not taken to mean the copyright holder authored
  every line, nor that no third-party terms apply. It is simply an absence of
  metadata.
- **Third-party terms.** None were identified. If any portion is later shown to
  include third-party material, the original terms must be retained and
  surfaced in `NOTICE` before public release.
- **Release authorization.** Rudy Sanchez authorized publication under
  `rudysanchez-mfb` using Apache-2.0 for original code and skills, with existing
  third-party terms retained. `NOTICE` names Rudy Sanchez as copyright holder.
