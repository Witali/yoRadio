# Isolated public word-storage capability probe

This minimal ESP32 SDK/QEMU program observes real public allocations under
`INTERNAL|32BIT` and separately `EXEC|INTERNAL|32BIT`. Each case holds a separately
labelled 23,040-byte byte-capable DRAM control buffer, then attempts up to eight
11,520-byte word planes. A refusal is retained as a resource observation; it is
not relabelled as application or codec support. Every successful plane is cleared,
filled and checked through the shared aligned volatile32 helper only.

Actual public pointer classification and D/IRAM counterpart addresses distinguish
pure IRAM from aliases. No alias is dereferenced, and executable capability is not
treated as automatically additional physical RAM. Public 8-bit,32-bit and EXEC
free/largest values are reported before and after every allocation and after full
cleanup. They overlap in capability and must not be added as independent RAM.

The actual `esp_ptr_executable` result is checked against the pinned SDK6.0.2
address predicate, separately from the requested allocation capabilities. That
predicate ends its IRAM window at `SOC_IRAM_HIGH` (`0x400aa000`); the allocator
can also return instruction aliases in the wider D/IRAM range ending at
`0x400c0000`. Such a high alias reports `executable=0` through this public query.
The probe preserves that result and tests integer data accesses only; it never
executes code from the allocation. The original native01 remains NONPASS: its
extra assertion incorrectly required this query to be true for every EXEC
allocation and stopped before the second case's cleanup. The successor reader
checks both low and high aliases, including false query results, and rejects
contradictory address classifications.

The native06 application's initial pure-IRAM heap extent was80,740 bytes, from
0x4008c49c to0x400a0000. That historical boot/map bound is not current free space
and is not the minimal probe's available memory. The probe uses no decoder,
production task, private heap state, hardware, network or byte/halfword/FP access
to word planes. A diagnostic pass does not qualify full family1 application fit.

The finite SDK6.0.2/QEMU successor is **PASS**: both separate capability cases
allocated and checked all eight planes, including all 5760 samples and odd-half
RMW checks, then returned every allocation and all six heap measurements to
their original values. The [recorded checkpoint](../../results/cyd-word-plane-caps-20261103/README.md)
preserves the initial NONPASS and the exact successful successor.

The later launcher changes only correct main/worktree dependency discovery,
make the historical native06 comparison optional and use the tracked Windows
argument parser. They did not change the measurement parser, target/helper
code or recorded native result, and no native rerun is claimed for those CLI
changes. Full application fixtures, cadences and deadlines remain separate.
