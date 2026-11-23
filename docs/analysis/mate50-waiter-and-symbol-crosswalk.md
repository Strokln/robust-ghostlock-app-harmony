# Mate 50 Pro 4.2.0.225 — offline GhostLock kernel reverse-engineering update

Scope: static, read-only analysis of the exact supplied `boot_42.img` (SHA-256 `96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf`), DCO-AL00, kernel `5.10.136-gfdd4fb7e74b6-dirty`.

## Concrete findings

- Extracted **173,179** `CONFIG_KALLSYMS_BASE_RELATIVE` symbols and built a research ELF64 AArch64 wrapper for Ghidra.
- Disassembled `task_blocks_on_rt_mutex` and `remove_waiter` with LLVM.
- Verified the following `rt_mutex_waiter` *field offsets*, which **match P50 Pro**: tree_entry 0x00, pi_tree_entry 0x18, task 0x30, lock 0x38, major_prio 0x40, major_only 0x44, prio 0x48, deadline 0x50. Inferred object size **0x58 (88)** from fields plus ARM64 ABI; no authoritative vendor type debug-info.
- In `remove_waiter`, `mrs x20,SP_EL0` at `0xffffffc0101cb160` precedes `str xzr,[x20,#0x8b8]` at `0xffffffc0101cb1a8`. This is evidence of the old current-task handling pattern in the static image, **not** a runtime exploit test.
- For 23 P50 `target.h` anchor names/fields chosen for a crosswalk, 14 map directly by name to Mate 50 Pro `kallsyms`, while 9 map **only to parent symbols** with inner-field offsets still unverified. Found name ≠ validated equivalent behavior.

Selected ELF symbol locations (static Image VA, **NOT runtime KASLR addresses**):
- `init_task` 0xffffffc01275b100
- `init_cred` 0xffffffc012775bd8
- `__schedule` 0xffffffc011801ac0
- `do_futex` 0xffffffc01022cdbc
- `__arm64_sys_futex` 0xffffffc01023023c
- `random_table` 0xffffffc01289bdb8
- `sysctl_bootid` 0xffffffc0129df039
- `selinux_state` 0xffffffc0129d2a48
- `runqueues` 0xffffffc0127230c0

## Boundaries / unverified

Kernel runtime address derivation, exact semantics of sysctl table entries and user-visible perf samples, memory-write exploit reliability, `cred` reference repair, system recovery, and root/KernelSU outcome remain **unverified**.

Do not import these symbolic coordinates as an executable GhostLock profile. Do not run the P50 binary on DCO-AL00. This change records static analysis only and changes no app or native exploit logic.
