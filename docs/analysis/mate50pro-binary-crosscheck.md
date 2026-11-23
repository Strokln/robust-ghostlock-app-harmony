# Huawei Mate 50 Pro — independent static binary cross-check

The owner-provided DCO-AL00 Android boot image for kernel 5.10.136-gfdd4fb7e74b6-dirty was checked against the earlier header-derived task_struct and cred layout study.

- Boot SHA-256: 96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf
- Extracted ARM64 Image SHA-256: 03537d7f14ad9b44e70a9565115e529d76893328a0ff708034038a5eb958237c
- Android boot v4: ARM64 Image starts at byte 4096 (0x1000), length 44,954,580 bytes.
- Static virtual image base inferred: 0xffffffc010000000.

## Read-only binary verification: 14/14 PASS

1. Static image base derived from the compiled init_task.real_cred pointer matches 0xffffffc010000000.
2. init_task.cred points to init_cred, VA 0xffffffc012775bd8.
3. init_task.real_cred points to the same init_cred.
4. init_task.tasks.next is a self-reference to 0xffffffc01275b5e0.
5. init_task.tasks.prev is the same self-reference.
6. init_task.sched_task_group targets root_task_group, VA 0xffffffc012989f00.
7. init_task.comm is "swapper".
8. init_cred.usage is 4.
9. init_cred.uid is 0.
10. init_cred.cap_inheritable is 0.
11. init_cred.cap_ambient is 0.
12. init_cred.cap_permitted, cap_effective and cap_bset match (0x3ffffffffff).
13. init_task.normal_prio is 120.
14. init_task.prio is 120.

Validation rejects an image with a changed SHA-256; a single-byte mutation was tested and correctly rejected. The verifier reads only the boot image and profile; it never touches a running device.

## What remains unverified

The original imported profile has 24 null fields. The earlier kheaders probe estimated 8 missing task_struct fields, but exact live kernel equivalence is not established. The selected select_stack route, exploit-specific cred reference and repair values, runtime relocation, SELinux effects, and root outcome remain **unverified**. This static cross-check does not validate a writable GhostLock profile, prove exploitability, or justify device execution.

**Status: STATIC IMAGE LAYOUT CORROBORATED. NOT ROOTED. NOT A RUNNABLE PROFILE.**

The full replayable read-only verification script and JSON results have been delivered to the device owner in this conversation as a ZIP file.
