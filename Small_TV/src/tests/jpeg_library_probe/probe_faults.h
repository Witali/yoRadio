/* Deterministic host-only failures, separate from the decoder's memory budget. */
#ifndef SMALL_TV_JPEG_PROBE_FAULTS_H
#define SMALL_TV_JPEG_PROBE_FAULTS_H

typedef enum {
    PROBE_FAULT_ALLOC,
    PROBE_FAULT_OPEN,
    PROBE_FAULT_READ,
    PROBE_FAULT_WRITE,
    PROBE_FAULT_SEEK,
    PROBE_FAULT_INPUT,
    PROBE_FAULT_OUTPUT,
    PROBE_FAULT_COUNT,
    PROBE_FAULT_NONE = PROBE_FAULT_COUNT
} probe_fault_kind;

typedef struct {
    unsigned long visits[PROBE_FAULT_COUNT];
    unsigned long hits;
} probe_fault_stats;

const char *probe_fault_name(probe_fault_kind kind);
probe_fault_kind probe_fault_parse(const char *name);
void probe_fault_reset(probe_fault_kind kind, unsigned long ordinal, int persistent);
int probe_fault_visit(probe_fault_kind kind);
probe_fault_stats probe_fault_snapshot(void);
int probe_reuse(int argc, char **argv);
#endif
