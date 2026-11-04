# Separate CYD Ogg runtime controls

This additive target prepares six bounded controls. Syntax and object checks
pass; every native launch requires the reviewed exact-file release manifest.
The first SDK/QEMU attempt completed byte-to-word recovery, then stopped at a
test-only health assertion that confused OGP_MEMORY status2 with the retained
15360-byte failure detail. That NONPASS is preserved. The corrected target
declares exact15360/23040 details before playback and records the complete
health snapshot before assertions; its full native rerun remains pending.
Earlier compiler attempts and placement audits are retained separately.

The source scaffold is copied from the immutable
`.build/cyd-family1-playback-task-20261103-03/sources/harness` input, not from the
concurrently evolving positive target. `baseline-provenance.json` authenticates
those original bytes and records that native03 was NONPASS at its final
zero-allocation-failure guard. No historical result is relabeled. Production
sources remain whole external inputs from the existing 35-file root release
(SHA256 745e7482cd90517c4e5778717dd7e1016d4e8c692d125f4a3cf15302e7dc9381).

## Finite controls

| Control | Genuine witness | Required recovery/output |
| --- | --- | --- |
| BYTE_FALLBACK | Original C8 / 20 ms `realloc(NULL,15360)` really returns NULL while public byte-heap pressure is retained; all eight real 1920 B word candidates succeed | Complete original C8 source and final mono, exact hashes |
| DUAL_OOM | Existing REVERSE_120_CHAIN reaches C8 at link index 2 after a real completed-source-write fence for links 0–1; byte and first word allocation both really return NULL | Exact predeclared two-link prefix and allocation-error terminal; complete unchanged five-link reopen |
| SCRATCH_OOM | Complete creator C8 / 120 ms input gets a genuine public BUFF_NOT_ENOUGH request, then existing scratch `realloc(old,23040)` really returns NULL | Zero logical output for the uncommitted first packet, allocation-error terminal, cleanup and complete exact reopen |
| RING_RELEASE | Original 8192 B NOSPLIT ring returns at least two genuine 50 ms valid-sized SendAcquire timeouts while one borrowed output write is held before the real renderer | Release and full exact EOF output |
| RING_STOP | Same real blocked ring, then actual public Stop; the already-entered old write may finish | Real output discard, owner cleanup, 25-tick quiet fence and complete exact reopen |
| RING_MAINTENANCE | Same real blocked ring; release gate only after forwarding real pause(true), so real renderer returns INVALID_STATE | Actual public maintenance HELD/token/all-owner cleanup, blocked Play/stale-token checks and full exact resume |

The matrix contains 10 HTTP sessions, 8 typed terminal outputs (6 healthy and 2
allocation failures),2 cancelled partial streams and 57 successful public codec
owners. The complete original 2,198,003 B immutable asset, 13 direct-public PCM
references, creator provenance, complete packet bodies and transport schedules
are reused. No fixture truncation, ring shrinking, fake queue returns, task
suspension, private codec/heap access or private ACK/state writes are used.
There is no scripted allocator return injection in these controls.

## Pressure and accounting

Pressure blocks use real `heap_caps_malloc`/`heap_caps_free` with public
capabilities and are never dereferenced, including possible IRAM allocations.
Every production allocation wrapper forwards its unchanged arguments to the
real allocator. Target matching excludes calls inside public decoder APIs;
it is bounded by actual decoder owner, session, link, public request geometry
and the observed resize result. Pressure is released after the targeted real
outcome (after all eight candidates for recovered fallback), before cleanup
and recovery. Actual target NULLs, pressure-helper NULLs and natural NULLs are
separate records. Largest-block observations alone never qualify a failure.

The diagnostic failed-allocation callback is IRAM, does no allocation/logging
or function-name dereference, and forwards the original production health
callback. Callback and allocator interval records are static and overflow is
NONPASS. The pinned no-SPIRAM ESP-IDF 6.0.2 path emits exactly one callback
for each positive-size real NULL. The SDK libc `realloc` bridge calls
`heap_caps_realloc_default`, which selects `heap_caps_realloc` with
DEFAULT|INTERNAL (6144). Its single callback must match the original requested
size and that mask; the record's zero capability value identifies the libc
wrapper rather than the callback mask. Public `heap_caps_malloc` reports one
callback matching its exact requested size/capabilities. The base routines do
not recursively call public failure-reporting allocation entries. The reader
rejects extra/nested/duplicate callbacks, wrong sizes/masks, successful calls
with callbacks and unaccounted intervals. Every actual callback is retained
and forwarded to the original health callback; unexpected real behavior is
NONPASS. The production health count must match the full callback census. Target calls also retain exact public
pressure block/byte counts; actual nonzero retained pressure is required.

At a 32-bit target ABI the three principal static observer arrays occupy
1232 B: 128 public pressure pointers use 512 B, 12 callback records use 240 B
and 12 allocator records use 480 B. Every genuinely quiet leg serializes every
retained record with its global sequence number before reusing the two small
trace buffers. The largest planned leg has 9 allocator records (one actual byte
NULL plus 8 actual word successes); 12 leaves 3 slots for pressure-helper or
natural failures. The one-callback-per-real-NULL SDK contract remains strict;
up to 12 actual callbacks per leg are retained, and any larger trace is a recorded
hard NONPASS, never a truncated passing case. The 128-pointer pressure table
has its own finite bound; an unmet target NULL remains NONPASS if that bound
is insufficient. No pointer needs a per-block size because all pressure is
released together and requested bytes are counted separately.

There are additionally 16 word-pointer/size slots (128 B), published stack
bounds and small scalars/atomics. The historic native03 heap minimum was only
1712 B. This reduced observer memory remains a material readiness risk; no
spare DRAM or extra IRAM is inferred. Exact linked footprint, heap impact,
callback IRAM call closure, stack headroom and actual controls require the
root-reviewed native build. The old map's pure-IRAM initial extent is
provenance, not an allocation-capacity claim.

The callback never calls a task getter. Task context publishes the actual
public `xTaskGetStackStart` bounds once, using the unchanged creation sizes
and validating that all three owner stacks are disjoint and nonoverflowing.
The pinned SDK documents that the returned address is the lowest stack
address regardless of growth direction and uses byte stack sizes here.
The callback uses inline `esp_cpu_get_sp`/core checks and the IRAM ISR check;
it reads neither stack memory nor a TCB. Its complete linked IRAM call closure
still needs verification in the newly authorized image.

## Completion and cancellation rules

The new target replaces only its own healthy-only flush guard with the
predeclared expected prefix/full extent. Codec owners must close before every
real terminal flush; HTTP cleanup is required eventually before acceptance.
A decoder allocation terminal can have `audio_failed=false`; the real public
status must be `decoder allocation failed` with running/pending false, the
exact allocation-error health reason and no unexpected pipeline failures.
The original positive target/readers and all production sources are unchanged.

All borrowed source bytes are independently hashed before/after every real
renderer return, including INVALID_STATE. Ordered gain/layout stamps, complete
source/link/mono hashes, logical-versus-wire padding, actual ring send/receive/
return balance, real discard completion and post-discard quiet are asserted.
The separate reader and independent Decimal 100/160-digit oracle qualify all
8 output extents if and only if the genuine native campaign later succeeds.
The public maximum fitting item size is sampled separately as `free_before`
immediately before the real SendAcquire and `free_after` following its actual
timeout. Selected held-ring witnesses require both values below the requested
valid-sized packet. These are independent observations, not an atomic snapshot
or a claim that the ring has zero unused bytes. A 50 ms SendAcquire wait is one retry; no application total-stall timeout is
claimed. Stop is allowed to complete one entered old write before its real
discard/quiescence fence. No stale activity is allowed after that fence.

## Unchanged diagnostic profile and open gates

Stream remains core 0 / priority 3 / 6144 B; decoder core 1 / priority 5 / 16384 B; output
core 1 / priority 6 / 4096 B. Reference wait is fixed 90 s, ordinary/control waits 30 s,
maintenance public request 10 s and whole QEMU 600 s, with no progress resets or
manual watchdog feeds. Both idle watchdogs, assertions, stack canaries and
light heap poisoning stay enabled. The native03 diagnostic defaults are
TWDT 20 s / PANIC=y and INT 1000 ms; this is not the separate original production
TWDT 5 s / no-panic / INT 300 ms selection. Heap abort-on-allocation-failure and PSRAM
must be disabled in the actual configuration, as verified by the controller.
Diagnostic barriers/delays are explicitly reported as enabled.

Normalization stays disabled while the exact real normalizer/settings component
is linked. The enabled-normalizer gate remains OPEN and unqualified. Hardware,
performance/radio fit, permanent exhaustion, real SDK close refusal, FLAC fault
campaign, private AAC and extended Vorbis are outside this bounded target.

The following pure checks remain available; further SDK/link/QEMU actions require root release:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 tests/target/cyd_ogg_runtime_controls_qemu/check_reader.py
```

Root must review memory/causal guards and replace `NATIVE_RELEASE_ID` with a
reviewed release identifier, then create a manifest with that `release_id` and
`files` mapping every target file plus the new controller and reader to exact
`bytes`/`sha256`. Supply its exact hash with `--native-release-sha256` and its
path with `--native-release`; the 35-file production release is checked separately.
The identifier avoids a self-referential manifest/controller hash. Existing
installed SDK/vendor/QEMU/tool pin and compiler-closure checks remain in force.
