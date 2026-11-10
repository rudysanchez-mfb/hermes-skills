#!/usr/bin/env python3
"""Read-only storage space checker.

Usage: check_storage.py PATH [PATH ...]

Emits one timestamped JSON record per path on stdout. Reads filesystem
statistics with os.statvfs only; it never writes to, creates, or deletes
anything on the paths it measures. The exit status is 0 when every path was
measured, and 1 when one or more paths could not be read (their error is
reported on stderr). No configuration file and no hard-coded paths are used;
every path to measure is supplied on the command line.
"""

import datetime
import json
import math
import os
import sys


def record(path):
    s = os.statvfs(path)
    b = s.f_frsize
    total, free, available = s.f_blocks * b, s.f_bfree * b, s.f_bavail * b
    used = total - free
    pct = 100 * used / (used + available) if used + available > 0 else None
    result = dict(
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        path=os.path.abspath(path),
        is_mount=os.path.ismount(path),
        total_bytes=total,
        used_bytes=used,
        available_bytes=available,
        available_GiB=round(available / 2**30, 3),
        free_unavailable_bytes=free - available,
        free_unavailable_GiB=round((free - available) / 2**30, 3),
    )
    result.update(
        total_used_pct=round(100 * used / total, 4) if total else None,
        df_style_pct=round(pct, 4) if pct is not None else None,
        df_style_display_pct=math.ceil(pct) if pct is not None else None,
        inodes_total=s.f_files,
        inodes_available=s.f_favail,
        read_only=bool(s.f_flag & os.ST_RDONLY),
    )
    return result


def main(argv):
    if len(argv) < 2:
        raise SystemExit("Usage: check_storage.py PATH [PATH ...]")
    status = 0
    for path in argv[1:]:
        try:
            print(json.dumps(record(path), sort_keys=True))
        except OSError as exc:
            status = 1
            error = dict(
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                path=os.path.abspath(path),
                error=str(exc),
            )
            print(json.dumps(error, sort_keys=True), file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
