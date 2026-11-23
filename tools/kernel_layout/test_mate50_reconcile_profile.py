import unittest
from mate50_reconcile_profile import BOOT_SHA256, reconcile

PROFILE = '''release = "5.10.136-gfdd4fb7e74b6-dirty"
kernel_phys_load = { HWDCO = 2818572288 }
kernel_phys_offset = null
task_struct {
  pi_lock = null
  pi_waiters = null
  pi_top_task = null
  pi_blocked_on = null
  pid = null
  tgid = null
  atomic_flags = null
  tasks = null
}
cred {
  usage_offset = null
}
'''

class ReconcilerTests(unittest.TestCase):
    def test_reconciles_only_verified_task_fields(self):
        updated, audit = reconcile(PROFILE, BOOT_SHA256)
        self.assertEqual(len(audit["filled_task_struct_fields"]), 8)
        self.assertIn("pi_lock = 2188", updated)
        self.assertIn("tasks = 1248", updated)
        self.assertIn("kernel_phys_offset = null", updated)
        self.assertIn("usage_offset = null", updated)
        self.assertIn("NOT VERIFIED FOR ROOT", updated)
        self.assertEqual(audit["remaining_null_count"], 2)

    def test_rejects_nonmatching_boot(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            reconcile(PROFILE, "0" * 64)

    def test_rejects_wrong_release(self):
        with self.assertRaisesRegex(ValueError, "kernel release"):
            reconcile(PROFILE.replace("5.10.136-", "5.4.86-"), BOOT_SHA256)

    def test_rejects_conflicting_existing_offset(self):
        with self.assertRaisesRegex(ValueError, "contradictory"):
            reconcile(PROFILE.replace("pi_lock = null", "pi_lock = 999"), BOOT_SHA256)

    def test_no_overwriting_matching_offsets(self):
        updated, audit = reconcile(PROFILE.replace("pi_lock = null", "pi_lock = 2188"), BOOT_SHA256)
        self.assertIn("pi_lock = 2188", updated)
        self.assertNotIn("pi_lock", audit["filled_task_struct_fields"])

if __name__ == "__main__":
    unittest.main()
