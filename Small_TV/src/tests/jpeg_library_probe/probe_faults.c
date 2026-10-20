#include "probe_faults.h"
#include <assert.h>
#include <string.h>

static const char *const names[] = {
    "alloc", "open", "read", "write", "seek", "input", "output", "none"
};
static probe_fault_stats stats;
static probe_fault_kind selected = PROBE_FAULT_NONE;
static unsigned long target;
static int repeat;

const char *probe_fault_name(probe_fault_kind kind)
{
    /* Keep names stable in machine-readable fault and recovery evidence. */
    assert(kind <= PROBE_FAULT_NONE);
    return names[kind];
}

probe_fault_kind probe_fault_parse(const char *name)
{
    /* Reject unknown operation names rather than silently disabling injection. */
    for (unsigned i = 0; i <= PROBE_FAULT_NONE; ++i)
        if (!strcmp(name, names[i])) return (probe_fault_kind)i;
    return (probe_fault_kind)-1;
}

void probe_fault_reset(probe_fault_kind kind, unsigned long ordinal, int persistent)
{
    /* Arm one exact operation, optionally retaining an allocation outage. */
    memset(&stats, 0, sizeof(stats));
    selected = kind;
    target = ordinal;
    repeat = persistent;
}

int probe_fault_visit(probe_fault_kind kind)
{
    /* Count real calls even when no failure is armed, to calibrate the sweep. */
    assert(kind < PROBE_FAULT_COUNT);
    unsigned long ordinal = ++stats.visits[kind];
    if (kind == selected && target &&
        (ordinal == target || (repeat && ordinal > target))) {
        ++stats.hits;
        return 1;
    }
    return 0;
}

probe_fault_stats probe_fault_snapshot(void)
{
    /* Preserve the first phase counters before recovery disables injection. */
    return stats;
}
