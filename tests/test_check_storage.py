"""Stdlib-only tests for storage-space-check's check_storage.py.

Run with:

    python3 -m unittest discover -s tests -v

These exercise the record arithmetic with a faked ``os.statvfs`` (so exact
filesystem shapes are reproducible) and the CLI exit codes by running the
script in a subprocess. They never write to or delete anything on the paths
they measure.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(
    HERE, os.pardir, "skills", "storage-space-check", "scripts", "check_storage.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("check_storage_under_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _statvfs(frsize=4096, blocks=1000, bfree=100, bavail=80, files=1000,
             favail=900, flags=0):
    """A minimal stand-in for the object os.statvfs() returns."""
    return types.SimpleNamespace(
        f_bsize=frsize,
        f_frsize=frsize,
        f_blocks=blocks,
        f_bfree=bfree,
        f_bavail=bavail,
        f_files=files,
        f_ffree=favail,
        f_favail=favail,
        f_flag=flags,
        f_namemax=255,
    )


class RecordArithmeticTests(unittest.TestCase):
    def setUp(self):
        self.mod = _load_module()
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _record(self, fake):
        with mock.patch.object(self.mod.os, "statvfs", return_value=fake):
            return self.mod.record(self.dir)

    def test_rounded_100_percent_with_positive_available(self):
        # used = (1000-10)*4096 = 4_055_040; available = 5*4096 = 20_480
        # df-style pct = 100*used/(used+available) = 99.497...% -> displays as 100
        fake = _statvfs(blocks=1000, bfree=10, bavail=5)
        rec = self._record(fake)
        self.assertGreater(rec["available_bytes"], 0)
        self.assertEqual(rec["available_bytes"], 5 * 4096)
        self.assertEqual(rec["df_style_display_pct"], 100)
        self.assertLess(rec["df_style_pct"], 100.0)

    def test_zero_inode_totals(self):
        fake = _statvfs(files=0, favail=0)
        rec = self._record(fake)
        self.assertEqual(rec["inodes_total"], 0)
        self.assertEqual(rec["inodes_available"], 0)

    def test_reserved_blocks_and_read_only(self):
        # bfree=100, bavail=80 -> 20 blocks reserved (free but not available)
        fake = _statvfs(bfree=100, bavail=80, flags=os.ST_RDONLY)
        rec = self._record(fake)
        self.assertEqual(rec["available_bytes"], 80 * 4096)
        self.assertEqual(rec["free_unavailable_bytes"], 20 * 4096)
        self.assertEqual(rec["free_unavailable_GiB"], round(20 * 4096 / 2**30, 3))
        self.assertIs(rec["read_only"], True)

    def test_not_read_only_by_default(self):
        rec = self._record(_statvfs(flags=0))
        self.assertIs(rec["read_only"], False)

    def test_run_reads_only_never_writes(self):
        # Snapshot the fixture dir, measure it, snapshot again: no change.
        path = os.path.join(self.dir, "probe")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("x")
        before = sorted(os.listdir(self.dir))
        self.mod.record(self.dir)
        after = sorted(os.listdir(self.dir))
        self.assertEqual(before, after)


class CommandLineExitTests(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            capture_output=True,
            text=True,
        )

    def test_missing_path_exits_nonzero(self):
        missing = os.path.join(tempfile.mkdtemp(), "definitely-not-here")
        proc = self._run(missing)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("No such file", proc.stderr)

    def test_no_args_exits_nonzero_with_usage(self):
        proc = self._run()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Usage", proc.stderr)

    def test_valid_path_prints_json_and_exits_zero(self):
        proc = self._run(tempfile.gettempdir())
        self.assertEqual(proc.returncode, 0)
        record = json.loads(proc.stdout)
        self.assertIn("available_bytes", record)


if __name__ == "__main__":
    unittest.main()
