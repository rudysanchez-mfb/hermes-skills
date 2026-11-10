---
name: hermes-core-change-safety
description: "Use when editing Hermes core source; the runtime is a snapshot, not the checkout."
---

# Hermes Core Change Safety

Use this before editing ANY file under the Hermes source checkout (core Python,
plugins, hooks, turn gates, model_tools). It prevents the two expensive mistakes:
silently mutating the live runtime, and shipping a change the repo's own gates reject.

## When to Use

- You are about to edit, add, or test any file under the Hermes source checkout.
- You need plugin/hook behaviour exercised through real dispatch, not a stub.
- You must confirm a change did NOT reach the live agent yet.

## The one fact that matters most

**On a managed install the running agent imports from an environment SNAPSHOT,
not from the source checkout.** The checkout is the edit target; the snapshot is
what actually runs.

Verify (never assume) before editing:

```bash
# 1. Resolve the active environment
python3 -c "import json;d=json.load(open('$HOME/.hermes/installs/<install-id>/facts.json'));print(d['packages']['venv']['environment'])"
# 2. Ask the runtime where it imports from — the authoritative answer
<env>/venv/bin/python3 -c "import hermes_cli.plugins as p; print(p.__file__)"
#    prints .../environments/<env-id>/workspace/hermes_cli/plugins.py
```

**Run step 2 from a NEUTRAL cwd (`cd /tmp`).** From the checkout root, `sys.path[0]` is the
cwd, so the same venv python imports the CHECKOUT and prints it as the live path — a false
"this install runs the checkout" verdict that makes an inert edit look live.

Snapshot and checkout are INDEPENDENT copies (different inodes, `links=1`), not
hardlinks — confirm with `stat -c '%i links=%h %n' <snapshot>/<file> <checkout>/<file>`.
That is why editing the checkout cannot affect the live agent or new sessions.

Rules:
- Edit the CHECKOUT. Never patch the install snapshot in place.
- Resolve the supported activation path from the installed version's metadata, CLI help,
  and update documentation before editing. Do not assume `hermes update` is the only path,
  or invent a local rebuild command. Keep activation separate from source edits; arrange
  verification outside any process the rollout will terminate.
- Prove the live runtime was not disturbed: `sha256sum` the snapshot's copy of every
  file you edited, before and after. Byte-identical until rollout is the pass condition.

## Testing a core change

- The checkout has its own test environment (e.g. `<checkout>/venv`). The supported
  runner is `scripts/run_tests.sh` — use it, don't invent an invocation.
- Run the repo's `scripts/check` (lint/health ratchet). It FAILS a change that grows
  a file already over its line cap — when that fires, move the new logic into a sibling
  module (that is the repo's own convention) rather than inflating a god-file.
- TDD the non-obvious behaviour: write the regression that FAILS against the
  pre-change core and show the real RED output. A test that would pass before the
  change proves nothing.
- **Make the RED fail for the reason the fix removes.** Run the regression against the
  recorded pre-change revision in an isolated worktree or source copy with a throwaway home.
  Do not repeatedly revert and restore the active dirty checkout: concurrent workers and
  interrupted commands can observe or leave the wrong bytes. If RED trips on an unrelated
  guard before the bug assertion, fix the harness before treating it as regression evidence.
- **Assert field VALUES, not key presence.** Records often seed optional fields to `None` at
  creation, so `"field" not in record` fails for a reason unrelated to the bug. Print the
  record once before writing an assertion whose semantics are not obvious.
- **Attribute failures individually against an isolated baseline.** Run the same selected
  tests with matching dependencies, environment, and runner on baseline and candidate; compare
  failing test IDs and failure causes, not totals alone. A baseline comparison of three files
  does not explain failures elsewhere in the suite. Report unmatched failures as unclassified,
  never infer that they are unrelated from their volume or filenames. Run the nearest existing
  end-to-end test before building on its harness; resolve harness failures rather than quietly
  substituting a gate-level test and calling it end-to-end.
- **Keep verification bounded and updates short.** Start with tests for the touched behavior
  and expand only for a concrete dependency risk or repository requirement. When the operator
  interrupts to question what you are doing, answer the scope and current state before
  launching more work; do not promise to stop and then run another suite or duplicate verifier.
  Use background completion notifications instead of replacing a prohibited poll with PID
  checks, log loops, or sleeps. Report baseline attribution separately from the candidate's
  pass/fail counts.

## Testing a plugin / hook change against REAL dispatch

A plugin test in a package venv that lacks Hermes deps can only skip the real path.
Run the real dispatch with an interpreter that HAS Hermes deps and a throwaway home:

```bash
PYTHONPATH=<checkout>:<pkg>/src \
HERMES_HOME=$(mktemp -d) \
<checkout-venv-python> -m pytest <test-file> -q -p no:cacheprovider
```

- `HERMES_HOME` MUST be a throwaway dir — never the real profile.
- The hook names your plugin registers must be real members of the host's hook
  registry (`hermes_cli.plugins.VALID_HOOKS`). NOTE the real failure mode: an
  UNKNOWN name only WARNS and the callback is still STORED — with no fire site it is
  INERT, so the plugin loads clean while that hook never fires. Never register
  blindly: guard on the runtime's supported hooks and SURFACE the unsupported ones.
- A green real-dispatch run against the CHECKOUT proves nothing about the deployed
  runtime if the checkout is ahead of it. Run the suite against the active SNAPSHOT
  workspace too (`PYTHONPATH=<snapshot>/workspace`) and report any difference.
- A plugin hook body must never raise into the host: wrap every callback so a
  failure degrades to a fail-open return (or a recorded, visible failure), never an
  uncaught exception on the hot path.

## Rollout

**Check the rollout posture BEFORE you edit**, not after — it decides whether the change can
ship at all:

```bash
git rev-parse --abbrev-ref HEAD
git rev-list --left-right --count origin/main...HEAD    # <behind>  <ahead>
git log --oneline origin/main..HEAD | head              # local-only commits
hermes update --check   # read-only: is a release pending?
hermes update --plan    # read-only: install kind + every service it will restart
```

Verify the installed CLI documents `--check` and `--plan` as read-only before using them.
Start with those outputs, then inspect the matching updater source when target selection or
activation behavior remains unclear.

**Divergence is a risk indicator, not an activation verdict.** Determine the actual update
channel, requested target, branch tracking, parked-branch policy, and treatment of local commits
and dirty changes. Release-tag activation, branch switching, and in-place merging are different
paths; a count against `origin/main` does not prove which path runs. A historical "already up
to date" result does not establish today's target either. Do not claim that no local activation
path exists until the current supported interface and documentation have been inspected.

Before activation, record the exact candidate revision, backup, rollback, expected service
impact, and verification owner. Protect local safeguards; do not substitute arbitrary `git pull`,
a blind upgrade, or snapshot edits. If a genuine unresolved trade-off remains, present one
specific evidence-backed decision rather than a speculative rollout menu. After rollout, verify
the active runtime's import path/revision, relevant behavior, and service health. A queued worker,
a completed build, and passing checkout tests are milestones, not deployed completion.
