# Opus PVQ: boundary fast-path applicability

2026-09-15. Host census only; no ASM change or target-speed measurement.
This investigation is independent of the endpoint-cost board experiment.

## Exact predicates

For the standard nonempty monotonic byte-cost rows:

- q=0 when bits <= floor((cache[1]+1)/2). This includes the original lower
  sentinel and tie rule; do not double a potentially large signed budget.
- q=cache[0] when bits > cache[cache[0]]+1. The strict comparison matters:
  equality may select an earlier entry if costs repeat.
- Also count hi-lo<=1 after three binary-search probes. This is applicability,
  not a measured gain from adding another branch before the accepted
  fourth/fifth-step shortcuts.

The observer always returns the original six-step bits2pulses result and
checks guarded indices. PCM, actual state/scratch and guards remain equal.
378304 standard budgets and42240 synthetic duplicate/tie/signed-edge cases
are checked. Neither range is an imposed decoder bitrate limit.

## Frequency on the saved audio corpus

Percent of basic no-split bits2pulses calls, not CPU percent:

| Stream | Calls | q=0 guard | Upper guard | Upper, LM!=-1 | Converged after3 |
|---|---:|---:|---:|---:|---:|
| mono12 |0|not applicable|not applicable|not applicable|not applicable|
| mono24 |102|39.22%|0%|0%|55.88%|
| stereo64 |675|24.15%|3.26%|3.11%|45.19%|
| stereo128 |1204|10.80%|4.82%|4.82%|19.77%|
| stereo192 |1765|6.63%|2.72%|2.10%|6.06%|
| stereo320/20ms |2665|6.75%|68.41%|5.59%|4.47%|
| stereo510 |19751|2.54%|97.46%|39.26%|1.89%|

All10 files, including320kbps2.5/5/10/20ms, are in
[summary.json](benchmarks/esp8266-opus-pvq-boundaries-2026-09-15/summary.json).
The first five use0.24seconds each; later lengths differ and are saved per file.
Uniform exhaustive upper-guard coverage371773/378304 must NOT be used as the
frequency at192kbps, where only48/1765 calls qualify.

LM!=-1 identifies calls whose original pre-split condition already reads
the upper cost. It does not prove that a suitable live register is available
at a future ASM insertion point. LM==-1 skips that load; inspect the linked
caller paths before trying reuse.

## Decision

Do not immediately add a blanket upper-bound guard for the192kbps target:
it benefits only2.72% of calls (2.10% with prior upper-cost evaluation), while
its loads/branch may cost time on every call. This is a priority decision,
not a measured slowdown. The guard may warrant a separate high-bitrate
experiment at320/510; those streams remain supported.

A third-step convergence branch benefits only6.06% at192, unlike the already
measured fourth-step43.34%; it also needs a new cost analysis before an ASM
trial. The zero guard6.63% is similarly unproven. No firmware default changes.

Reproduce with node tools/esp8266_opus_asm/profile_pvq_boundaries.cjs.
The baseline host decoder includes accepted tell-inline semantics; target
MDCT/PVQ register-only overlays are not being timed by this host observer.
