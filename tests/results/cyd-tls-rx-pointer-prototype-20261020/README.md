# Superseded pointer-userdata RX reserve prototype — partial/nonpass

This is historical evidence for an **unapplied, superseded prototype**, not a
qualified feature. Runner14586 exited1. Its final raw report SHA is
`d4b6e019c0dcf1eaa59ca6f10f32be7d995fa82be2402fdb92ef8d9833561efc`; the terminal observation SHA is
`4411a96a7ac1318ce465a1e212cbbf4c216d50b9d1c42344991925f6cfce32a8`.

Six outcomes were accepted by that historical runner: canonical and five named
semantic controls. Seven QEMU executions occurred. The seventh, bypass-reclaim,
printed `busy_slot_reclaim_retry_preserved` and its controlled stop, then aborted
while esp_restart entered the SDK timekeeping-lock path under exhausted heap.
The QEMU process returned0, but the runner correctly rejected the panic and the
campaign remains nonpass. Three final reserve/reclaim option combinations were
frozen as source recipes and never built or run. Only reserve-on/reclaim-on was
actually compiled; the option matrix is incomplete.

Independent review also found a public API contract gap. The pinned SDK says
the pointer userdata getter's value is undefined after the numeric setter,
without a subsequent pointer setter. This prototype probes pointer userdata for
all configurations; old tests exercised pointer userdata only. Numeric-userdata
isolation is unproved. The prototype will not be integrated. A corrected registry
design is separate and is not covered by this archive.

The archive preserves raw passing host/config evidence with its original limits,
failed host attempts, prior preparations, all ten frozen source recipes, seven
execution bundles, raw compiler/runtime/nm/disassembly logs, source/header/config
identities and derived actual Xtensa ELF94 allocator metadata. Public SDK
documentation and the rejected panic's exact nm-resolved frame chain are separate
entries. Historical helper versions and unbuilt preparation claims remain
historical. Host success does not erase the target rejection or API gap.

Long paths flatten into content-addressed raw or deterministic-gzip payloads,
retaining encoded and original hashes. Whole ELF/flash/object/library/ROM/tool
binaries are explicit identity-only omissions. Linux tool identities are the
original host's reported observations; packaging does not invoke WSL. No prior
evidence, source, SDK or index is modified.

Run `python -B verify.py` for a standalone offline archive-integrity check. It
replays accepted oracles and requires the rejected seventh panic plus the three
unrun recipes. **Archive integrity PASS keeps target qualification false.** No
production integration, numeric isolation, protocol conformance, physical RAM,
fragmentation, speed or benefit is claimed. AAC, Ogg and deferred FLAC are excluded.
