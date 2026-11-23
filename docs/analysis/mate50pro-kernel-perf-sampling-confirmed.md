# DCO-AL00: confirmed kernel-mode perf sampling on 2026-11-23

User-provided `mate50_perf_sampling_result.txt` (read-only ADB test):
- Target: HWDCO / DCO-AL00, HarmonyOS 4.2.0.225(C00E182), kernel `5.10.136-gfdd4fb7e74b6-dirty`.
- Mixed CPU clock samples: **712** = **502 kernel + 210 user**.
- Kernel-only CPU clock samples: **437** = **437 kernel + 0 user**.
- Combined: **1,149 samples** = **939 kernel + 210 user**.
- Every sample in both modes was marked `PERF_SAMPLE_REGS_ABI_64` (**1,149**).
- No `PERF_RECORD_LOST` notices, no hypervisor/guest samples.
- **Important limit:** all instruction pointer and register values were discarded, so this does not yet establish their validity, a KASLR slide, a write primitive or root.

The preceding, separate disabled-event ABI probe returned OK for all 5 event-attribute combinations. The current result is more substantial because actual sampling occurred while the performance events were enabled.

## New diagnostic: kernel IP plausibility

`tools/kernel_layout/mate50_perf_ip_classifier.c` samples the same two modes; for `PERF_RECORD_SAMPLE` records it inspects the IP transiently and outputs only counters:

- `kernel_ip_zero`: zero-valued kernel-labeled IPs;
- `kernel_ip_nonzero`: nonzero kernel-labeled IPs;
- `kernel_ip_image_region`: kernel-labeled IPs whose upper 32 bits are `0xffffffc0` (a **heuristic** for the currently studied ARM64 image, not a semantic validation);
- `kernel_ip_all_ones`, `kernel_ip_other`: placeholders or addresses outside that heuristic;
- `kernel_regs64`, `kernel_x0_nonzero`: records with 64-bit register ABI and transiently nonzero x0.

Raw addresses, other registers and x0 values are **never printed or written to disk**. The values are briefly held in the on-device perf ring and local CPU registers for classification, then the mapping is closed. The probe does not calculate KASLR slide, exploit a race, write kernel memory, or load KernelSU.

**Caveats:** Positive nonzero addresses in the expected high address range are necessary but not sufficient to show a usable kernel-address leak. `x0` may contain any argument, including zero. The classifier is a diagnostic only and has not yet been executed on the user's actual handset.

The macOS user archive `Mate50PerfIPCheck.zip` contains the prebuilt static ARM64 ELF, C source, SHA-pinned ADB runner and Russian README.
