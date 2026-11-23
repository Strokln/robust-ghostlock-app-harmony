/*
 * Read-only compile-time layout probe for the 2026-11-23 Mate 50 Pro
 * kheaders archive extracted from boot_42.img. DOES NOT ACCESS THE DEVICE.
 *
 * Build as AArch64 assembler with the original include/generated/autoconf.h.
 * Read the .xword values of probe_* labels from the resulting .s file.
 * A replacement compiler may produce layouts that differ from the device.
 * Never use these measurements alone as a writable kernel profile.
 */
#include <linux/sched.h>
#include <linux/cred.h>
#include <linux/capability.h>
#define OFF(type, field) __builtin_offsetof(struct type, field)
#define PROBE(name, expression) const unsigned long probe_##name = (expression)
PROBE(task_prio, OFF(task_struct, prio));
PROBE(task_normal_prio, OFF(task_struct, normal_prio));
PROBE(task_sched_task_group, OFF(task_struct, sched_task_group));
PROBE(task_pi_lock, OFF(task_struct, pi_lock));
PROBE(task_pi_waiters, OFF(task_struct, pi_waiters));
PROBE(task_pi_top_task, OFF(task_struct, pi_top_task));
PROBE(task_pi_blocked_on, OFF(task_struct, pi_blocked_on));
PROBE(task_pid, OFF(task_struct, pid));
PROBE(task_tgid, OFF(task_struct, tgid));
PROBE(task_atomic_flags, OFF(task_struct, atomic_flags));
PROBE(task_real_cred, OFF(task_struct, real_cred));
PROBE(task_cred, OFF(task_struct, cred));
PROBE(task_comm, OFF(task_struct, comm));
PROBE(task_tasks, OFF(task_struct, tasks));
PROBE(task_seccomp, OFF(task_struct, seccomp));
PROBE(task_struct_size, sizeof(struct task_struct));
PROBE(cred_size, sizeof(struct cred));
PROBE(cred_usage, OFF(cred, usage));
PROBE(cred_usage_size, sizeof(((struct cred *)0)->usage));
PROBE(cred_uid, OFF(cred, uid));
PROBE(cred_security, OFF(cred, security));
PROBE(cred_cap_inheritable, OFF(cred, cap_inheritable));
PROBE(cred_cap_permitted, OFF(cred, cap_permitted));
PROBE(cred_cap_effective, OFF(cred, cap_effective));
PROBE(cred_cap_bset, OFF(cred, cap_bset));
PROBE(cred_cap_ambient, OFF(cred, cap_ambient));
PROBE(kernel_cap_size, sizeof(kernel_cap_t));
