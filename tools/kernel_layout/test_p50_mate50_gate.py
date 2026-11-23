#!/usr/bin/env python3
"""Self-contained offline CI tests; no device and no exploit binary required."""
import contextlib
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path

from p50_mate50_gate import audit, main


class CompatibilityGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path = Path(self.tmp.name)
        self.elf = path / "p50"
        hdr = bytearray(64)
        hdr[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<H", hdr, 18, 183)
        self.elf.write_bytes(hdr)
        self.boot = path / "boot.img"
        self.boot.write_bytes(b"offline-test-data-only")
        self.profile = path / "dco.conf"
        self.profile.write_text('release = "5.10.136-gfdd4fb7e74b6-dirty"\ncred { copy_size = null }\n')
        self.layout = path / "layout.json"
        self.layout.write_text(json.dumps({
            "kernel_release": "5.10.136-gfdd4fb7e74b6-dirty",
            "task_struct": {"fields": {"real_cred": 1944, "cred": 1952, "comm": 1968}}
        }))

    def test_refuses_unverified_target(self):
        result = audit(self.elf, self.boot, self.profile, self.layout)
        self.assertEqual(result["status"], "NOT_PORTED")
        self.assertFalse(result["safe_to_execute_p50_binary_on_mate50"])
        self.assertFalse(result["kernel_exact_match"])
        self.assertFalse(result["boot_matches_researched_image"])
        self.assertFalse(result["struct_offsets"]["cred"]["equal"])

    def test_cli_returns_blocked_status(self):
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            code = main([self.elf, self.boot, self.profile, self.layout])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stream.getvalue())["status"], "NOT_PORTED")

    def test_refuses_kernel_metadata_mismatch(self):
        self.layout.write_text(json.dumps({
            "kernel_release": "5.4.86",
            "task_struct": {"fields": {"cred": 1952}}
        }))
        with self.assertRaisesRegex(ValueError, "different kernels"):
            audit(self.elf, self.boot, self.profile, self.layout)

    def test_refuses_non_aarch64(self):
        hdr = bytearray(64)
        hdr[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<H", hdr, 18, 62)
        self.elf.write_bytes(hdr)
        with self.assertRaisesRegex(ValueError, "AArch64"):
            audit(self.elf, self.boot, self.profile, self.layout)


if __name__ == "__main__":
    unittest.main()
