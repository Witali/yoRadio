# Isolated identification and complete setup capture

This fixture links the owned `native_vorbis_numeric` component and minimal SDK
runtime. It captures complete identification/setup descriptors, every nested
codebook layout/word/multiplicand, the full uint32 configuration pool, typed
getter values and the audio packet prefix. No vendor/private ABI, stream
decoder, floor/residue synthesis, PCM or production application is linked.

The coordinator uses core0; the worker uses core1 on ESP32 and core0 on C3.
Priority3/stack16384 and the isolated DIO40/4MB profile are test settings.
Production task affinities and configuration are unchanged by this fixture.

Generate the reviewed JSON/header corpus with the independent setup oracle.
Run `tests/run-vorbis-setup-qemu.py` with explicit hashes for all four component
C files, all four public headers, component CMake, JSON/header and QEMU, plus
explicit ROM and pinned SDK/tool locations. Every literal input byte and every
C descriptor field is read back before SDK configuration; the complete source
closure, fixture and original data are frozen.

The 60 shared API controls exercise identification, invalid contexts, all four
caller-array capacity/NULL cases, error precedence, typed getter preservation,
short/long prefixes and sticky EOP. Scientific native rows are valid inputs
selected before measurement. Their declared ceilings are 16384bytes per packet,
256books,512words,1024multiplicands and8192configuration words. Larger host-only
boundaries do not become native coverage. Test-only guarded allocations use the
actual measured counts per case, with full immutable byte snapshots and frees;
the core component remains allocation-free. Array logs use128-element chunks.

`CHECKED_SETUP_CAPTURED` / exit0 confirms complete guarded capture only.
`passed` and `numerical_qualified` remain false until the separate independent
raw parser compares all descriptors, context links and typed getter results.
The three native per-cut counters explicitly remain zero; the host campaign
separately exercises every preceding valid identification/setup/prefix cutoff.
Raw floor0 zero fields and ignored mapping time bytes retain their documented
meaning; they do not qualify active floor0 curves or synthesis.

Only the fixture adds `-fstack-usage` to all four compilation units. Retained
`.su` files estimate compiler frames, excluding callees/libm, task high-water
and physical performance. No full decoder, PCM, radio or device qualification
follows from these finite parser/descriptor checks.
