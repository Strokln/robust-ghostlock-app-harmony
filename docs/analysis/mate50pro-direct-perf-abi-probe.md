# Mate 50 Pro: direct perf_event_open ABI probe

**Read-only diagnostic, not an exploit.** Target: Huawei DCO-AL00, kernel
5.10.136-gfdd4fb7e74b6-dirty, Android 12 / HarmonyOS 4.2.

The probe opens a software CPU-clock perf event five times, with differing
sample_type and exclude_kernel settings:

1. User-space counting
2. User-space PERF_SAMPLE_IP
3. User-space PERF_SAMPLE_REGS_INTR (x0)
4. PERF_SAMPLE_IP with kernel events included
5. PERF_SAMPLE_REGS_INTR with kernel events included (x0)

Each opened event has **disabled=1**, is closed immediately, and is never enabled,
mapped or read. The tool does **not** extract kernel addresses/registers, write
kernel memory, exploit GhostLock, load a module, or change SELinux policy.

A positive open result means only that the kernel **accepted the event
attributes**. It does not prove that kernel IPs can actually be sampled,
that KASLR can be bypassed, or that the phone is exploitable.

## Build

On an LLVM Clang + LLD Linux host, run:

    bash tools/kernel_layout/build_mate50_perf_probe.sh

Cross-target is aarch64-linux-android31, no NDK or libc. The output is a static
ELF64 AArch64 binary. Verified with Clang 17, ELF readelf and LLVM objdump.

## Run on Android

    adb push mate50_perf_event_probe_arm64 /data/local/tmp/
    adb shell chmod 755 /data/local/tmp/mate50_perf_event_probe_arm64
    adb shell /data/local/tmp/mate50_perf_event_probe_arm64

The device-owner has a prepared ZIP with the validated prebuilt binary and
macOS runner:

    bash run_perf_probe_mac.sh

The runner writes only the temporary binary to /data/local/tmp and saves
its console output on the Mac as mate50_perf_probe_result.txt.

## Expected diagnostic codes

- OK: event attributes accepted; no actual sampling was performed
- errno=1 / EPERM, errno=13 / EACCES: permissions/security policy
- errno=22 / EINVAL: unsupported or invalid parameters
- errno=38 / ENOSYS: syscall unavailable

The on-device runtime result has not been measured; any conclusion about
kernel sample availability would be premature.
