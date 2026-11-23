# DCO-AL00: why the extractor omitted verifiable init_cred data

**Device/kernel:** Huawei Mate 50 Pro DCO-AL00, HarmonyOS 4.2.0.225(C00E182), kernel `5.10.136-gfdd4fb7e74b6-dirty`.

**Exact boot image SHA-256:** `96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf`.

The existing extractor has a no-BTF, image-based `structs::derive_cred_layout_5_10` implementation. However, `main.rs` only calls it when the kernel matches a measured Android-GKI `series_matched` branch. Huawei's vendor release has no `-android12-9-` suffix; `dirty.conf` therefore emitted 16 `null` credential entries despite the original image containing recognizable init_cred data.

## Verified static observations

`init_cred` was recovered from the embedded kallsyms at image-relative offset `41376728` (`0x2775bd8`). Across its 168-byte C-header-derived extent:

- `usage` at byte 0 is 4 in the static initial credential.
- Linux capability run (all 64-bit slots): `cap_inheritable` byte 40 is zero, `cap_permitted` byte 48, `cap_effective` byte 56 and `cap_bset` byte 64 each contain `0x3ffffffffff`, `cap_ambient` byte 72 is zero.
- The three unambiguously symbol-resolved pointer fields at offsets **128, 136, 144** point respectively to **`root_user`**, **`init_user_ns`**, **`init_groups`**.

These are facts about the owner-supplied **on-disk image**, NOT evidence that runtime security contexts or reference counts can be safely rewritten in the live kernel.

## Code change

Allow the existing `derive_cred_layout_5_10` path when the exact DCO kernel release is seen; for an unmatched release series, **do not fall back to `family::cred_from_image` GKI template constants**. The image pattern must match, or the credential fields stay unresolved.

A separate native guard already blocks this same DCO kernel when `kernel_phys_offset` has not been independently verified. No functional root, module loading, SELinux alteration or new on-device exploitation is claimed.

## Risks still unresolved

- Runtime `memstart_addr` / `kernel_phys_offset` (the on-disk `memstart_addr` is a sentinel `0xffffffffffffffff`).
- Kernel address disclosure translated correctly to the live image.
- The `select_stack` write sequence and reference-count repair have not been exercised safely on this target.
- `lock_anchor_image` suitability is not yet proven.

This is a **generator compatibility fix based on verified static image structure**, not a complete working exploit.
