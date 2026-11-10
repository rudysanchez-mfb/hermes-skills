# Provenance

This document records the source material and changes made for publication.

## Source

Both skills were curated from a private Hermes agent skills directory operated
by the copyright holder:

- `scope-fence/SKILL.md`
- `storage-space-check/SKILL.md`
- `storage-space-check/scripts/check_storage.py`

They were read from the private host read-only over SSH (`BatchMode`, forwarding
disabled) and staged into a clean, allowlisted tree. No file in the source
location was modified, moved, or deleted.

## What was included

Only the two skill directories named above are included in this release.
Nothing else from the private skills tree was copied. A larger set of
operational notes was deliberately deferred until it has been version-tested
in the open.

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

## Verification performed

- Frontmatter parsed for both `SKILL.md` files (`name`, `description` present).
- Relative script reference resolves to an existing file inside the skill.
- `check_storage.py` compiles and runs against temporary fixtures, including a
  permissions-restricted (non-writable) directory, with no files created or
  modified on the measured paths.
- The published `skills/` tree was grepped for personal identifiers, host
  names, private paths, and IP addresses; none remain.

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
