# CYD Ogg runtime pressure and cancellation checkpoint

**PASS, 4 November 2026.** The root agent initiated and completed the SDK/QEMU
capture `cyd-ogg-runtime-controls-native-20261104-02`: SDK build exit0
(184.828 s), QEMU exit0 (73.203 s), followed by the complete independent
Decimal output check. These durations describe this diagnostic run.

The real RTOS, CYD `audio_service.c` and `native_audio_output.c` translation
units run with public allocator/decoder forwarding and public I2S driver
seams. The original stream/core0/priority3/6144-byte stack,
decode/core1/priority5/16384-byte stack and output/core1/priority6/4096-byte
stack profiles are preserved. Effective priority may change through mutex
inheritance; public task identity and startup/creation provenance are checked
separately. The selected SDK has no enabled public live-base-priority query.

| Finite control | Actual observation and required recovery |
| --- | --- |
| `BYTE_FALLBACK` | Real15360-byte byte realloc returns NULL; all eight real1920-byte word allocations succeed. Complete C8 source and final mono match their references. |
| `DUAL_OOM` | The original reverse five-link chain completes links0–1 before link2 really refuses both15360-byte byte storage and the first1920-byte word candidate. The exact two-link prefix drains and closes with allocation completion9, PROCESS stage2 and retained detail15360. The whole five-link reopen completes. |
| `SCRATCH_OOM` | A real public decoder reports BUFF_NOT_ENOUGH at11520 bytes and requests23040. The actual old-scratch growth returns NULL. The first packet commits zero logical output; health retains detail23040. Cleanup and the complete C8/120 ms reopen succeed. |
| `RING_RELEASE` | One borrowed output write is held before the real renderer. The original8192-byte NOSPLIT ring produces two real50-tick SendAcquire timeouts for valid requests; release yields complete exact EOF output. |
| `RING_STOP` | Real public Stop is issued while the producer is blocked. The entered old write may finish; real discard and the25-tick quiet fence precede complete exact reopen. |
| `RING_MAINTENANCE` | The gate releases after the real pause(true) call. The renderer returns documented INVALID_STATE with its source unchanged; actual maintenance returns HELD and a token after all owners are quiet. Blocked Play/stale-token assertions pass, and resume completes. |

The run completes **10 HTTP sessions, 8 typed terminals (6 healthy, 2 allocation
errors), 2 cancelled partial streams, 57 public decoder opens/closes and
10 HTTP cleanups**. All45 pressure allocations are freed. There are5 actual
failed-allocation callbacks: the four targeted NULLs above and one separate
natural15360-byte NULL during the full-chain reopen, which also recovers.
All callbacks forward to production health and match real allocation
intervals. No allocator return is scripted, no pressure block is dereferenced,
and no private codec/heap state, queue return, ACK or task suspension is used.

There are33 actual word-plane attempts:32 successes,32 frees and one refusal;
no live planes remain. The six retained ring timeouts cover two timeouts for
each blocked control. All12018 ring sends, receives and returns balance.
The complete source of each of12004 real writes is independently hashed
before and after the renderer; every comparison succeeds, including the
single maintenance INVALID_STATE return. Layout and gain stamps each total
12004. These finite counts do not establish full-application RAM headroom.

The complete immutable creator asset and13 direct-public reference decodes
are retained locally. The independent speaker/header/player projection uses
100 and160 Decimal digits, no production arithmetic helper and no new
numerical tolerance. All8 typed terminal outputs and12 complete logical
source/mono link spans match; a typed failure may have the predeclared
two-link prefix or empty output. Earlier complete F20/Vorbis stock PCM
bindings are checked separately. The codec itself remains the same pinned
Espressif implementation, so this is an integration/output oracle rather
than an independent codec-conformance result. Normalization is disabled in
this checkpoint; its enabled gate is separate.

The actual compiler closure contains18 translation units and472
dependencies. [source-inventory.json](source-inventory.json) binds all28
current runtime files, the existing35 committed production source inputs
from `de94a304ab70e0babe7345ac249b43b8d79300ca`, and7 data/oracle helpers to
their exact captured bytes. The121 reader contradictions and8 explicit
owner/health positive controls remain current for their consumed code.
Documentation and pure-check files are not all compiler dependencies.

The first native attempt remains **NONPASS**. It completed byte fallback and
the genuine dual refusal, then its test asserted `decoder_result==2`.
`2` is OGP_MEMORY status; the production public health path retains the exact
15360-byte detail. The corrected test predeclares15360/23040 before playback,
prints the full22-field health snapshot before health assertions, and checks
the exact generation/completion/stage/detail and actual callback sequence.
Healthy reopens retain the previous fault payload while adding zero decoder
failures. No production correction or relaxed acceptance was required.

This is the **diagnostic20 s TWDT/panic, INT1000 ms, light heap-poisoning**
profile with both idle watchdogs. It does not qualify production5 s/no-panic/
INT300 ms timing, enabled normalization, the separate48-case positive
campaign, full radio/TLS/TFT resource use, physical DMA/I2S, hardware or speed.

[observed-summary.json](observed-summary.json) contains selected actual
process receipts and observations. [manifest.json](manifest.json) binds the
three publication files and identifies selected whole originals by SHA256
and byte length. All raw UART/PCM, reports, SDK/config/header inventories,
source snapshots, objects, images and original failures remain whole/local.
There is no SDK archive or executable verification framework in this package.
A hash binding identifies an omitted original; these four files cannot
independently authenticate or reparse omitted bytes. Preparation reproduced
the original measurements with the current data-only reader and checked all
13 retained PCM hashes, without rerunning native code or Decimal arithmetic.

Entry points: [controller](../../run-cyd-ogg-runtime-controls-qemu.py),
[data reader](../../read-cyd-ogg-runtime-controls.py),
[target](../../target/cyd_ogg_runtime_controls_qemu/README.md),
[reader controls](../../target/cyd_ogg_runtime_controls_qemu/check_reader.py).
The target README is kept at its exact pre-capture bytes; this result README
records the completed successor status.
