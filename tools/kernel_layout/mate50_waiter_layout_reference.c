/*
 * DCO-AL00 rt_mutex_waiter RECONSTRUCTION from exact ARM64 disassembly.
 * This is NOT an original Huawei kernel header.
 * No live kernel access, writes, or exploit logic.
 */
struct rb_node {
    unsigned long __rb_parent_color;
    struct rb_node *rb_right, *rb_left;
};
struct task_struct;
struct rt_mutex;
struct rt_mutex_waiter {
    struct rb_node tree_entry;
    struct rb_node pi_tree_entry;
    struct task_struct *task;
    struct rt_mutex *lock;
    unsigned int major_prio;
    unsigned int major_only;
    int prio;
    unsigned long long deadline;
};

#define PROBE(k,v) const unsigned long probe_##k = (v)
PROBE(size, sizeof(struct rt_mutex_waiter));
PROBE(tree_entry, __builtin_offsetof(struct rt_mutex_waiter, tree_entry));
PROBE(pi_tree_entry, __builtin_offsetof(struct rt_mutex_waiter, pi_tree_entry));
PROBE(task, __builtin_offsetof(struct rt_mutex_waiter, task));
PROBE(lock, __builtin_offsetof(struct rt_mutex_waiter, lock));
PROBE(major_prio, __builtin_offsetof(struct rt_mutex_waiter, major_prio));
PROBE(major_only, __builtin_offsetof(struct rt_mutex_waiter, major_only));
PROBE(prio, __builtin_offsetof(struct rt_mutex_waiter, prio));
PROBE(deadline, __builtin_offsetof(struct rt_mutex_waiter, deadline));
