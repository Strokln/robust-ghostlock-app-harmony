#!/usr/bin/env python3
"""Negative-path tests do not require proprietary firmware in CI."""
import unittest

from mate50_kallsyms_extract import (
    BASE, BOOT_HASH, IMAGE_HASH, main, recover,
)

class Mate50SymbolRecoveryTests(unittest.TestCase):
    def test_exact_kernel_metadata(self):
        self.assertEqual(BASE, 0xffffffc010000000)
        self.assertEqual(len(BOOT_HASH), 64)
        self.assertEqual(len(IMAGE_HASH), 64)

    def test_rejects_wrong_boot_image(self):
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            recover(bytes(4096))

    def test_rejects_missing_arguments(self):
        self.assertEqual(main([]), 64)

if __name__ == "__main__":
    unittest.main()
