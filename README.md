# Hermes curated skills

A small, curated collection of [Hermes](https://github.com/NousResearch/hermes-agent) agent skills,
published as a normal **skills tap**: one directory per skill under `skills/`,
each containing a `SKILL.md` (and optional helper scripts).

This release contains **ten** battle-tested skills in three groups:
**methodology** (how to plan, verify, edit, and remember), **diagnostics**
(evidence-first operational checks), and **devops** (Hermes-specific operational
runbooks). They are deliberately practical: each one encodes a failure mode that
has actually cost time in production and the procedure that prevents it.

## Layout

```
skills/
  scope-fence/
    SKILL.md
  plan-gate/
    SKILL.md
  adversarial-verify/
    SKILL.md
  ruthless-editor/
    SKILL.md
  memory-hygiene/
    SKILL.md
  storage-space-check/
    SKILL.md
    scripts/
      check_storage.py
  hermes-compression-monitoring/
    SKILL.md
  hermes-cron-pitfalls/
    SKILL.md
  hermes-core-change-safety/
    SKILL.md
  hermes-relay-ops/
    SKILL.md
```

Each skill directory is self-contained. A `SKILL.md` starts with YAML
frontmatter containing at least `name` and `description`, followed by the
instruction body. Any helper script is referenced by a path relative to the
skill directory.

## Skill catalog

### Methodology

- **scope-fence** — use on any task that modifies existing work (code, docs,
  configs). It fences changes to exactly what was requested and turns adjacent
  problems into flags instead of unrequested edits, keeping diffs minimal and
  reviewable.
- **plan-gate** — use before any task with more than one edit, file, or step.
  It forces a written plan (goal, unknowns, success criteria, step order) before
  the first change, and treats a plan-resume request as a search for the
  existing plan rather than a fresh investigation.
- **adversarial-verify** — use after finishing substantive work and before
  presenting it. It switches you from author to attacker: restate the claim,
  attack the requirements and inputs, verify the evidence, and only present the
  work if it survives.
- **ruthless-editor** — use on prose a human will read (docs, READMEs, reports,
  summaries, commit messages, emails). A cutting pass where every sentence must
  earn its place; target 30 percent shorter with zero information loss.
- **memory-hygiene** — use when writing to or reading from persistent agent
  memory. Governs what deserves persistence, how to date and scope it, and the
  recall rule: verify remembered facts against live state before acting.

### Diagnostics

- **storage-space-check** — read-only disk-space diagnostics. It records
  evidence (bytes available, inodes, mount identity, read-only state) before
  anyone declares a disk full, reconciles cleanup claims against measurements,
  and refuses to treat rounding artifacts or unsupported inode counts as
  exhaustion. Includes `scripts/check_storage.py`, a dependency-free,
  read-only checker that takes every path on the command line.
- **hermes-compression-monitoring** — monitor Hermes Agent context compression:
  choose the auxiliary model, parse compression events, audit cost and quality
  from `lcm.db` and `agent.log`, distinguish a healthy drought from a broken
  pipeline, and set up a daily monitoring cron.

### DevOps

- **hermes-cron-pitfalls** — use when a cron job fails, misreports, writes to
  the wrong path, or silently stops producing output. Covers the `$HOME`
  override, stale state files, MCP tools absent in cron, checkpoint starvation,
  sticky `last_failure` badges, completion-policy kills, and watchdog lifetime.
- **hermes-core-change-safety** — use before editing Hermes core source. The
  running agent imports from an environment snapshot, not the checkout; this
  skill covers proving which copy is live, testing against real dispatch,
  running the repo's own gates, and planning rollout and rollback.
- **hermes-relay-ops** — use when setting up, pairing, or troubleshooting
  `hermes-relay`: systemd persistence, dashboard ingress, pairing state, TTL
  policy, and safe restart/uninstall ordering.

## Install

Add this repository as a Hermes skills tap, then install the skills you want:

```sh
hermes skills tap add rudysanchez-mfb/hermes-skills
```

Install all ten:

```sh
hermes skills install rudysanchez-mfb/hermes-skills/skills/scope-fence
hermes skills install rudysanchez-mfb/hermes-skills/skills/plan-gate
hermes skills install rudysanchez-mfb/hermes-skills/skills/adversarial-verify
hermes skills install rudysanchez-mfb/hermes-skills/skills/ruthless-editor
hermes skills install rudysanchez-mfb/hermes-skills/skills/memory-hygiene
hermes skills install rudysanchez-mfb/hermes-skills/skills/storage-space-check
hermes skills install rudysanchez-mfb/hermes-skills/skills/hermes-compression-monitoring
hermes skills install rudysanchez-mfb/hermes-skills/skills/hermes-cron-pitfalls
hermes skills install rudysanchez-mfb/hermes-skills/skills/hermes-core-change-safety
hermes skills install rudysanchez-mfb/hermes-skills/skills/hermes-relay-ops
```

`hermes skills tap add` registers the repo (its default tap path is `skills/`,
which matches this layout) so the skills are discoverable and searchable:

```sh
hermes skills search scope-fence --source github
```

Installing by the full `owner/repo/skills/<name>` identifier fetches that skill
directory from the same GitHub repo (default branch). By default skills land
under `~/.hermes/skills/<name>/`.

## Usage

Load a skill when its trigger matches the task. For example:

- Before a multi-file change: **plan-gate** to write the plan, then
  **scope-fence** to keep the diff bounded.
- Before declaring work done: **adversarial-verify** to try to refute it.
- Before shipping prose: **ruthless-editor** for the cutting pass.
- When a cron job goes red: **hermes-cron-pitfalls**, starting with the
  "sticky last_failure" section.
- When a disk looks full: **storage-space-check** to collect evidence before
  anyone deletes anything.

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
