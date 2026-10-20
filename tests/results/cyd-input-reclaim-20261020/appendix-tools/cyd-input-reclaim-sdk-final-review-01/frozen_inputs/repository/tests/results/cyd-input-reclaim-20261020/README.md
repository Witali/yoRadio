# CYD TLS input reclaim: host qualification — 2026-10-20

This archive preserves the completed host, configuration, static-analysis and
independent source-review checkpoint. At this checkpoint, target QEMU and
production SDK application exports are pending. Later exported-build evidence
may be added in `SDK.md`/`SDK.json`; it does not change the scope of these reports.

| Directory | Completed evidence |
| --- | --- |
| `runs/service` | Whole production reclaim service and canonical queue; 21 cases, 17 exact semantic controls, ASan/UBSan |
| `runs/startup` | 12 ring/adaptive/reclaim configurations, 4 exact publication/rollback controls, ASan/UBSan |
| `runs/config` | 8 actual CMake guard cases; no firmware compilation |
| `lint/raw` | Full opt-in Clang: 54 units, 86 warnings, 0 errors, 661 frozen inputs |
| `lint/warning-delta.json` | Exact normalized diagnostic multiset equals prior telemetry 53/86; no added/removed warnings; new reclaim unit has zero diagnostics |
| `review/raw` | Independent production-service/root-wiring review; no actionable findings; 1600 frozen read inputs |
| `history/startup-attempt-01`, `-02` | Failed fixture preparations, preserved explicitly as historical failures |

`HOST.md` defines what the SDK/RTOS/allocator seams establish. Startup tests were
authored by the production reviewer and are supporting evidence, not an
independently authored test gate. In particular, their `observe_health_failure`
is an explicit SDK failed-allocation callback seam; startup does not execute the
actual `native_health.c` callback.

Reports, logs, source/configuration snapshots and generated inputs retain their
original bytes. `source-mappings.json` maps original paths to archive files;
long paths may use flat names. `omitted-artifacts.json` lists replaceable host
executable/object hashes. No executable binaries or SDK tool executables are
copied. `.gitattributes` disables Git text conversion.

Run the finished verifier with Python 3:

```text
python verify.py
```

It works offline from the archive alone, checks every manifest byte count/hash,
source mappings, frozen report inputs, the completed case/control counts and
the normalized warning delta. It does not access the original workspace or SDK.
`manifest.json` indexes every initial archive file except itself. Later SDK
appendices require updated/additional manifest coverage without changing this
README, HOST or the bound raw evidence.

No actual SDK OOM, target allocator/wrapper execution, final firmware linkage,
TLS handshake, RF, physical SMP/ISR timing, DMA, audio quality, memory margin,
fragmentation recovery or performance is established by this host checkpoint.
