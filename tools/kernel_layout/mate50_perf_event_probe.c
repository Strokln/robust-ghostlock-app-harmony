/*
 * Huawei Mate 50 Pro / HarmonyOS 4.2 -- read-only perf_event_open ABI probe.
 *
 * ARM64 Android static executable; no libc, root, KASLR data, or kernel writes.
 * Opens DISABLED per-thread perf events and immediately closes each descriptor.
 * Does NOT mmap the ring buffer, enable sampling, or read IP/register values.
 * Exit status 0 means diagnostic completed, not that KASLR information leaked.
 */
typedef unsigned long long u64;
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned long usize;

/* Linux perf_event_attr ABI through PERF_ATTR_SIZE_VER5 (112 bytes). */
struct perf_attr {
    u32 type;                 /* +0  */
    u32 size;                 /* +4  */
    u64 config;               /* +8  */
    u64 sample_period;        /* +16 */
    u64 sample_type;          /* +24 */
    u64 read_format;          /* +32 */
    u64 flags;                /* +40 */
    u32 wakeup_events;        /* +48 */
    u32 bp_type;              /* +52 */
    u64 bp_addr;              /* +56 */
    u64 bp_len;               /* +64 */
    u64 branch_sample_type;   /* +72 */
    u64 sample_regs_user;     /* +80 */
    u32 sample_stack_user;    /* +88 */
    u32 clockid;              /* +92 */
    u64 sample_regs_intr;     /* +96 */
    u32 aux_watermark;       /* +104 */
    u16 sample_max_stack;    /* +108 */
    u16 reserved;            /* +110 */
};
_Static_assert(sizeof(struct perf_attr) == 112, "kernel ABI size mismatch");

#define NR_WRITE 64
#define NR_CLOSE 57
#define NR_PERF_EVENT_OPEN 241
#define NR_EXIT_GROUP 94
#define PERF_TYPE_SOFTWARE 1
#define PERF_COUNT_SW_CPU_CLOCK 0
#define PERF_SAMPLE_IP (1ULL << 0)
#define PERF_SAMPLE_REGS_INTR (1ULL << 18)
#define PERF_FLAG_DISABLED (1ULL << 0)
#define PERF_FLAG_EXCLUDE_USER (1ULL << 4)
#define PERF_FLAG_EXCLUDE_KERNEL (1ULL << 5)
#define PERF_FLAG_EXCLUDE_HV (1ULL << 6)

static inline long syscall5(long nr, long a0, long a1, long a2, long a3, long a4) {
    register long x0 asm("x0") = a0;
    register long x1 asm("x1") = a1;
    register long x2 asm("x2") = a2;
    register long x3 asm("x3") = a3;
    register long x4 asm("x4") = a4;
    register long x8 asm("x8") = nr;
    asm volatile ("svc #0" : "+r"(x0) : "r"(x1), "r"(x2), "r"(x3), "r"(x4), "r"(x8) : "memory");
    return x0;
}
static inline long write1(const char *s, usize n) {
    return syscall5(NR_WRITE, 1, (long)s, (long)n, 0, 0);
}
static usize length(const char *s) {
    usize i = 0;
    while (s[i]) ++i;
    return i;
}
static void puts0(const char *s) { (void)write1(s, length(s)); }
static void unsigned_num(u64 v) {
    char buf[24];
    usize i = sizeof(buf);
    do {buf[--i] = '0' + (char)(v % 10); v /= 10;} while (v && i);
    (void)write1(buf + i, sizeof(buf) - i);
}
static void status(long fd) {
    if (fd >= 0) {
        puts0("OK (event descriptor opened, no sampling performed)");
        (void)syscall5(NR_CLOSE, fd, 0, 0, 0, 0);
    } else {
        puts0("FAIL errno=");
        unsigned_num((u64)(-fd));
        switch (-fd) {
            case 1:  puts0(" (EPERM)"); break;
            case 13: puts0(" (EACCES)"); break;
            case 22: puts0(" (EINVAL)"); break;
            case 38: puts0(" (ENOSYS)"); break;
            case 95: puts0(" (EOPNOTSUPP)"); break;
            case 24: puts0(" (EMFILE)"); break;
            default: break;
        }
    }
    puts0("\n");
}
static void test(const char *name, u64 sample_type, u64 flags, u64 regs) {
    struct perf_attr a = {0};
    a.type = PERF_TYPE_SOFTWARE;
    a.size = sizeof(a);
    a.config = PERF_COUNT_SW_CPU_CLOCK;
    a.sample_period = sample_type ? 100000 : 0;
    a.sample_type = sample_type;
    a.flags = PERF_FLAG_DISABLED | PERF_FLAG_EXCLUDE_HV | flags;
    a.sample_regs_intr = regs;
    puts0(name); puts0(": ");
    /* pid=0 = calling thread, cpu=-1 = any CPU, group=-1, flags=0 */
    status(syscall5(NR_PERF_EVENT_OPEN, (long)&a, 0, -1, -1, 0));
}
void _start(void) {
    puts0("MATE50 PERF ABI PROBE v1 (ARM64, no root, read-only)\n");
    puts0("Each event is disabled and closed; NO kernel IP or registers read.\n");
    test("1) cpu-clock counter (user)", 0, PERF_FLAG_EXCLUDE_KERNEL, 0);
    test("2) PERF_SAMPLE_IP (user)", PERF_SAMPLE_IP, PERF_FLAG_EXCLUDE_KERNEL, 0);
    test("3) PERF_SAMPLE_REGS_INTR (user, x0)", PERF_SAMPLE_IP|PERF_SAMPLE_REGS_INTR, PERF_FLAG_EXCLUDE_KERNEL, 1);
    test("4) PERF_SAMPLE_IP (kernel included)", PERF_SAMPLE_IP, 0, 0);
    test("5) PERF_SAMPLE_REGS_INTR (kernel included, x0)", PERF_SAMPLE_IP|PERF_SAMPLE_REGS_INTR, 0, 1);
    puts0("DONE. An OK only means perf_event_open accepted attributes.\n");
    (void)syscall5(NR_EXIT_GROUP, 0, 0, 0, 0, 0);
    __builtin_unreachable();
}
