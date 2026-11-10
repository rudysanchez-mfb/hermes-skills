# Hermes curated skills

A small, curated collection of [Hermes](https://github.com/NousResearch/hermes-agent) agent skills,
published as a normal **skills tap**: one directory per skill under `skills/`,
each containing a `SKILL.md` (and optional helper scripts).

This first release contains exactly two skills. It is intentionally small —
more operational notes will be added only after they have been version-tested
in the open.

## Layout

```
skills/
  scope-fence/
    SKILL.md
  storage-space-check/
    SKILL.md
    scripts/
      check_storage.py
```

Each skill directory is self-contained. A `SKILL.md` starts with YAML
frontmatter containing at least `name` and `description`, followed by the
instruction body. Any helper script is referenced by a path relative to the
skill directory.

## Skills in this release

- **scope-fence** — use on any task that modifies existing work (code, docs,
  configs). It fences changes to exactly what was requested and turns adjacent
  problems into flags instead of unrequested edits, keeping diffs minimal and
  reviewable.
- **storage-space-check** — read-only disk-space diagnostics. It records
  evidence (bytes available, inodes, mount identity, read-only state) before
  anyone declares a disk full, reconciles cleanup claims against measurements,
  and refuses to treat rounding artifacts or unsupported inode counts as
  exhaustion. Includes `scripts/check_storage.py`, a dependency-free,
  read-only checker that takes every path on the command line.

## Install

Add this repository as a Hermes skills tap, then install either skill:

```sh
hermes skills tap add rudysanchez-mfb/hermes-skills
hermes skills install rudysanchez-mfb/hermes-skills/skills/scope-fence
hermes skills install rudysanchez-mfb/hermes-skills/skills/storage-space-check
```

`hermes skills tap add` registers the repo (its default tap path is `skills/`,
which matches this layout) so the skills are discoverable and searchable:

```sh
hermes skills search scope-fence --source github
```

Installing by the full `owner/repo/skills/<name>` identifier fetches that skill
directory from the same GitHub repo (default branch). By default skills land
under `~/.hermes/skills/<name>/`.

For `storage-space-check`, invoke the bundled checker with the paths you want
to measure (adjust the path if you installed into a category):

```sh
python3 ~/.hermes/skills/storage-space-check/scripts/check_storage.py / /path/to/mount
```

The script prints one JSON record per path and never writes to, creates, or
deletes anything on the measured paths. It needs no configuration file and has
no hard-coded paths.

## License

Original code and text in this collection are licensed under the
**Apache License 2.0** — see [LICENSE](LICENSE). See [NOTICE](NOTICE) and
[PROVENANCE.md](PROVENANCE.md) for the provenance and for how third-party
terms, if any are later identified, are retained.
