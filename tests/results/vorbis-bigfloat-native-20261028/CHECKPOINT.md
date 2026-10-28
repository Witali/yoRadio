# Preserved native basic-arithmetic qualification

Custom full-standard Vorbis interval/gain work is deferred at the user's
request. This checkpoint preserves the already-completed diagnostic runs;
it does not select a production backend or resume that deferred work.

Both actual pinned SDK/QEMU targets passed the unchanged 701-row public C
fixture: ESP32 SDK 6.0.2/LX6 on worker core 1, and C3 SDK 6.1/RV32 on worker core 0.
Coordinator core 0, priority 3, stack 16384, task/idle watchdogs and assertions
remain enabled. Only the fixture's existing completed-record fflush calls are
redirected to real fflush followed by one tick of vTaskDelay. There is no yield
or watchdog reset inside a long arithmetic operation.

Each target retained all 701 primary records, 825 allocation refusals/recoveries,
18 guards, 3606 exports, 1643 capacity refusals, 1253 alias checks and 12,587,858
assertion checks. Actual NTT entries are rows 681 and 684. Every primary and
recovery dyadic/floor was compared with the independent Fraction/isqrt reader
and the saved actual host32 output. Allocator request sizes and peaks remain
actual native observations; they were not forced to match the host ABI.

| Actual diagnostic observation | ESP32 | ESP32-C3 |
| --- | ---: | ---: |
| Tracked allocator peak bytes |46616|47944|
| Final worker stack free watermark bytes |12812|13608|
| Final free heap bytes |292720|329244|
| Minimum observed free heap bytes |235700|269436|

Both terminal heap-integrity checks passed and all applicable IDLE tasks remain
registered with the watchdog. These figures cover this isolated retained
fixture, not a radio application's total resource use or realtime performance.

Seven groups are preserved: a synthetic parser-control group, and attempts
01–03 for each target. Both 01 attempts retain the SDK activation WinError 623
failure before the compiler child. Both 02 attempts retain 13 creator format
diagnostics promoted by the SDK's global-Werror. No QEMU execution is claimed
for these failures. Both 03 actual runs complete all seven commands and the SDK
child with exit 0. Full original BF UART records and native metadata are retained.

The isolated test project restores creator sign-compare/unused-parameter
warnings and makes only those categories nonfatal for creator files. Only
portable/libbf.c also makes its known format diagnostics nonfatal; all warnings
remain visible (42 per target). Adapter/main retain SDK -Werror. Actual symbols
and discarded-section/link-map evidence exclude debug, decimal, string and
transcendental helpers from the linked image; selected basic arithmetic symbols
are present. Foundation and shared fixture sources remain unchanged.

Artifact identities:

- ZIP: 7,978,161 bytes; SHA256 `e607c44ccb08db5e5378b55a416f4adcf1ad41addde586040b0b5256cf2260e9`.
- Manifest SHA256 `705d37bf3762b836f3521b7819f66e35343c82d1a39402e8e26c2a8ea998dea5`.
- 206 physical blobs/84,711,921 decoded bytes; 532 logical files/113,484,670 bytes.
- 3424 explicitly hashed derived SDK object/library/scratch omissions,
  294,056,278 bytes. Own objects/stack reports, ELF/map/images, compiler database,
  configs, source/project/corpus/reference bytes and every process log remain.
- Final native controller SHA256 `2bf2dddc4997b0555d33c97fdaa41cb76a1bdd572357ae9e2fdfe804b240afb8`.
- Unchanged shared fixture SHA256 `a07ae74869e64a4a008a5dd420bec305479fde6b8e420b721b6f973320809c79`.

`replay.json` is produced by the data-only verifier. It checks archive/alias
bytes, explicit omissions, all histories, source/config/flags, actual process
terminal facts, four native objects per target, linked/discarded symbols,
watchdogs and recorded resources. It compares every exact mathematical record
with the saved host32 records as strings, dropping only allocator ABI fields;
it never substitutes a digest for those comparisons. It does not recalculate
Fraction/MPFR arithmetic, import archived programs, extract files or launch any
compiler, SDK, QEMU or arithmetic child. Repeat into a fresh worktree path:

```sh
python -B -X utf8 tests/verify-vorbis-bigfloat-native-checkpoint.py --output .build/vorbis-bigfloat-native-replay-new.json
```

This checkpoint proves the retained basic-arithmetic diagnostic contract only.
It does not certify transcendental gain, Bark selection, wider transforms,
history/PCM continuation, all legal numerical inputs, physical hardware, a
production firmware image or production task changes.
