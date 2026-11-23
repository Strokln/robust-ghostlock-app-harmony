# DCO-AL00: perf sample IP-range follow-up

## Confirmed on-device result (owner-supplied, November 23, 2026)

Source: `mate50_perf_ip_result.txt` produced by the v2 read-only classifier, HWDCO, HarmonyOS 4.2.0.225(C00E182), kernel `5.10.136-gfdd4fb7e74b6-dirty`.

| Property | Mixed mode | Kernel only |
|---|---:|---:|
| All samples | 540 | 328 |
| Kernel-labeled samples | 383 | 328 |
| User-labeled samples | 157 | 0 |
| Nonzero kernel IPs | 383 | 328 |
| Kernel IPs in `0xffffffc0xxxxxxxx` prefix | 0 | 0 |
| 64-bit registers ABI | 540 | 328 |
| Nonzero x0 in kernel-labeled records | 383 | 328 |
| Lost records | 0 | 0 |

**Interpretation:** the perf ring delivered 711 kernel-labeled, nonzero IPs but none matched our narrowly assumed static kernel-image high-32-bit prefix. This is an unresolved contradiction, NOT a verified bypass of KASLR. The underlying reasons could include valid runtime mappings outside the assumed prefix, stripped/modified IP values, or an incorrect assumption in the diagnostic.

## v3 diagnostic

`tools/kernel_layout/mate50_perf_ip_range_classifier.c` extends v2 to show privacy-preserving aggregate counters:

- high 16 bits all ones vs other values;
- any suspicious small sentinel values;
- 4-byte address alignment expected from AArch64 instruction addresses;
- count of consecutive changes in kernel-labeled IP values;
- canonical high-16 values outside the previously tested image prefix.

The ring-buffer records and IPs remain local, and the classifier prints no raw IP/register values. The tool neither computes the KASLR slide nor modifies kernel memory, boot state, SELinux, or privilege state.

The owner receives the independently compiled v3 prebuilt and macOS runner in `Mate50PerfIPRangeCheck.zip`.

**Status:** v2 result confirmed. v3 binary compiled successfully offline and ZIP verified; no v3 on-device test yet. Even a positive v3 cannot establish a correct KASLR slide or successful GhostLock root.
