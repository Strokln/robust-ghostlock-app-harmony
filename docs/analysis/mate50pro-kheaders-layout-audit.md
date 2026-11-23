# Mate 50 Pro / HWDCO: offline ARM64 kernel layout audit (2026-11-23)

**State: research evidence only; NOT an importable or validated GhostLock profile.**
No exploit was executed, no device memory was read or changed.

## Exact input evidence

- Device: Huawei Mate 50 Pro, DCO-AL00 / HWDCO.
- Kernel: `5.10.136-gfdd4fb7e74b6-dirty` (from original `include/generated/utsrelease.h`).
- `boot_42.img` SHA-256: `96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf`.
- Embedded `kheaders.tar.xz` SHA-256: `438a08fe8e793c490567b578d742bbe62fefb8638ccc780872bb4de8e2ec8f79`.
- Source of comparison: user-supplied `K5.10.136-gfdd4fb7e74b6-dirty.conf`.
- Running kernel compilation banner: Android Clang 12.0.5; offline cross-compiler: Clang 17.0.0, target `aarch64-linux-gnu`.
- This is a **compile-time estimate** from the original headers, using `__builtin_offsetof` and `sizeof`, not a measurement from a running kernel.

`CONFIG_DEBUG_INFO_DWARF4=y` is configured, but the raw ARM64 boot image is not a DWARF `vmlinux`. There is no `CONFIG_DEBUG_INFO_BTF=y` in the attached configuration.

## `task_struct` offsets, bytes

| Field | From headers | Previously supplied profile |
|---|---:|---:|
| `prio` | 332 | 332 |
| `normal_prio` | 340 | 340 |
| `sched_task_group` | 1040 | 1040 |
| `pi_lock` | 2188 | null |
| `pi_waiters` | 2208 | null |
| `pi_top_task` | 2224 | null |
| `pi_blocked_on` | 2232 | null |
| `pid` | 1504 | null |
| `tgid` | 1508 | null |
| `atomic_flags` | 1448 | null |
| `real_cred` | 1944 | 1944 |
| `cred` | 1952 | 1952 |
| `comm` | 1968 | 1968 |
| `tasks` | 1248 | null |
| `seccomp` | 2152 | 2152 |

Computed `sizeof(struct task_struct)`: **4992 (0x1380)**. **All seven prefilled `task_struct` offsets match** the ARM64 header-derived estimates. The other eight were null.

## `cred` layout (not a usable credential-template)

Computed `sizeof(struct cred)`: **168 (0xa8)**. Fields from original `linux/cred.h`:

- `usage`: offset 0, size 4 bytes
- `uid`: offset 4
- `cap_inheritable`: 40
- `cap_permitted`: 48
- `cap_effective`: 56
- `cap_bset`: 64
- `cap_ambient`: 72
- `security`: 120
- `sizeof(kernel_cap_t)`: 8

These are C layout facts, **not** an independent check of GhostLock's `cred.copy_size`, `cred.caps_count`, `cred.caps_value`, `cred.ref_count`, or `cred.refN_image` semantics. The complete original profile contains **24 explicit null values**.

## Reproduction

Compile `tools/kernel_layout/mate50_layout_probe.c` against the extracted headers with AArch64 Clang, the exact archive's `include/generated/autoconf.h`, `-D__KERNEL__`, `-nostdinc`, the Clang resource headers and the standard kernel ARM64 include paths. Read `.xword` constants in the emitted `-S -O0` assembly.

**Caveat:** `include/linux/cred.h` includes `linux/key.h` → `linux/rwsem.h`, which refers to two vendor files absent from the published archive:
`chipset_common/hwqos/hwqos_rwsem.h` and `chipset_common/hwcfs/hwcfs_rwsem.h`.
For this *offline probe only*, compilation used two empty temporary include shims. Original headers were untouched. The shims may conceal vendor definitions, so this procedure cannot certify a production binary layout. `task_struct` was also separately compiled with no shims, using only `linux/sched.h`, and the tested offsets agree.

## Status and remaining unknowns

1. Seven original `task_struct` values match, but **all computed values still require confirmation against the actual firmware binary or running kernel**.
2. The base profile still lacks credible, verified reference-repair values and proof that its selected `select_stack` route is viable.
3. `kernel_phys_offset` is not determined from these headers.
4. No evidence exists of successful root or safe kernel-memory modification on this DCO-AL00 firmware.

**Do not auto-import generated geometry or enable execution based solely on this report.**
