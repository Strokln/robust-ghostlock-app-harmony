# Mate 50 Pro DCO-AL00 — rt_mutex_waiter binary layout verified

**Scope:** static disassembly of the exact, owner-provided Android 12 HarmonyOS 4.2.0.225(C00E182) `boot_42.img`, kernel `5.10.136-gfdd4fb7e74b6-dirty`; NO ON-DEVICE EXPLOITATION.

SHA-256 of `boot_42.img`: `96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf`.

SHA-256 of the extracted ARM64 kernel Image: `03537d7f14ad9b44e70a9565115e529d76893328a0ff708034038a5eb958237c`.

The kernel has `CONFIG_KALLSYMS_BASE_RELATIVE=y` and `CONFIG_KALLSYMS_ALL=y`. Parsed its actual compressed symbol table: **173,179 names**. The embedded relative-address base `0xffffffc010000000` independently reproduced the expected `init_task` and `init_cred` offsets. Constructed a fully symbolized ELF64 AArch64 wrapper and disassembled target functions with LLVM 17.

## Extracted `rt_mutex_waiter` geometry

| Member | Byte offset | Machine-code evidence |
|---|---:|---|
| tree_entry | 0x00 | RBT node and `rb_erase` operations |
| pi_tree_entry | 0x18 | `rt_mutex_init_waiter` and `remove_waiter` |
| task | 0x30 | `task_blocks_on_rt_mutex`: `stp x20,x19,[x22,#0x30]` |
| lock | 0x38 | Same paired store; `remove_waiter`: `ldr x8,[x22,#0x38]` |
| major_prio | 0x40 | `str wzr,[x22,#0x40]` and `str w8,[x22,#0x40]` |
| major_only | 0x44 | `str w8,[x22,#0x44]` |
| prio | 0x48 | `str w8,[x22,#0x48]` |
| deadline | 0x50 | `str x8,[x22,#0x50]` |

**Size 0x58 (88 bytes) is inferred** from the highest observed field end and standard ARM64 alignment, assuming no further fields. The field offsets themselves are evidenced by compiled instructions. Not a DWARF `sizeof` measurement.

**Unexpected positive portability result:** These offsets, including the Huawei-specific major-priority fields, MATCH the P50 Pro 5.4.86 port's `exploit/src/target.h` description. Other kernel-specific absolute addresses and execution assumptions do not match.

## Independently recovered symbol entry points

- `rt_mutex_init_waiter`: `0xffffffc0101ca2f0`
- `__rt_mutex_start_proxy_lock`: `0xffffffc0101ca7fc`
- `task_blocks_on_rt_mutex`: `0xffffffc0101cabc0`
- `rt_mutex_start_proxy_lock`: `0xffffffc0101cb074`
- `remove_waiter`: `0xffffffc0101cb124`
- `rt_mutex_cleanup_proxy_lock`: `0xffffffc0101cb508`

## Observed behavior of `remove_waiter`

The ARM64 image contains `mrs x20, SP_EL0` at `0xffffffc0101cb160` (kernel `current`), `add x21,x20,#0x88c` at +4 (`task_struct.pi_lock`), `str xzr,[x20,#0x8b8]` at `0xffffffc0101cb1a8` (`pi_blocked_on`), and `mov x5,x20` before the priority-chain call. This corroborates the old, pre-fix implementation of CVE-2026-43499 in the static file; it does **not** prove that privilege escalation is reachable on the running phone.

Eleven exact address/instruction checks passed in the offline bundle. All kernel binary bytes remain local to the user; the public repository contains only results and reproducible read-only scripts.

**Status:** `WAITER_LAYOUT_STATICALLY_VERIFIED`. No validated `select_stack` execution, credential repair or root method. Do not copy P50 binaries or source-defined kernel addresses into a runnable DCO profile.

Local artifact assembled for the owner: `Mate50Pro_DCOAL00_Symbolized_Ghidra.zip` (ELF, full symbol map, disassembly and SHA-pinned scripts).
