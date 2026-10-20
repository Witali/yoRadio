# Actual SDK input reclaim qualification — 2026-10-20

Final fresh05 passed **five positive cases and four exact semantic controls**
on classic ESP32 dual-core QEMU with pinned ESP-IDF 6.0.2. It ran complete
production reclaim/queue/native-health translation units, real SDK tasks,
semaphores, heap, public mbedTLS allocator/free and a real SDK timer ISR.
The unchanged production CMake helper enabled the test-only opt-in profile;
production default activation remains off.

The allocator spy delegates to real `heap_caps_calloc` and records observed
NULL; it never fabricates positive-run OOM. Synthetic caller-owned filler
allocations exhaust eligible internal heap. Recovery must obtain a zeroed SDK
allocation before those fillers are freed. Protected data/control payloads,
queue floor and native-health allocation failure accounting are checked.
Two-core barriers exercise pin/retirement/restore overlap and fixed retry
budget despite concurrent producer restores. No private owner phases or ACKs
are written by the positive test.

Exact controls omit the first real attempt only after publication, omit
reclamation, omit paired pin accounting, or extend the fixed budget. Each
requires its named failure, controlled restart and clean QEMU exit. Generic
panic/abort, timeout, compiler failure and wrong-source selection are rejected.
On a failed predicate only test-owned fillers are freed before restart, so the
SDK can create its lazy timekeeping lock; the bound pool/SDK objects remain.

This is an allocator/lifecycle mechanism gate. Heap pressure and coordination
are synthetic. Full TLS handshake/audio/network workload, production memory
margins, driver/DAC/DMA/RF behavior, timing and physical qualification remain
separate. Production task/core/priority/stack assignments are unchanged.

## Retained evidence

`manifest.json` maps each original campaign path to raw or content-addressed
text bytes. Large repetitive SDK compile/build text uses deterministic gzip;
stored and decoded hashes/byte counts are verified. Raw reports and execution
bundles remain direct, unchanged bytes. Sources, exact mutation recipes,
compiler closure/config, pointer proofs and SDK/QEMU logs are retained.

ELF, test app, complete emulator flash, object/archive/tool binaries and binary
configuration are intentionally **not copied**. Their SHA256, byte size and
role/omission reason are recorded. Installed runtime/ROM files also have only
hash/size references. This includes packaging-time transient SDK binary
scratch, explicitly outside immutable qualification bundle claims. Original
ignored campaign directories retain those binaries on the originating host.

The final execution report is `raw/final05/report.json`; the five immutable
bundles are under `raw/final05/variants/`. Actual source/compiler dependency
closure is seven translation units and 206 dependencies per variant; 246
original source snapshots and 11 runtime references were checked. All bound
immutable input/artifact hashes were checked before and after execution and
again from the original files during packaging.

`parent-review/` preserves the supplied read-only parent review and its script.
The parent independently checked current sources/logs/bundles and raw ELF
allocator/free initializer words for all five variants. This review did not
run a new SDK build or emulator session. Binaries are omitted here, so the
offline verifier checks retained proofs and omission metadata rather than
recomputing ELF pointer words or executing code.

`preflight/` preserves 13 current-runner CLI/path protection cases. Final
session 65323 reached terminal exit 0. Rejected attempts01–04 have terminal
exit 1 and contribute **zero qualified detections/cases** to the final count:
variant selection initially failed to reconfigure; an unscoped mutant broke
SDK boot; an unused release symbol was legitimately garbage-collected; and
restart under full test pressure aborted on a lazy timekeeping lock. Their
unaltered reports/logs remain historical rejected evidence, including partial
internal PASS entries which are excluded from aggregate counts.

`scope/harness-README.md` was added after final qualification and is explicitly
not a frozen runtime input. It documents reproduction and source chronology.
`.gitattributes` preserves all stored bytes with `-text`.

Verify only the retained archive, without SDK/QEMU or a physical device:

```powershell
python tests/results/cyd-input-reclaim-qemu-20261020/offlineverify.py
```
