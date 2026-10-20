# CYD output telemetry qualification — 2026-10-20

This archive binds host qualification of the integrated output telemetry and
actual standalone Xtensa helper objects. All source reports, logs, fixtures,
generated seams and captured configuration bytes are preserved. `manifest.json`
indexes every initial archive file except itself. `.gitattributes` disables text
conversion. `source-mappings.json` resolves original absolute/raw paths to the
archive; some Clang snapshot and long paths use flat names.

| Evidence | Scope/result |
| --- | --- |
| `runs/cyd-output-metrics-03` | Complete counter service: 16 quiet/diagnostic cases, 7 exact semantic controls |
| `runs/cyd-output-metrics-review-01` | Read-only counter review and real SDK 6.0.2 quiet/diagnostic Xtensa object compilation; IRAM helper, DRAM state/lock |
| `runs/cyd-output-telemetry-01` | Complete output and metrics translation units: 22 PDM/DAC/legacy quiet/diagnostic cases, 8 exact controls |
| `runs/cyd-telemetry-regression-*` | Existing PCM/gain/normalizer/pause/maintenance regressions; metrics deliberately use an empty seam |
| `runs/cyd-output-telemetry-verification-01` | Six final host reports, frozen/current source verification |
| `runs/cyd-health-output-telemetry-01` | 3 profiles; maximum JSON 2000 bytes in 2304-byte capacity; all-capacity canaries |
| `runs/cyd-stream-output-telemetry-03` | 50 stream cases and 80 settings requests; output-driver snapshot forwarding |
| `runs/cyd-output-telemetry-independent-review-01` | Independent integration/SDK contract/evidence review; no actionable findings |
| `lint` | Complete Clang analysis: 53 units, 86 warnings, 0 errors, 656 frozen inputs; no warning changes against N5 |
| `sdk-object-inputs` | Additional actual GCC object dependency closure and baseline config/command/map inputs |
| `tool-metadata` | Captured tool versions/hashes; no tool executable copies |
| `history/cyd-stream-output-telemetry-01`, `-02` | Incomplete failed fixture attempts; success 03 is authoritative |

`HOST.md` describes coverage and limits. `qualification.json` records current
source checks before/after copying. `omitted-artifacts.json` records hashes of
replaceable Linux x86-64 executables/objects and the existing baseline production
ELF omitted from the archive. Real Xtensa helper `.obj` files are retained.

This is not a new target application build or final integrated memory-map gate.
It does not establish physical ISR/SMP timing, DMA transmission, audible underrun
rate, hardware margin, audio quality, speed or telemetry overhead. Future target
evidence should be added as a separately manifested appendix without changing
these bound reports or snapshots.
