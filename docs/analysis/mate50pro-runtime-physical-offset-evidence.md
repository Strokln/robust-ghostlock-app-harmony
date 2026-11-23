# DCO-AL00 — physical-address proof and native fallback correction

**Device:** Huawei Mate 50 Pro DCO-AL00, HarmonyOS 4.2.0.225(C00E182), kernel `5.10.136-gfdd4fb7e74b6-dirty`.

## Source-image evidence (offline)

Owner-supplied `boot_42.img`, SHA-256:
`96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf`

Recovered kallsyms from the exact kernel Image, whose link-address base is `0xffffffc010000000`:

| Symbol | Link address | Image-relative offset | On-disk initial u64 |
| --- | --- | --- | --- |
| `memstart_addr` | `0xffffffc01246abc0` | `0x246abc0` | `0xffffffffffffffff` |
| `kimage_voffset` | `0xffffffc01246abd0` | `0x246abd0` | `0x0000000000000000` |
| `kimage_vaddr` | `0xffffffc011830000` | `0x1830000` | `0xffffffc010000000` |

The initial `memstart_addr` is a sentinel, **not** the live physical DRAM start. It is initialized during boot. Likewise, `kimage_voffset=0` on disk is not the runtime value.

Owner-supplied `uefi_42.img`, SHA-256:
`8da097407c9d72786978e41de20fc76a5b338cd029494eba2668c928ed4586aa`

The embedded `[MemoryMap]` contains:
- `0x80000000, 0x00600000, "HYP"` — first listed DDR reservation
- `0xA8000000, 0x10000000, "Kernel"` — 256 MiB kernel reservation

This supports the bootloader's physical memory layout but **does not prove** `kernel_phys_offset` at runtime. In ARM64 this is tied to the boot-initialized `memstart_addr`. Neither `0xA8000000` nor `0x80000000` is automatically safe as the user profile's `kernel_phys_offset`.

## Source-code finding and fix

The native `src/core/memory/address_space.cpp` previously used `kernel::P0_PHYS_OFFSET` whenever `kernel_phys_offset` was missing, even on this exact DCO profile. An unverified fallback could give a wrong image-to-direct-map translation.

A narrowly scoped guard now rejects the exact Huawei kernel release when the parameter is unknown, with `errno=EINVAL`. All other Qualcomm releases retain existing behavior. A native host regression covers:
1. Missing DCO physical offset => reject.
2. Explicitly supplied physical offset => accept *as a configured value* (not proof that its numeric value is correct).

**Current status:** `kernel_phys_offset` remains **unverified**. The compile-time host test passes; no device exploitation, memory writes or root have been attempted with this change.

**Never flash these images or execute an incomplete GhostLock profile solely because its physical memory map contains a plausible DRAM base.**
