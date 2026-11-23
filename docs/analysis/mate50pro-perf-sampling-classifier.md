# Huawei Mate 50 Pro: on-device perf event confirmation and read-only sample classifier

Device: DCO-AL00 / HWDCO, kernel 5.10.136-gfdd4fb7e74b6-dirty, HarmonyOS 4.2.0.225(C00E182).

Owner-supplied diagnostic, November 23, 2026: **5 of 5 perf_event_open calls returned OK**, including PERF_SAMPLE_IP and PERF_SAMPLE_REGS_INTR with kernel events included. Events were DISABLED and immediately closed. This proves that the kernel accepts these configurations, not that kernel IPs or privileged registers are actually available.

Previous simpleperf testing also confirmed ordinary user-space samples from /system/bin/sh and libc.so.

## New read-only probe

tools/kernel_layout/mate50_perf_sampling_classifier.c

It enables two short (~1.2s) CPU-clock events and classifies PERF_RECORD_SAMPLE records based on perf_event_header.misc. It counts records with a 64-bit register ABI but deliberately discards all instruction pointer and register values without printing or persisting them. It uses only standard syscalls and a short getpid workload; no kernel-memory modification, CVE trigger, bootloader operation or root functionality.

Build on LLVM Clang + LLD:

    clang --target=aarch64-linux-android31 -ffreestanding -nostdlib -static -fno-stack-protector -O2 -fno-builtin -fno-pic -fuse-ld=lld -Wl,-e,_start -Wl,-z,max-page-size=4096 -Wl,--build-id=none tools/kernel_layout/mate50_perf_sampling_classifier.c -o mate50_perf_sampling_classifier_arm64

Then transfer via adb push, chmod 700, run through adb shell.

Interpretation:
- samples>0: actual sample records reached the ring buffer.
- kernel>0: some records are kernel-labeled (NOT proof of exposed kernel IP/KASLR).
- regs_abi64>0: a sample declares the 64-bit interrupt-register ABI.
- kernel=0: can be due to lack of kernel samples within the short recording window, not necessarily a hard security block.

Prebuilt ARM64 ELF and macOS launch script are available to the owner in the conversation archive Mate50PerfSamplingCheck.zip. Local ELF inspection and Clang -Wall/-Wextra/-Werror compilation passed, but this new executable has **not been tested on the user's actual phone**. **No root outcome is claimed.**
