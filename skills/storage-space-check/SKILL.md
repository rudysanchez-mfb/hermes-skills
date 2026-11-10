---
name: storage-space-check
description: "Use when checking disk space or a disk-full claim."
---

# Storage space: evidence before alarm

## When to Use
Check disk space, challenge a disk-full alarm, reconcile cleanup claims, or assess storage before downloads. Load this skill before making a storage claim even when disk usage appears incidentally during playback, network, cache, or service troubleshooting; the original task's category does not exempt a new storage diagnosis.

## Evidence gate

Loading this skill is not sufficient. Run the checker and produce output before you make a storage claim. Run:

```
python3 ABSOLUTE_SKILL_DIR/scripts/check_storage.py PATH [PATH ...]
```

Keep the timestamped JSON it emits as your evidence. A byte-level exhaustion claim requires `available_bytes == 0`; a df-style percentage of 100% with positive GiB available is a rounding artifact and does NOT support exhaustion.

## Scope
Read-only diagnostic. Use before declaring a disk full, comparing a previous cleanup, or proposing remediation. No deletion, migration, reserved-block change, root-folder removal, service restart or scheduled job is authorized by this skill.

## Check procedure
1. Verify mount identity with `findmnt -T PATH -o TARGET,SOURCE,FSTYPE,OPTIONS`. An external drive's TARGET must equal the intended mount, not `/`. Confirm source/UUID against expected identity if needed; device letters can change.
2. Run `python3 ABSOLUTE_SKILL_DIR/scripts/check_storage.py PATH [PATH ...]`, resolving ABSOLUTE_SKILL_DIR from the skill's own location. Pass the specific paths you want to assess (for example `/` or a mounted volume) and verify them live. The script emits timestamped JSON records without writing to the measured paths.
3. Lead with available_bytes/GiB, then available inodes, read_only and mount identity. These metadata checks are NOT a write test or proof of application health. Preserve errors; a failed command is not a zero-space measurement. Inspect permissions, quotas and application errors if writes fail.
4. Compare headroom with outstanding downloads, repair/unpack requirements, concurrent jobs, cache growth and copies versus hardlinks. Unknown requirements mean `usable space remains; workload headroom unverified`, not an unconditional all-clear. Do not invent emergency thresholds.

## Correct arithmetic
- Available to ordinary applications: `f_bavail * f_frsize`.
- Free: `f_bfree * f_frsize`; used: `(f_blocks-f_bfree) * f_frsize`.
- Free but unavailable to ordinary users: `(f_bfree-f_bavail) * f_frsize`; commonly reserved space on ext4. Measure instead of assuming 5%. Do not label it automatically reclaimable.
- GNU df-style percentage for ordinary positive values: `ceil(100*used/(used+available))`. A 99.2% result displays as 100% while usable space remains. It does NOT become 100% merely because availability is below the reservation.
- Used/total capacity is a DIFFERENT denominator. Never compare it with df Use% to claim cleanup or refill.
- GB = 10^9 bytes; GiB = 2^30 bytes. Preserve raw bytes and labels. Never subtract ambiguous historical units and call the result exact.
- Zero available bytes, exhausted inodes, read-only mounts, missing mounts and application write errors are separate findings. Report only what is established.
- If `inodes_total` is zero, inode accounting may be unsupported (observed on some exFAT filesystems). Report inode availability as N/A, NOT exhausted. Zero available inodes indicates exhaustion only when the filesystem supplies meaningful inode accounting.

## Reconciling cleanup
Recover timestamped before/after evidence with units and filesystem identity. Memory is a historical claim, not a raw measurement. Without comparable snapshots, say the exact delta is unverified. Current cache size is NOT growth since cleanup. File mtime can be preserved or future-dated; birth time is supporting evidence, not tamper-proof provenance. Do not claim every byte is accounted for without a reconciled allocation history.

When the user challenges repeated storage alarms after a claimed fix, reconcile the previous action before raising another alarm. Distinguish actual bytes reclaimed from a service restart or configuration change; restored playback does not establish that storage was freed. Retract an unsupported prior claim plainly instead of recommending another cleanup or purchase.

## Deeper investigation only when needed
- Use bounded targeted `du -x -h --max-depth=1 PATH`; do not combine `-s` with `--max-depth=1`. Keep stderr/exit codes visible so failure cannot masquerade as empty output.
- Distinguish apparent file size from allocated blocks, especially sparse VFS cache files.
- De-duplicate device/inode pairs when totaling hardlinks across download/library trees. Separate du calls can count the same allocation twice.
- Check deleted-but-open files, permissions and quotas for df/du discrepancies; do not label the gap reclaimable without evidence.
- ISO/M2TS files are not inherently uncompressed waste, duplicates or disposable. Verify media-server file mapping, copies, allocation and user approval before deletion.
- An *arr root-folder list does not prove active routing. Inspect per-title paths, request defaults and download destinations. Deleting a root-folder entry is not a verified migration.

## Report
`PATH: X GiB available; df displays Y%; [mount/inode/read-only facts].` Then workload fit or `unverified`. Do not label positive availability simply FULL, or claim all services healthy from capacity alone. No remediation without authorization.

## Cache and pool attribution
1. Trace the application's container path through bind mounts and symlinks to the actual backing filesystem. Resolve the cache directory separately from the media path; they may consume different storage.
2. Identify what a named pool aggregates before proposing expansion. A mergerfs pool of remote debrid mounts is not the physical filesystem holding rclone's cache; adding a branch does not automatically enlarge that cache filesystem.
3. Read the full nested error before attributing failure to storage. A `failed to write to cache file` wrapper around an HTTP timeout reports an upstream fetch failure, not proof of local ENOSPC.
4. Treat a cache near its configured size target as a cache-policy observation, not exhausted disk capacity. Verify eviction behavior, active/open files, allocated bytes, and actual write failures before recommending a larger cache or disk.
5. Recommend additional capacity only after comparing verified usable space with a quantified workload requirement. Positive headroom with unknown demand remains unverified, not an emergency.
