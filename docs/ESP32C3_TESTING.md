# ESP32-C3 firmware testing

This document defines the acceptance tests added after the 2026-09-30 audit.
**A test exists, a test ran, and a test passed are three different states.**
Keep failed measurements. Never accept AAC-core fallback as successful HE-AAC.

For processor capabilities, hardware cycle counters, cache-aware measurements
and the applicable ESP-IDF 6.1 speed guidance, read the
[ESP32-C3 optimization reference](ESP32C3_OPTIMIZATION_REFERENCE.md).

Since 2026-10-08, positive HTTP/HTTPS file cases also reject captured allocation,
decoder, TLS, panic, watchdog, reboot and serial-capture failures, even if the
format status and EOF look correct. The result records whether serial capture
was enabled. Without it, status observations cannot prove the absence of runtime
faults. `tests/test-file-playback-runtime.py` injects these failures after valid
HEv2 PCM observations and verifies that the case fails and still stops the board.
Older file-matrix PASS records retain their original, narrower status/EOF scope.

The [2026-09-30 physical results](../tests/results/esp32c3-acceptance-20260930/README.md)
record passing OTA checks and outstanding HE-AAC, EOF and HTTP-load failures.
Tests not run are identified separately from failures.

The subsequent [EOF correction and regression tests](ESP32C3_EOF_STATUS.md)
separate terminal playback status from full-rate HE-AAC acceptance. They include
a deterministic delayed-output regression and FFmpeg/FDK complete-file references.

For allocation phases, per-task stack margins and reproducible SBR structure
sizes, see the [AAC memory investigation](ESP32C3_AAC_MEMORY_20260930.md) and
`tools/esp32c3_tests/memory.py`. Its survey is separate from a passing load/soak test.

The [AAC pointer audit](ESP32C3_AAC_POINTER_AUDIT_20261003.md) checks exact
core/SBR/PS targets, rotating rows, stack ownership and copy ranges for the
PC18 + four-row smoothing adapter in QEMU. Six retained runs include station
captures, allocation failures, resets and simultaneous decoders. Run
`python tests/test-aac-pointer-audit.py` to validate their evidence and parser.
The report documents unchecked views. The [PS coverage follow-up](ESP32C3_AAC_PS_COVERAGE_20261003.md)
shows why FFprobe's profile/channel label alone cannot establish PS execution.

The [low-QMF lifetime test](ESP32C3_AAC_LOW_QMF_LIFETIME_20261003.md) deliberately
overwrites transient rows before native decoding and compares the output with
the unmodified history. It includes a rejected bad-history control and a
deterministic two-task rendezvous. `python tests/test-aac-low-lifetime.py`
recomputes error statistics from retained synthetic PCM and checks capture
hashes, pointer coverage and source fingerprints. This is a prerequisite for
shrinking the allocation; it reports zero additional production RAM savings.

The [scoped low-QMF adapter](ESP32C3_AAC_LOW_QMF_WORKSPACE_20261003.md) now
retains only eight history rows per channel and moves the live full matrix to
the existing decoder stack. Its [physical follow-up](ESP32C3_AAC_LOW_QMF_PRODUCTION_20261003.md)
measures the 10,240-byte allocator saving, CPU, stack, local formats and OTA.
`python tests/test-aac-low-production.py` verifies the retained evidence, including
public HTTP/HTTPS failures that still block promotion. Passing this evidence
test means the records are consistent; it does not mean all playback passed.

The [asymmetric channel owner](ESP32C3_AAC_ASYMMETRIC_OWNER_20261003.md)
removes the unused left PS reserve and measures another 4 KiB allocator saving
in QEMU. `python tests/test-aac-asymmetric-owner.py --compiler <RV32-gcc>` checks
native object edits, prefix/stride assertions, six pointer/PCM runs and the
disabled-flag control. The [physical follow-up](ESP32C3_AAC_ASYMMETRIC_PRODUCTION_20261004.md)
adds the production storage flag, unpoisoned QEMU runs and actual hardware/OTA
outcomes. `python tests/test-aac-asymmetric-production.py` validates that evidence
while preserving unsuccessful tests. Nested transport exception types and
numeric OS codes are retained without private exception text.

The optional [network heap sampler](ESP32C3_NETWORK_MEMORY.md) records heap
blocks, TCP states and queued payload on the owning lwIP thread. Its summarizer
corrects for delayed logging and keeps the public-stream PASS/FAIL decisions.
Run `tests/test-esp32c3-network-memory.py` and `tests/test-network-heap-native.py`
for the host parser and sanitized C callback checks.

The [receive-credit extension](ESP32C3_NETWORK_RECEIVE_CREDIT.md) additionally
observes TCP data waiting for the application. Long load runs can use
`--load-seconds 180 --load-idle-recovery`; their outcomes remain separate from
the post-stop memory check. `load_windows.py` uses explicit observation bounds
and retains incomplete telemetry instead of assigning the next codec's samples
to a failed case. Its boundary tests are `tests/test-esp32c3-load-windows.py`.
The [physical receive-credit results](ESP32C3_RECEIVE_CREDIT_20261004.md) retain
the long paced failures, a post-Vorbis fragmentation failure, subsequent HE-AAC
HTTPS playback and three passing unpaced-file controls.

The [Vorbis audit and repair plan](ESP32C3_VORBIS_REPAIR_PLAN.md) records static
failed-open/low-memory defects, a PCM retry concern and the investigation needed
to identify the fragmentation owner. Its [first runtime step](ESP32C3_VORBIS_LIFECYCLE_20261004.md)
is complete: 100 repeatable decode/close cycles, 198 individual allocation
failures and four malformed headers in isolated QEMU. The original decoder
still fails the fault-handling gate; the subsequent
[initialization repair](ESP32C3_VORBIS_REPAIR_20261004.md) and
[retry/EOF repair](ESP32C3_VORBIS_OUTPUT_20261005.md) pass their retained target
tests. Physical fragmentation attribution and broader format coverage remain
pending. Run `python tests/test-vorbis-lifecycle.py` and
`python tests/test-vorbis-lifecycle-evidence.py` to verify the classifier and
retained results. The linked report includes full build/run commands.

The [custom-decoder terminal-memory check](ESP32C3_CUSTOM_DECODER_TERMINAL_20261005.md)
detects retained FLAC state after natural EOF which a Stop-based check hides.
Use `diagnostic.py terminal_memory` to measure before playback, after EOF
without Stop, and after a separate Stop. The service now also releases custom
FLAC/legacy state at terminal errors; the host ownership scenarios use
`python tests/run-custom-decoder-terminal.py`.

The [FLAC input-bounds repair](ESP32C3_FLAC_INPUT_BOUNDS_20261005.md) reproduces
truncated-frame overreads under ASan and tests the actual shared decoder against
FFmpeg PCM. Run `tools/codec_benchmark/run_flac_bounds.py --output OUTPUT_DIR`
(add `--contiguous` for the Arduino workspace), then use
`flac_truncation.py --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --output OUTPUT_DIR`
for partial-frame EOF and recovery on C3. Retained results are replayed by
`tests/test-flac-bounds-evidence.py`.

The [FLAC depth repair and matrix](ESP32C3_FLAC_DEPTHS_20261005.md) separates
4..24-bit source metadata from signed-16 output. `run_flac_depths.py` compiles
the actual core/adapter under sanitizers and compares with known PCM and FFmpeg;
`--allocation-failures` also checks persistent OOM cleanup and reopen. The
shared fixture generators cover source depths, stereo modes and 8192-sample
blocks. `terminal_memory.py --fixture-manifest PATH` accepts those fixtures for
physical natural-EOF heap checks using AUTO and explicit codec selection.

The [30-minute HE-AACv2 load report](ESP32C3_HEV2_SOAK_20261005.md) retains
a failed progressive-heap gate despite real-time playback and post-Stop
recovery. `summarize_sustained.py` replays the complete window and consecutive
five-minute windows; it does not replace the original acceptance outcome.
This report does not satisfy the one-hour C3-T08 criterion.

The [ten-minute HE-AACv2 RX-owner investigation](ESP32C3_HEV2_RX_OWNER_20261007.md)
retains the same progressive-heap failure with an 8-byte post-Stop idle
difference. Its full ownership trace is rejected for a truncated USB record;
independent playback, recovery and OTA observations remain available.

The [compact telemetry and native RX-copy follow-up](ESP32C3_RX_COPY_20261007.md)
retains two further ten-minute runs. Compact CRC records still lose rows;
native packet copies improve the observed memory minimum but retain the
progressive-heap failure. `tests/test-rx-transport-evidence.py` replays both
archives without treating missing telemetry as zero memory or declaring audio
continuity from decoder progress. Both experimental images remain unqualified.

The [configurable station timeout](ESP32C3_STATION_TIMEOUT.md) adds recovery
within a bounded connection window and an unavailable terminal state. The
default is ten seconds; WebUI accepts 1–120 seconds and persists it across
reboot. `connection_retry.py` checks temporary 503 responses, cancellation,
finite EOF, configured deadlines, stalled data, NVS persistence and post-Stop
memory. The server's `/recover/FIXTURE` route is shared by all boards.

The optional [heap-owner diagnostic](ESP32C3_HEAP_FRAGMENT_OWNER_20261005.md)
tracks live allocations in the largest initial free region, with explicit
overflow/unknown-owner rejection. Use `heap_idle.py` for a stopped-board window
without HTTP polling, and `tests/test-heap-fragment-evidence.py` to replay the
retained physical results. It changes timing and is disabled by default.
Shared-server `--delivery-stats` records completed socket-write timing for any
board; it does not measure TCP acknowledgements or audible gaps.

The audio server is shared by **ESP32-C3, ESP8266, CYD and any other HTTP audio
client**. Only the device-control runner knows the native C3 WebUI API. The
server does not select a board, upload firmware, reset it or change credentials.

The [IRAM placement audit](ESP32C3_IRAM_REDUCTION_20261001.md) compares matched
ELF/MAP files and physical playback/OTA evidence. The standalone
`tools/esp32c3_tests/iram_inventory.py` reports aliased SRAM capacity without
double-counting IRAM as additional DRAM. Auto Suspend is an optional,
hardware-specific experiment, not a global default.

The follow-up [Wi-Fi buffer balance](ESP32C3_WIFI_BUFFER_BALANCE_20261001.md)
checks whether that DRAM headroom permits sufficient dynamic Wi-Fi buffers
without sacrificing full-rate HE-AAC. It retains failed six-buffer controls,
host TCP_NODELAY experiments and high-bitrate multi-codec load evidence.
It also retains a later OTA panic and two load failures. ROM recovery restored
the original app; startup and saved playback were verified after a manual
reset. The failures block promotion of the Auto Suspend profile despite
earlier successful playback and OTA checks.

The [conservative IRAM follow-up](ESP32C3_CONSERVATIVE_IRAM_20261001.md)
disables Auto Suspend and passes all 15 repeat OTA gates from the new image.
Its 3584-byte capacity gain still leaves two first-cycle HE/v2 switching failures.
`tests/test-esp32c3-conservative-iram.py` validates the retained successes,
failures, exact configuration and source/image fingerprints; it does not turn
this experimental image into a production-qualified build.

The [TCP half-close investigation](ESP32C3_LWIP_HALF_CLOSE_20261001.md) reproduces
the pool ownership defect with real lwIP sockets and with the ordinary heap
allocator. `tests/run-lwip-half-close.py` checks six packet-driven scenarios
under ASan/UBSan. Its host results do not substitute for board OTA qualification.

For new hardware investigations, `diagnostic.py` wraps the existing `run`,
`memory`, `ota_transition` or `pool_settle` runner and keeps filtered panic
MEPC/RA/MCAUSE evidence alongside CPU/heap logs. For example:

```powershell
python tools/esp32c3_tests/diagnostic.py memory --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 --output .build/c3-memory-diagnostic
```

It retains possible code addresses from stack/backtrace lines, not raw stack
contents. These candidates are not a verified unwind. The wrapper does not
change firmware or settings on its own; the selected runner retains its normal
actions and restoration rules. Earlier filtered logs cannot retroactively
recover a discarded panic PC. Host filter checks are in
`tests/test-esp32c3-panic-capture.py`.

For contiguous-allocation failures, add `sdkconfig.heap-layout.defaults` to an
awake HTTP-profiler build. `CONFIG_YORADIO_HEAP_LAYOUT_DIAGNOSTICS` logs selected
blocks at the existing AAC memory checkpoints: all free areas >=256 bytes and
their immediate neighbors, plus allocations >=1024 bytes. Each capture is
bounded at 128 rows; `dropped` must be zero before interpreting it as a complete
selection, and received rows must match the declared count. The
[physical heap/TCP investigation](ESP32C3_HEAP_LAYOUT_20261001.md) retains two
incomplete serial captures and excludes them from topology conclusions.
It does not enumerate every small block. Only addresses, sizes and
allocation state are retained; payload memory is never read.

The capture table uses at most 1600 bytes of the existing AAC task stack on
RV32 and no persistent heap/BSS table. Callbacks only copy metadata while IDF
holds the individual heap lock; logs are emitted afterward. Heaps are visited
sequentially, so the combined view is not an atomic global snapshot. Raw walker
sizes differ from the allocator's rounded maximum allocatable size. SDK codec
malloc/calloc addresses are also logged for allocations >=1024 bytes; these
are allocation events, not a complete ownership/lifetime trace. Logging changes
scheduling and can change transient network demand, so do not use this image
for performance qualification. Host ASan/UBSan selection/bounds checks:
`python tests/run-heap-layout-capture.py` in an environment with `cc`.

Add `sdkconfig.tcp-allocation.defaults` to that diagnostic build to correlate
the selected addresses with `PERF TCP_ALLOC` and `PERF TCP_FREE` records. This
separate option forwards lwIP allocation/free unchanged and logs the PCB state
before release. It never logs IP addresses, ports or packet contents. Retain
the exact ELF/config: a matching size alone does not prove block ownership.

`sdkconfig.tcp-pcb-pool.defaults` enables the separate experimental PCB pool.
Its capacity remains `CONFIG_LWIP_MAX_ACTIVE_TCP`, including active and TIME_WAIT
PCBs, exactly as in this IDF's heap-backed allocator. The 168-byte C3 structures
use RTC RAM, with one ownership byte per slot in ordinary DRAM. The protocol,
TIME_WAIT duration, packet allocations and codec code are unchanged. The pool
cost is reserved RAM, not a reduction of each PCB's payload. Allocation exhaustion
still returns NULL to TCP's existing recovery/reaping logic; other memp types
are forwarded unchanged. Ownership flags reset on boot independently of retained
RTC contents, which `tcp_alloc` initializes before publishing a reused PCB.

This build option is off by default and mutually exclusive with the passive
TCP allocation trace. The implementation requires IDF's heap-backed memp mode
without memp overflow instrumentation; static assertions reject an incompatible
configuration. Memp usage/error statistics remain supported. Host checks run
with `python tests/run-tcp-pcb-pool.py`: configured capacities 1/16/32, statistics
off/on, exhaustion/reuse, forwarding, alignment and 40000 concurrent lifetimes
per variant under ASan/UBSan. Physical qualification must include early mixed-codec
switches, WebUI traffic/OTA, TLS and the deep-sleep RTC footprint before promotion.

The [physical pool trial](ESP32C3_TCP_PCB_POOL_20261001.md) passes all 21 mixed-codec
switches but is rejected after two ownership assertions during OTA. Its 15 HTTP
checks alone passed because the application automatically rebooted into the same
image. For new OTA campaigns use `tools/esp32c3_tests/ota_diagnostic.py`, which
returns failure on panic/capture errors even if HTTP/hash checks pass. Both
`report.json` and `serial-health.json` must pass. Optional
`sdkconfig.tcp-pcb-pool-trace.defaults` retains 128 pool lifetime events and
dumps them on an ownership failure; its 1028-byte DRAM cost and timing effects
make it a diagnostic build, not a performance result.

The [half-close fix](ESP32C3_LWIP_HALF_CLOSE_20261001.md) now passes the same 15
OTA gates with serial-health PASS and exactly the five expected software resets,
plus 21/21 mixed-codec switches. Run `tests/test-esp32c3-half-close-hardware.py`
to validate its exact image/configuration, retained checks and CPU survey.
These results supersede the ownership failure for the fixed image only.

The [physical DIO/QIO comparison](ESP32C3_FLASH_QUAD_20260930.md) records passing
standalone QIO 40/80 MHz tests with register checks, repeated flash reads and
AAC decoding. Run `python tests/test-esp32c3-flash-quad.py` to validate retained
evidence and rejection paths. This does not replace full-radio QIO acceptance.
The subsequent [full-radio QIO 80 MHz results](ESP32C3_QIO80_ACCEPTANCE_20260930.md)
retain both failures and passes; the production default remains DIO 80 MHz.
The [ESP-IDF 6.1 repeat](ESP32C3_QIO80_RECHECK_20261008.md) separates actual
bus/read verification from current HTTP/HTTPS, switching, sustained load,
OTA and boot acceptance. Run `python tests/test-flash-mode-probe.py` and
`python tests/test-qio80-recheck-evidence.py` to check the parser and retained
physical evidence, including unsuccessful cases and restoration of the board.

## Gaps found and corresponding tests

The [BFP16 QMF experiment](ESP32C3_AAC_BFP16_20260930.md) adds paired real-decoder
raw-PCM comparisons in QEMU, arithmetic boundary tests, unquantized controls,
three block sizes and instruction counts. Its harness completes, but all tested
HE/v2 BFP16 block sizes **fail** the one-LSB limit. Run
`python tests/test-aac-bfp16.py` to validate the retained evidence and negative
parser cases; that regression pass preserves a measured optimization failure.
The [real-recording extension](ESP32C3_AAC_BFP16_REAL_20260930.md) adds 60 paired
comparisons, per-channel error moments/histograms and independent FFprobe frame
counts. Validate that retained evidence with `python tests/test-aac-bfp16-real.py`.

The [packed complex history experiment](ESP32C3_AAC_PACKED_HISTORY_20261001.md)
uses **±5 LSB during development and ±2 LSB for the final version**, maximum per
sample/channel (2026-10-01). It tests
14+14+4 storage on retained SBR/PS histories, nearest and floor/midpoint modes,
lossless controls and five real recordings: 201 paired comparisons. It still
fails precision (3 LSB real, 7 LSB synthetic). Run
`python tests/test-aac-packed-history.py`; a passing evidence test preserves
that rejection. Inactive history paths are explicitly marked as not exercised.

The [FAAD2 scaling comparison](FAAD2_HISTORY_SCALING_20261001.md) adds 60 paired
host runs in fixed and float modes on the same inputs, plus 98,304 exact scaling
invariance checks. `python tests/test-faad-history-comparison.py` validates the
raw evidence, source hashes and rejection of overflow-bypassed large-scale trials.
This is a reference backend comparison; it does not qualify a firmware backend
replacement, C3 memory savings or physical decoding speed.

The [PC16 shift and block-storage test](ESP32C3_AAC_PC16_SHIFTS_20261001.md)
executes the `shift=exponent+1` implementation, exhaustive component codes,
independent rounding/boundary checks and eight-sample block equivalence under
UBSan: `python tests/test-aac-pc16-shifts.py`. The subsequent
[201 PC16 QEMU decoder comparisons](ESP32C3_AAC_PC16_QUALITY_20261001.md) pass the
temporary ±5 gate but fail the final ±2 gate (maximum 3). Validate logs, block/tail
coverage, scalar equivalence and both gates with `python tests/test-aac-pc16-history.py`.
Reduced live allocations and physical CPU speed remain unqualified.

The [supplied FAAD PS patch test](FAAD2_PS_PATCH_QUALITY_20261001.md) adds 33 host
decodes from pristine, patch-disabled and patch-enabled sources. Both active-PS
inputs reach 2 LSB; nine inactive-PS inputs and every disabled-patch decode are
bit-identical controls. `python tests/test-faad-ps-patch.py` checks frame traces,
delayed mono-to-stereo PS activation, source/PCM hashes and integer error counts.
The measured 9600-byte host PS-structure reduction is not a full-radio RAM result.

The [current-decoder PS write port](ESP32C3_AAC_PS_WRITE_PORT_20261001.md) adapts
that strategy to Espressif's actual delay/feedback writes: 81 QEMU paired
comparisons, bit-exact native-source/bypass controls and guarded unused storage.
The maximum is 3 LSB (temporary ±5 passes, final ±2 fails). Packed delay payload
shrinks by 2468 bytes, but the owner allocation is unchanged and heap saving is
zero. `python tests/test-aac-ps-history-port.py` validates retained evidence,
implementation hashes, controls and rejection of false memory/precision claims.
Packed transitions/reset lifetimes and full-radio performance remain unqualified.

The [pristine FAAD float32/fixed comparison](FAAD2_FLOAT_FIXED_COMPARISON_20261001.md)
adds 22 main decodes and 22 fresh-process repeatability controls. LC differs by
up to 2 LSB, but synthetic HE/v2 and PS onset expose much larger existing
arithmetic-path discrepancies. `python tests/test-faad-arithmetic-comparison.py`
validates hashes, full output rates, channel transitions, histograms and retained
transients. This is separate from the additional error allowed for packed storage.

| ID | Previously missing coverage | Test created | Acceptance |
| --- | --- | --- | --- |
| C3-T01 | Repeatable production RAM-policy regression | `tests/test-esp32c3-acceptance.py`, `ProductionConfigTests` | Execute the actual PowerShell production wrapper against saved configs: both Wi-Fi IRAM options become disabled, other values survive, second run is idempotent; relative and absolute paths work. |
| C3-T02 | All current codec families through the full HTTP pipeline | `run.py --suite http` | Every fixture plays with correct decoded rate/channels/bit depth, using both AUTO and explicit codec; finite file reaches EOF. |
| C3-T03 | Equivalent HTTPS/TLS playback | `run.py --suite https` | Same matrix, trusted certificate, no TLS-verification bypass. Missing trusted server is BLOCKED. |
| C3-T04 | Certificate rejection and recovery | `run.py --suite tls-rejection` | Untrusted TLS stream never plays; a subsequent HTTP stream plays normally. |
| C3-T05 | Full-radio AAC changes in one connection | `run.py --suite transitions` | Ordered, repeatedly confirmed full-rate formats; includes LC mono → HEv2 with identical ADTS core configuration and Stop/Play generation replacement. |
| C3-T06 | Repeated codec switches and retained/fragmented heap | `run.py --suite switch` | At least three cycles; every start succeeds; settled heap/largest block/task count recover after warm-up. |
| C3-T07 | Network faults with recovery | `run.py --suite faults` | Truncation, stall and HTTP 503 allow a new mono stream; redirect and jitter preserve playback and EOF. |
| C3-T08 | Long continuous playback on the full radio | `run.py --suite soak` | Default one hour, correct format throughout, responsive HTTP, real-time PCM progress and heap budgets; CPU is recorded. A shorter run is only a smoke test. |
| C3-T09 | CPU and memory with concurrent WebUI requests | `run.py --suite load` | 40 seconds per selected fixture, 100 ms polling, at least three stable CPU/decode windows, no allocation failure or core fallback. |
| C3-T10 | OTA regression against the exact current app | `ota.py` | Both slots used, uploaded ELF identity checked after boot, negative cases preserve active app, Wi-Fi/playlist/settings unchanged. Includes slow and playing-state uploads. |
| C3-T11 | Live browser-channel metadata after reconnect | `run.py --suite websocket` | Two fresh WebSocket connections receive `fmt` and playing state matching REST. Host stream-format tests already check OLED formatting and generation changes. |
| C3-T12 | Quantified Wi-Fi-placement boot/readiness A/B | `run.py --suite boot-time`, `compare_latency.py --kind boot` | At least 30 samples per configuration, same board/network conditions and selected regression/budget limits. This measures reboot-to-WebUI, not pure association time. |
| C3-T13 | Interrupt-latency A/B under flash/Wi-Fi load | Manual procedure below + `compare_latency.py --kind irq` | External edge timing, full provenance, at least 30 samples and an explicit absolute deadline. Host HTTP timing cannot substitute. |
| C3-T14 | Real browser rendering, OLED appearance and physical audio | Manual procedure below | Upload form/progress/errors are usable; whole OLED updates; stereo channels and audio continuity are checked physically. |
| C3-T15 | Power interruption during OTA | Manual procedure below | Dedicated recoverable test board boots the previous/new valid app after interruption at each stage; do not assume automatic rollback exists. |
| C3-T16 | AAC buffer-reuse equivalence and error paths | `run-esp32c3-stream-format.py`, `run-esp32c3-memory-trace.py`, `compare-pcm-wav.py`, real-decoder QEMU and full-radio matrix | Adaptive ADTS and 8 KiB PCM pass host OOM/retry checks and byte-identical fixture output. Full-radio HE/v2 and internal-state/exhaustive-profile coverage remain open. |
| C3-T17 | Stable terminal status after buffered decoder output | `tests/run-esp32c3-eof.py`, `run.py --suite eof`, `reference_eof.py` | EOF follows queued PCM; stopped REST/WebSocket status stays stopped and clears stream parameters. Exercise all eleven fixtures with AUTO/explicit codecs, late metadata, stale generations, cancellation and failures. Profile/rate acceptance remains a separate requirement. |
| C3-T18 | Configurable station-unavailable timeout and connection retry | `tests/run-stream-connection-retry.py`, `connection_retry.py`, `tests/test-connection-retry-runtime.py` | Temporary 503 recovers within the deadline; 3/10-second timeouts stop with an unavailable status, no later request; Stop/new station/watchdog cancel pending retries; EOF stays finite; settings survive reboot and invalid values are rejected; settled heap recovers. Only a recorded, verified software reset for the persistence test is exempt from the unexpected-reboot gate. |

## What “all formats” means here

The current native C3 streaming pipeline selects MP3, AAC, FLAC and Ogg
(Vorbis/Opus). The built-in matrix contains eleven files/layouts:

- MP3 320 kbit/s, FLAC level 8, Vorbis quality 10, Opus 510 kbit/s:
  48 kHz stereo, original 11-second noise/tone fixtures.
- AAC-LC 320 kbit/s: 48 kHz stereo, original 11-second fixture.
- AAC-LC 44.1/48 kHz stereo and 22.05 kHz mono; HE-AAC 44.1/48 kHz stereo;
  HE-AAC v2 44.1 kHz stereo. Short original ADTS fixtures are repeated into
  finite approximately 12-second streams without adding another container.
- Two extra continuous ADTS files exercise format changes. Their individual
  phases are paced at their own encoded rates.

The manifests verify source hashes before serving. These are representative
tests of every current codec family, not exhaustive coverage of all possible
AAC object types, sample rates, bitrates or containers. In particular, SDK
support for M4A/TS/raw AAC does not prove those inputs are wired into this
firmware. Add explicit fixture/routing tests before advertising them. Preserve
all existing AAC-LC/HE/PS capability while optimizing memory.

## Setup and host checks

Run commands from the repository root or task worktree. Use Python 3.10+,
Node.js, PowerShell for T01, and a host C/C++ compiler (WSL on Windows).

```powershell
python -m pip install -r tools/esp32c3_tests/requirements.txt
python tests/test-esp32c3-acceptance.py
python tests/test-esp32c3-cache-hardware.py
python tests/test-esp32c3-radio-profile.py
node --test tests/esp32c3-memory-stability.test.js tests/esp32c3-native-idf.test.js tests/esp32c3-cpu-profile.test.js tests/webui-firmware-ota.test.js tests/codec-benchmark.test.js tests/audio-stream-info.test.js
```

From a WSL shell in the same checkout:

```sh
python3 tests/run-esp32c3-ota.py
python3 tests/run-esp32c3-stream-format.py
python3 tests/run-esp32c3-eof.py
python3 tests/run-esp32c3-memory-trace.py
C3_MEMORY_SANITIZE=1 python3 tests/run-esp32c3-stream-format.py
```

The sanitizer mode instruments the host C callbacks, PCM workspace and ADTS
adapter/fault tests with AddressSanitizer and UndefinedBehaviorSanitizer.
It does not instrument the precompiled Espressif library or the Helix C++ test.

For the same deterministic QEMU fixture sequence, compare the baseline and
candidate captures with `python tests/compare-pcm-wav.py before.wav after.wav`.
The tool checks layout/duration, non-silent data and every PCM byte. Keep both
image/configuration identities with the result; equal captures alone cannot
prove a different decoder's internal-state equivalence.

`memory.py --minimal` checks existing INFO-level production RAM logs without
requiring the extra profiler task, runtime counters or allocation-trace arrays.
It still rejects incorrect HE/v2 output. `--audio-buffer-blocks 14` temporarily
selects the maximum compressed buffer, reboots to apply it, then restores the
original value and verifies Wi-Fi/playlist/settings against an in-memory snapshot.
The original non-private buffer count is saved in the report for recovery if
the test process is interrupted. This does not test stacks or CPU in minimal mode.

The new host tests exercise the acceptance checks against valid and invalid
evidence, including the retained physical SBR failure, actual HTTP/TLS server
responses and the production PowerShell wrapper. Passing these tests means the
test infrastructure detects those failures; it does not mean the board passes.

## Shared audio server — every board

```powershell
python tools/audio_test_server/server.py --host 0.0.0.0 --port 8770
```

Use your PC's LAN address in the board's stream URL, for example:

```text
http://PC_LAN_IP:8770/file/mp3-320
http://PC_LAN_IP:8770/file/flac-level8
http://PC_LAN_IP:8770/file/vorbis-q10
http://PC_LAN_IP:8770/file/opus-510
http://PC_LAN_IP:8770/file/he-48000-stereo
http://PC_LAN_IP:8770/stream/lc-48000-stereo
http://PC_LAN_IP:8770/file/changing
http://PC_LAN_IP:8770/file/implicit-sbr
```

`/manifest.json` lists profiles, decoded layouts, durations and hashes.
`/file/NAME` has Content-Length and EOF. `/stream/NAME` repeats ADTS AAC only;
it does not concatenate FLAC files or Ogg containers. `/drop/NAME`,
`/stall/NAME`, `/error/NAME`, `/jitter/NAME` and `/redirect/NAME` inject faults.
Unknown routes/files return 404. Stop the server with Ctrl+C.

For continuous longer files and extra mono/stereo/rate combinations, install
FFmpeg/FFprobe and generate an independent fixture directory:

```powershell
python tools/audio_test_server/generate.py --output .build/audio-60s --seconds 60
python tools/audio_test_server/server.py --fixture-manifest .build/audio-60s/manifest.json
```

Defaults generate five codec families × two input rates × mono/stereo. Opus
can decode at 48 kHz regardless of input rate; expected output comes from
FFprobe. FLAC bit depth also comes from FFprobe. Native FFmpeg AAC encoding
here is LC; the retained FDK fixtures supply HE/v2. Source audio is generated
locally; nothing is downloaded or recorded from radio stations. To test another
bitrate/profile, add a manifest-verified fixture rather than relabeling one.

## Physical playback tests

Use firmware **without deep sleep**. Choose the actual board address and PC
address. Only one test controller should use a board at a time. The runner
temporarily plays test URLs without saving playlist or Wi-Fi changes. It
normally reboots via the WebUI at exit to resume the saved station;
`--leave-stopped` avoids that reboot. Record failures of restoration too.

```powershell
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --suite http --output .build/c3-tests/http
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --suite transitions --suite faults --suite websocket --output .build/c3-tests/changes
```

Every matrix fixture runs with automatic detection and explicit codec selection.
Use repeated `--case NAME` arguments to narrow a diagnostic rerun. This is not a
full-matrix pass. REST samples and server transfer evidence are retained even
when a case fails. Tests check decoded layout, not merely `playing=true` in the
POST response. Finite playback must subsequently report stopped/EOF.

### HTTPS

Use a hostname/certificate chain already trusted by the production ESP-IDF CA
bundle and resolving to the test PC. Supply the leaf/chain PEM and private key
to the local listener, or use a separately configured HTTPS origin with the
same manifest and routes. Never commit keys, add a test CA to production, or
disable certificate validation to obtain a passing result.

```powershell
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --suite https --https-origin https://YOUR_TEST_HOST:8771 --tls-cert .build/tls/fullchain.pem --tls-key .build/tls/key.pem --output .build/c3-tests/https
```

Without `--https-origin`, each HTTPS case is **BLOCKED**, exit code 1. For the
separate negative test use a newly generated, intentionally untrusted cert:

```powershell
python tools/audio_test_server/make_test_certificate.py --host PC_LAN_IP --output .build/untrusted-tls
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite tls-rejection --https-origin https://PC_LAN_IP:8771 --tls-cert .build/untrusted-tls/cert.pem --tls-key .build/untrusted-tls/key.pem --output .build/c3-tests/tls-rejection
```

The negative test also requires the local TLS listener to record a certificate
rejection alert. An unreachable server alone cannot make this test pass.
ESP-IDF's bundle callback can produce `TLSV1_ALERT_ACCESS_DENIED`; that alert
is accepted only together with a fresh, sanitized serial message confirming
certificate verification failure. Generic TLS errors or an empty bundle alone
are insufficient. The test then requires successful HTTP playback recovery.

For public radio HTTPS plus concurrent WebUI requests, use the separate runner:

```powershell
python tests/test-esp32c3-public-streams.py
python tools/esp32c3_tests/public_streams.py --board http://BOARD_IP --serial-port COM9 --firmware firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin --seconds 60 --interval 0.1 --output .build/c3-tests/public-https
```

Install FFprobe on the PC and use an awake profiling image already on the board.
The firmware path verifies image identity; this command does not flash it. The
default manifest uses official public SomaFM AAC and MP3 HTTPS links. Before each
case, FFprobe validates TLS and identifies the live codec/profile/rate/channels.
The board must match the full decoded PCM layout, retain playback, answer REST
requests within two seconds and publish matching WebSocket state. CPU is
informational unless an explicit ceiling is supplied; heap gates apply. Serial
panics, decoder/allocation errors, unexpected
reboots and persistent idle heap loss fail the test. At exit it reboots to the
saved station and compares Wi-Fi, playlist and settings in memory.

Use `--case NAME` to select entries, `--interval 1` for a lighter polling run,
`--transport http` for an explicit public-stream cleartext RAM/CPU comparison,
or `--manifest PATH` with `sources` and `streams` fields as in
[`public_streams.json`](../tools/esp32c3_tests/public_streams.json). Only put public,
credential-free HTTPS URLs in that manifest: they are retained in the report.
No broadcast audio, titles or private board settings are saved. Streams and
their encoding may change; this short live-radio test does not replace the
controlled HTTPS fixture matrix, PCM comparisons, physical listening or one-hour
soaks. A server/probe failure remains a failed case, not a board playback pass.

For implicit AAC, FFprobe's `HE-AACv2` label alone does not establish actual PS.
[FFmpeg 8.1.1's AAC parser](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/aac/aacdec.c#L1851-L1865)
can assume PS/stereo when first discovering SBR on a mono stream. Use
`--aac-reference-command .build/faad-reference-command.json` to resolve this
with the independent `faad_history_probe.c` executable from the pinned
FAAD comparison build. Scope `0` disables all history quantization. Example
JSON argv for a native Linux build:

```json
["/absolute/path/to/probe-float", "{input}", "0", "1", "1"]
```

For a Linux probe used from Windows/WSL:

```json
["wsl.exe", "--exec", "/absolute/linux/path/to/probe-float", "{input_wsl}", "0", "1", "1"]
```

The runner also needs FFmpeg. It temporarily captures five seconds of the
same HTTPS source without transcoding, requires complete ADTS frames and a
successful independent decode, and retains only hashes and statistics. It
checks source channels separately from PCM channels; HE mono may produce two
identical PCM channels. Actual PS still requires the HE-AACv2 label. Missing,
silent, truncated or quantized reference output fails the test. A short source
observation cannot guarantee that a live station never changes its format.
Without this option the original strict FFprobe comparison remains in force;
an ambiguous result must be investigated, not silently accepted as playback.
The [2026-10-01 physical results](ESP32C3_PUBLIC_HTTPS_20261001.md) retain LC/MP3
passes and HE/v2 allocation failures under both HTTPS and HTTP load.
The [dynamic TLS follow-up](ESP32C3_TLS_DYNAMIC_20261001.md) uses the same
runner and records improved LC/MP3 free memory with continuing HE/v2 failures.
TLS error logs are sanitized before retention and fail the playback check.

### CPU, memory, switching and soak

These require the no-sleep diagnostic image with USB logs and FreeRTOS runtime
accounting. See [build instructions](../tools/codec_benchmark/cache/HARDWARE.md#full-radio-cpu-and-format-checks).
The diagnostic image is separate from quiet production; run the file and OTA
matrix on the production image as well. Save each test image under `firmware/`.

```powershell
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite switch --cycles 3 --output .build/c3-tests/switch
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite load --output .build/c3-tests/cpu-aac
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite load --fixture-manifest .build/audio-60s/manifest.json --case mp3-48000-2ch-60s --case flac-48000-2ch-60s --case vorbis-48000-2ch-60s --case opus-48000-2ch-60s --output .build/c3-tests/cpu-other
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite soak --case lc-48000-stereo --soak-seconds 3600 --output .build/c3-tests/soak-lc
```

Repeat soak for `he-48000-stereo` and `hev2-44100-stereo`. For non-AAC one-hour
soak generate a **single continuous file** at least 3,603 seconds long and pass
its manifest/name; short fixtures are BLOCKED, not looped with invalid headers.

As requested on 7 October, **CPU percentage is informational by default**:
exceeding 85% alone is not a playback failure. The priority is uninterrupted
audio, supported formats and absence of allocation failures. The physical
runners record `cpu_budget_percent: null`; use `--max-cpu-busy 85` with `run.py`,
`public_streams.py` or `pool_settle.py` only to reproduce the older headroom gate.
Historical reports without the new field retain their original 85% replay
criterion and original FAIL outcomes. This policy does not prove continuity
from an average CPU or decoder-progress figure.

Current acceptance budgets: free heap ≥8,192 bytes, largest
block ≥4,096 bytes, decoded audio/wall time between 0.9 and 1.1, HTTP response
<2 seconds. Switching permits ≤2,048 bytes of settled free-heap loss and
≤4,096 bytes largest-block loss after the warm-up cycle, with no extra tasks.
These are regression thresholds, not proof of a worst-case execution bound.
At least three CPU and decoder windows are mandatory; quiet production cannot
pass a CPU check by supplying no logs. Physical DMA underruns and audible
quality require T14's capture, not inference from REST status.

`stream_memory_study.py` runs a continuous paced AAC fixture with the same
memory/progress checks and an optional RX-owner diagnostic image. It verifies
the installed firmware hash, preserves settings, and atomically saves filtered
performance/status checkpoints every 30 seconds. An active checkpoint is
explicitly incomplete and is not an acceptance result. On normal completion,
the final report records all gates, Stop recovery and reboot. For example:

```text
python tools/esp32c3_tests/stream_memory_study.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --firmware firmware/development/esp32c3-output-first-rx-owner/app.bin --case hev2-44100-stereo --seconds 600 --output NEW_DIRECTORY
python tools/esp32c3_tests/summarize_stream_memory.py NEW_DIRECTORY --output SUMMARY.json
python tests/test-stream-memory-study.py
python tests/test-stream-memory-summary.py
```

The default duration is 600 seconds (ten minutes), as requested on 7 October;
`--seconds` can explicitly select a different duration.
It does not satisfy the one-hour soak criterion. The summarizer requires a
completed study, preserves original failures, checks RX snapshot completeness
and time coverage, and corrects aged network snapshots by their recorded age.
It reports actual RX allocation capacity separately from inferred allocator
headers and logical TCP receive credit. These asynchronous measurements cannot
be subtracted as if they were one simultaneous heap snapshot.

A diagnostic run identifies memory owners; its timing does not qualify the
uninstrumented firmware. It also does not replace physical audio continuity
measurement.

## OTA on the current production image

The runner requires the supplied image's embedded ELF hash to match the app
already running. This prevents accidentally testing a different build. It
checks the C3 chip/project and app size before sending anything. Uploads use
the same multipart contract as the browser.

```powershell
python tools/esp32c3_tests/ota.py --board http://BOARD_IP --firmware firmware/development/esp32c3-oled-native-production/app.bin --suite negative --suite roundtrip --suite slow --output .build/c3-tests/ota.json
```

For an upload during playback, start the shared server separately:

```powershell
python tools/esp32c3_tests/ota.py --board http://BOARD_IP --firmware firmware/development/esp32c3-oled-native-production/app.bin --suite while-playing --play-url http://PC_LAN_IP:8770/stream/lc-48000-stereo --output .build/c3-tests/ota-playing.json
```

The negative suite covers wrong chip/project, corruption, truncation, trailing
bytes, missing multipart boundary, SPIFFS target, oversized request, disconnect
and stalled sender. Positive cases verify the **other app slot and full ELF
hash after boot**, not only HTTP 200. Wi-Fi/playlist bytes and exposed system,
screen, timezone and control settings are compared in memory. Neither their
contents nor credential hashes are saved. This is not a byte-for-byte NVS
audit; for that use a private offline backup and partition comparison.

For ESP-IDF 6.0.3 and later, also exercise the HTTP parser's 64-to-32-bit
Content-Length guard and malformed/duplicate lengths:

```powershell
python tools/esp32c3_tests/http_headers.py --board http://BOARD_IP --firmware PATH_TO_INSTALLED_APP_BIN --output .build/c3-tests/http-headers.json
```

This sends less than 256 bytes per probe, regardless of the declared length.
Values above `UINT32_MAX` must return 413; invalid and conflicting lengths must
return 400. Every case checks the unchanged active image and settings. The
runner then reboots to restore the saved station. The local socket transport
test is `python tests/test-esp32c3-http-headers.py`; it does not replace the
actual SDK parser check on the board.

The pinned 6.1 HTTP source lacks the 6.0.3 guard, so the C3 build applies a
fingerprint-checked project-local backport. Do not weaken the expected 413 to
400: a later application error can hide an earlier narrowing conversion.
To run the source/boundary controls with the installed SDKs (Windows uses WSL
gcc; Linux uses gcc directly):

```powershell
python tools/test_httpd_content_length.py --idf-root PATH_TO_IDF_DEPENDENCY_ROOT --output .build/c3-tests/http-length-boundaries
```

This checks all 11 boundary values on each pinned SDK with ASan/UBSan, preserves
the already-fixed 6.0.3 file, rejects unknown sources, and demonstrates failures
with the original 6.0.2/6.1 assignments. Use a fresh output directory.

## Wi-Fi timing and external interrupt tests

Build otherwise identical diagnostic variants with Wi-Fi IRAM options on/off
using `build.ps1` and separate configs. `build-production.ps1` enforces the
RAM-saving options and is unsuitable for creating the baseline. Keep CPU/flash
clocks, SDK/library, access point, RSSI and fixtures unchanged; record hashes.

```powershell
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --suite boot-time --cycles 30 --sdkconfig PATH_TO_EXACT_CONFIG --output .build/c3-tests/boot-flash
python tools/esp32c3_tests/compare_latency.py --kind boot --baseline .build/c3-tests/boot-iram/report.json --candidate .build/c3-tests/boot-flash/report.json --max-ratio 1.25 --budget 30000 --output .build/c3-tests/boot-comparison.json
```

T13 needs a signal generator/logic analyzer and a separately identified
instrumented test build. Choose two unused pins from the actual board wiring;
do not reuse audio, OLED, BOOT or crystal pins. Feed timed edges to a test input
and toggle the output immediately on entry to the measured handler. Keep the
handler's placement/priority equal between variants. Capture input-to-output
latency during idle, playback/WebUI load and flash writes/OTA. Capture the
**actual Wi-Fi handler path separately** if claiming Wi-Fi interrupt latency:
a generic GPIO ISR only measures that ISR and system scheduling interference.

For each condition export measured values (never invented zeros):

```json
{
  "source": "external-edge-capture",
  "unit": "us",
  "firmware_sha256": "ACTUAL_IMAGE_HASH",
  "probe_description": "Actual pins, instrument, handler, priority and workload",
  "latency_us": []
}
```

Supply ≥30 real values (prefer thousands), then compare with `--kind irq` and
an application-specific `--budget` in microseconds. The parser rejects empty
captures and missing provenance. Budget/ratio must be chosen before the A/B
run. Without instrumentation this test is **NOT RUN**; QEMU and HTTP response
times cannot certify interrupt deadlines or flash-disabled behavior.

## Manual tests that cannot be replaced by host mocks

### T14 — browser, OLED and physical output

1. Open `/update.html` in an actual browser on the production board. Check the
   firmware-only choice and board-specific filename guidance. Upload the
   current app; verify progress, success, reconnect and changed app slot/hash.
2. Try a wrong-board image, cancel a partial upload and interrupt connectivity.
   Verify a readable error and working retry controls; the active app survives.
3. Play each codec and the two AAC transition streams. Observe the whole OLED,
   the browser format and current decoded rate/channels. There must be no stale
   split screen or falsely reported HE/PS. Reconnect the browser while playing.
4. Capture both audio channels through a suitable interface and the existing
   output filter. Generated stereo tones use distinct L/R frequencies. Check
   channel separation, duration and silent gaps during steady playback, rapid
   Stop/Play, WebUI load and codec changes. Record scope/audio files, firmware
   hash, settings and pass/fail; listening alone is not a bit-exact PCM test.

### T15 — interrupted flash write / boot recovery

Use a dedicated test board with a verified private backup and a working USB
recovery path. Schedule controlled power interruption during early/middle/late
app writes and around OTA activation. Restore power after each trial, query
the running app hash/partition, check preserved settings and successful playback.
Neither corrupted app activation nor boot loops pass. Save timing and flash
layout. No power-cut test is run automatically by these scripts. Automatic
first-boot rollback is currently not enabled, so a bootable crashing image is
a separate recovery limitation, not an expected successful rollback case.

### T16 — future decoder buffer reuse

Before accepting implementation, run old/new decode paths against identical
complete input and compare emitted PCM and persistent overlap/state after every
frame. Exercise all four AAC window sequences, distinct L/R, two SCEs, every
supported profile, reset, truncation, OOM and callback cancellation. Let the
consumer overwrite released PCM blocks and retain in-flight DMA blocks to
detect premature aliasing. Require identical results where bit-exact comparison
applies, bounded lifetimes and lower **peak live** RAM, then run T02–T11 on the
board. The current closed Espressif decoder exposes no internal overlap buffer;
test that state through subsequent decoded output or a supported debug API.
Do not create a fake internal-state test or mark this planned optimization done.

## Results and limitations

For sustained HTTPS playback, add `--sustained-protocol https` and a trusted
`--https-origin https://PC_LAN_IP:PORT` to `run.py --suite load` or `--suite soak`.
The default remains HTTP. Supply the laboratory certificate/key to the test
server and a matching trusted firmware image. Runtime fault checks also apply
when CPU profiling is disabled; serial capture is needed to observe UART faults.
See the [extended reserve tests](ESP32C3_TLS_RX_RESERVE_20261008.md), including
the original heap-trend, watchdog and host-transport failures.

For exact EOF checks over HTTPS, use `run.py --suite eof --eof-protocol https`
with the same trusted `--https-origin` and laboratory certificate/key options.
The default EOF transport remains HTTP. HTTPS entries use the `eof:https:`
prefix, and the report records `eof_protocol`. Both transports require decoded
playback before EOF, confirmed stopped REST samples, cleared PCM metadata and
a stopped WebSocket snapshot. A polling timeout fails the case even if earlier
samples already showed `stream ended`; no retry is added. Run
`python tests/test-eof-transport.py` for host checks of transport selection,
stale metadata, incomplete observations and timeout propagation.

For host-side HTTP failures, prefix the runner with
`python tools/esp32c3_tests/trace_transport.py --runner diagnostic -- run`,
followed by the same `run.py` arguments. For TLS wire tests, use
`--runner tls_records --` or `--runner tls_framing --` and their normal arguments.
The wrapper records connect/request/header/body timings, local TCP ports and
exception types/codes for the board's native HTTP endpoint only. It preserves
timeouts and exceptions, adds no retries or connection reuse, and saves no
URLs, headers or payloads. JSONL traces and a summary appear beside the output
directory. Run `tests/test-esp32c3-transport-trace.py` for behavior/privacy checks.

The [pipeline wait investigation](ESP32C3_PIPELINE_FLOW_20261006.md) measures
empty compressed-input queues, full PCM queues, DMA waits and completion
overruns on the physical C3. It includes a deliberate input-starvation control,
profile-on/off builds and exact PCM checks; it preserves the original heap
failure and does not change task scheduling or queue timeouts.

`CONFIG_YORADIO_PIPELINE_PROFILE=y` also supports the staged output backend.
It automatically selects staged DMA counters. `PERF FLOW_DEC` measures empty
encoded input and full PCM queues; `PERF FLOW_STAGED_OUT` measures empty PCM
queues, total submission time and completion-queue events. A separate DMA
wait is unavailable with the stock staged driver, so it is omitted rather
than reported as zero. Direct output retains `PERF FLOW_OUT` and its measured
DMA wait. These task-local wall times overlap and must not be added as CPU
usage. Leave profiling disabled for production timing comparisons.

`run_pipeline_profile_host.py` tests the real queue wrappers and extracted
staged/direct report helpers under ASan/UBSan, including disabled probes,
counter wrap, reset and ISR events during logging. `test-pipeline-flow.py`
checks both log formats; `test-pipeline-flow-evidence.py` verifies that the
older direct-output evidence still produces the same summaries.

For a bounded startup-margin experiment, set
`CONFIG_YORADIO_INPUT_PREFILL_MIN_MS=250` with
`CONFIG_YORADIO_INPUT_PREFILL_MS=500`. The minimum delays the early-full exit
without adding queue storage; Stop and a new generation still cancel promptly.
Both options remain off by default. `tests/run-input-prefill.py` exercises the
actual C function for both queue implementations at minima 0, 1, 250 and
500 ms, including coarse ticks, short/sparse input, cancellation and wrap.
Only hardware comparison can establish whether it improves continuity.

The [output-priority comparison](ESP32C3_OUTPUT_PRIORITY_20261006.md) tests
raising the direct-DMA output task from priority 6 to 8 above the decoder at 7.
It combines matched instrumented LPC12/LPC32 captures with a profile-off
seven-codec load, EOF, Stop/switch and OTA matrix. Original failed thresholds
remain in the report. Use `tests/test-output-priority-matrix.py` for analysis
boundary checks and `tests/test-output-priority-evidence.py` for retained data.

### FLAC predictor and high-depth playback

The [hot-loop study](ESP32C3_FLAC_HOTLOOPS_20261008.md) profiles exclusive host
CPU time in the actual decoder and compares optional bytewise Rice and LPC
unrolling experiments. It includes differential reader-state tests, exact PCM
checks and RV32 object-size audits. Host timing is not physical C3 timing;
both experimental compile definitions remain disabled by default.

The [physical Rice comparison](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md) uses fresh
matched IDF images and the default-off `CONFIG_YORADIO_FLAC_BYTEWISE_RICE`
switch. It compares two radio FLAC files, demanding HTTPS FLAC and a full-rate
HE-AACv2 control. `tests/test-flac-rice-physical-evidence.py` replays the archive,
checks firmware identities and verifies that missing/malformed telemetry cannot
be reported as a complete comparison. Original runtime and memory failures are
retained; DMA diagnostics do not establish acoustic continuity.

The [real-radio LPC study](ESP32C3_FLAC_RADIO_20261006.md) adds matched
120-second, 24-bit FLAC recordings with maximum predictor orders 32 and 12.
`capture_radio_flac.py` and the shared fixture server are board-independent;
`radio_flac_study.py` measures the C3 with alternating pair order. Use
`summarize_radio_flac.py` to separate predictor frequency, time-weighted CPU
saturation, decoder-task CPU and elapsed decoder cost. It also retains actual
audio/wall progress: a passed CPU gate alone does not prove gap-free output.
Run `tests/test-radio-flac-study.py` for statistics checks and
`tests/test-radio-flac-evidence.py` to replay the retained corpus measurements.

The [LPC optimization report](ESP32C3_FLAC_PREDICTOR_20261006.md) compares exact
PCM through segmented/contiguous/adapter paths, dense and sparse order-32
predictors, and physical CPU measurements. Use `summarize_terminal_cpu.py` for
short EOF diagnostics; it preserves the original verdict and does not replace
the sustained load gate. `diagnostic.py` now retains task-watchdog headings as
failures even when no register dump follows. The [depth report](ESP32C3_FLAC_DEPTHS_20261005.md)
retains the earlier CPU saturation and large-block allocation failures.

### AAC SBR layout regression

`python tests/test-aac-sbr-layout.py` validates retained lossless allocation/PCM
evidence and rejects missing measurements, false savings and failed cleanup.
For executable RV32 tests, use the build and runner in the
[SBR layout report](ESP32C3_AAC_SBR_LAYOUT_20261001.md). The variant tests eleven
inputs, delayed PS, 21 lifecycle segments and two allocation failures. The
[reset reproduction and repair](ESP32C3_AAC_RESET_20261001.md), checked by
`python tests/test-aac-reset.py`, adds six formats and 24 native/repaired reset
calls with byte-identical subsequent PCM. Wider streams and full-radio hardware
acceptance remain separate gates.

All automated suites return nonzero for FAIL or BLOCKED. Keep `report.json`,
`status.json`, `performance.json`, fixture hashes and exact app/config identity
together. Copy reviewable, sanitized results into `tests/results/` and retain
private keys, credentials and flash backups only in ignored local directories.

Known pre-existing failures: full-radio SBR allocation (HE/v2 core fallback)
and implicit SBR introduction without changed ADTS configuration. See
[hardware results](ESP32C3_CACHE_HARDWARE_20260930.md),
[stream format results](ESP32C3_STREAM_FORMAT_VALIDATION_20260930.md), and
[the memory optimization plan](ESP32C3_MEMORY_STABILITY_TODO.md).

Historical reports do not certify the newest binary. Record which of the
above cases actually ran and passed for each hand-off image.

### Bounded ICY song-title parsing

Run `node --test tests/esp32c3-icy-title.test.js` (WSL GCC on Windows). The
ASan/UBSan test compares the production streaming parser with the previous
whole-block `strstr`/`strchr` parser and the same 191-byte published prefix.
It covers every two-chunk split and byte-at-a-time input for boundary cases,
4080-byte blocks, empty/missing/truncated titles, quotes inside titles,
quote-semicolon precedence, UTF-8, embedded NULs, parser reset, independent
instances and 20,000 deterministic randomized blocks. The current corpus has
57,227 comparisons. This checks parser semantics and memory bounds; physical
streaming, title delivery to the WebUI and decoder output remain separate tests.

The parser retains 204 bytes of state instead of a 4081-byte metadata array.
It consumes the complete declared block even after finding the title, so the
following audio bytes remain aligned. An absent title preserves the current
title; an explicitly empty title clears it. Station-generation guards around
publication remain in `audio_service.c`.

For physical publication and audio framing, run:

```powershell
python tools/esp32c3_tests/icy_metadata.py --board http://BOARD_IP --host PC_IP --serial-port COM9 --firmware firmware/development/VARIANT/app.bin --output .build/icy-new-run
```

The seven synthetic ICY cases play the full-rate HE-AACv2 fixture, compare the
WebUI `meta` field with the expected title, check playback and runtime faults,
then stop and verify unchanged Wi-Fi, playlist and settings. Run on an awake
image with diagnostic logging for meaningful UART fault coverage. With a quiet
image, use `--functional-only` and omit `--serial-port`: its report explicitly
excludes UART runtime-fault coverage. An empty log is not evidence of fault-free
execution. Earlier reports that failed because of missing logs are retained. Each
case lasts seven seconds; this is a functional check, not a sustained load test.
`tools/audio_test_server/icy.py` has no board commands and can serve any HTTP
player. `python tests/test-icy-server.py` checks its byte framing and actual HTTP
responses, including the maximum 4080-byte metadata block.

The [ICY and receive-memory report](ESP32C3_ICY_RX_MEMORY_20261007.md) retains
the physical ICY/OTA results, matched receive-copy experiment and its original
failed heap gates, with exact firmware/config identities.

## Controlled TLS record growth

The [HTTP/TLS RFC audit](ESP32C3_HTTP_TLS_RFC_AUDIT_20261007.md) maps framing,
timeouts, fatal-error teardown and closure requirements to reproducible host
tests on ESP-IDF 6.0.3/6.1. The pre-adapter EOF correction now distinguishes
TLS `close_notify` from raw EOF, with independent linked-image and physical
fixtures below. Passing body-parser tests alone does not certify HTTPS.

`tools/esp32c3_tests/tls_records.py` checks full-rate AAC with 1 KiB and 16 KiB
TLS plaintext records, including growth after the decoder has started. Use only
an awake profiling image whose manifest explicitly sets `laboratory_only: true`
and `extra_trust_ca_sha256` to the generated local CA hash. The image must keep
the complete normal certificate bundle and full 16 KiB input capacity; only a
dedicated lab image adds the temporary CA. Restore a normal image afterwards.

```powershell
python tools/esp32c3_tests/tls_records.py --board http://BOARD_IP --host PC_IP --serial-port COM9 --firmware firmware/development/LAB_VARIANT/app.bin --ca .build/record-ca/ca.pem --cert .build/record-ca/server.pem --key .build/record-ca/server.key --output .build/record-test-run
```

Add `--pacing-ratio 1.0` for real-time delivery. The historical default is
`1.02`; keep that explicit when reproducing earlier queue/heap-growth failures.
Reports and server events record the ratio. Changing delivery timing does
not change or relax the original runtime, heap, full-format or record-size gates.

The default four modes run for 75 seconds each, with frequent WebUI polling,
CPU/heap evidence, idle recovery and saved-settings checks. `--mode grow` limits
the requested scope. The runner verifies exact generated TLS record lengths
and rejects retries or truncated record evidence. For the growth case it also
requires full-rate PCM before the first large record. A server-side successful
write alone cannot pass the playback check. Original memory-gate failures must
be retained. `record_observations` freezes each checked event snapshot before
Stop; the separate final server trace can include later failed socket writes.
See the [physical allocation-boundary results](ESP32C3_TLS_RECORD_MEMORY_20261007.md).
The [shared server guide](../tools/audio_test_server/README.md#full-sized-tls-record-tests)
documents certificates and host-side byte/record checks.

Use `--mode alternate --seconds 600` for a full ten-minute record-allocation
soak. The server keeps a 15-second tail beyond the observation and sends
`close_notify` on normal completion. Intentional client Stop and failed writes
remain visible in the separate final trace.

## HTTPS completion and truncation

```powershell
python tests/test-tls-framing-server.py
python tests/test-stream-http-reader.py --idf C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6 --output .build/http-eof-host
python tools/esp32c3_tests/tls_framing.py --board http://192.168.100.4 --host 192.168.100.253 --serial-port COM9 --firmware <lab-app.bin> --ca <ca.pem> --cert <server.pem> --key <server.key> --output .build/http-eof-board
```

The physical runner checks all eight modes documented by the
[shared HTTPS server](../tools/audio_test_server/README.md#https-body-completion-fixtures).
It requires an awake profiling image explicitly labelled with the test CA,
the ordinary full root bundle and full-sized TLS input capacity. It does not
flash automatically. Installed ELF identity and settings preservation are checked.

Complete Content-Length/chunked bodies and an unframed body ending with
`close_notify` must finish as `stream ended`. A short declared body, a missing
terminal chunk or an unframed raw TLS EOF must finish as `stream read failed`.
Every mode must first show full-rate/full-channel decoded audio. Expected TLS
errors in negative fixtures are distinct from decoder/allocation/panic failures.
The host runner checks real parser/adapter code with scripted transport seams;
the server test checks real TLS on loopback; only the physical runner checks
the board. None of these status checks establishes acoustic or PCM identity.

Use `verify_http_link.py --elf <firmware.elf> --sdkconfig <sdkconfig> --objdump <riscv-objdump> --output
<report.json>` to verify the actual linked HTTP and TLS-wrapper call paths.

## CPU diagnostics without a separate profiler stack

The optional [TLS receive-path profiler](ESP32C3_TLS_PATH_PROFILE_20261008.md)
measures nested HTTP, TLS, socket readiness, GCM and hardware AES-CTR calls in
`radio_stream`. Its counters measure inclusive wall time, not CPU time. Replay
them with `tools/esp32c3_tests/tls_path.py`; preserve damaged/incomplete captures
as failures rather than silently dropping them from the comparison.

The [GHASH experiment](ESP32C3_GHASH_EXPERIMENT_20261008.md) preserves exact
field arithmetic and independently generated GCM tag checks, but does not
improve the heavy physical FLAC case. Its optional build flag stays disabled;
the host math seam does not qualify complete TLS authentication or performance.

The [1/2/5 ms FreeRTOS tick experiment](ESP32C3_FREERTOS_TICK_20261008.md)
compares only the heavy HTTPS FLAC and HE-AACv2 cases. It retains original
runtime and heap gates, uses staged-DMA counter deltas after warmup, and treats
CPU utilization as informational. Tick changes also affect delay quantization;
the experimental overlays do not change the production default.

For new public-stream reports, use
`python tools/esp32c3_tests/summarize_public_windows.py --input <results> --output <summary.json>`.
It clips every CPU window to the recorded station start/end. Short failed runs
with fewer than four samples have no aggregate CPU value; samples from the next
station cannot fill the gap. The older `summarize_public.py` remains available
for historical reproduction and can overrun short failed playback windows.

The [PC18 production-adapter report](ESP32C3_AAC_HIGH_ADAPTER_20261003.md)
records the latest owner, QEMU task-interleaving, memory-failure, reset and
physical-radio qualification. Run `tests/test-aac-high-adapter.py` for retained
evidence/precision guards and `tests/test-public-window-summary.py` for window
isolation. Neither passing QEMU nor a successful OTA upload certifies long-term
HE-AAC playback on the complete radio.

For tight C3 HE-AAC budgets, add `sdkconfig.cpu-profile-http.defaults` after
`sdkconfig.cpu-profile.defaults`. This enables `CONFIG_YORADIO_CPU_PROFILE_HTTP`:
the existing `/api/native/status` handler samples runtime counters at most once
per five seconds, using the HTTP task's existing stack. It does not create the
normal 4096-byte `cpu_profile` task. Runtime accounting and the small previous
counter table still have overhead; this is not an uninstrumented production image.

Poll status regularly using the physical `memory.py` or `run.py` suites. Without
polling there are no periodic CPU samples. Preserve the exact config with the
report, and check the HTTP task's stack high-water mark as well as decode/output
tasks. Under `--suite switch`, use at least three cycles. Never label the CPU
usage of reduced-rate AAC-core fallback as full HE/SBR performance.

## OTA during full-format playback

For OTA during playback, `ota_diagnostic.py --case hev2-44100-stereo` requires
three consecutive full-rate/profile/channel observations before uploading.
Use `--https-origin https://PC_IP:8771 --tls-cert <server.pem> --tls-key <server.key>`
to exercise HE-AACv2 and TLS reception together. The selected fixture hash,
transport and actual pre-upload status are saved. The image must already
trust the server certificate; this does not disable verification.
`ota.py --play-fixture <name>` enables the same format gate for a separately
controlled `--play-url`. Run `python tests/test-ota-playback-format.py` to verify
rejection of core fallback, wrong channels/rates and transient matches.

OTA reports also retain a `timeline` on the same host monotonic clock used
by serial capture. Each upload, playback readiness check, boot verification
and final restoration reboot has persisted begin/returned/raised boundaries.
`returned` only describes a completed call; the original acceptance case
still decides PASS/FAIL. Response bodies and private exception messages are
excluded. Use `python tests/test-ota-timeline.py` to check timing persistence
and exception propagation. Correlate TLS errors with these actions without
automatically exempting errors close to an intentional reboot.

### Filtered TLS error codes

Acceptance and diagnostic serial captures retain a signed `mbedtls_return`
and an allowlisted `operation` for the exact ESP-IDF messages emitted by
`esp_mbedtls_dynamic_impl.c` (`fetch_input`, decimal `-ret`) and
`esp_tls_mbedtls.c` (`read`, `write`, `handshake`, hexadecimal `-ret`). For
example, `error=80` and `read error :-0x0050` both represent return `-80`.
The component is retained, so propagation through multiple layers is visible;
two log rows do not necessarily mean two independent failures.

Unknown or malformed messages remain generic TLS failures. Appended text,
hosts, URLs and certificate subjects are discarded. Allocation-size evidence
and the separate certificate-bundle rejection marker are preserved. A numeric
handshake code alone does not satisfy the certificate-rejection test, and
being close to a reset does not automatically excuse an error. Earlier
archives lacking a numeric code cannot be retroactively assigned one.

```powershell
python tests/test-tls-error-codes.py
python tests/test-serial-telemetry.py
python tests/test-esp32c3-tls-dynamic-evidence.py
```

## PCM-tail submission and EOF

The staged output must flush its final partial block before publishing EOF and
discard software PCM/resampler history at a new stream generation. Host tests
cover real output/task code, including failed writes and Stop/Play races:

```powershell
python tools/codec_benchmark/run_output_boundary_host.py --output .build/output-boundaries
python tests/run-output-task-boundaries.py --output .build/output-task-boundaries
python tests/test-pcm-tail.py
```

For physical driver-submission checks, use an awake C3 image built with
`CONFIG_YORADIO_STAGED_DMA_PROFILE=y`, the staged PDM backend, and the current
PCM flush/end diagnostic markers. Generate the shared short FLAC fixtures:

```powershell
python -m tools.audio_test_server.generate_pcm_tails --output .build/pcm-tail-fixtures
python tools/esp32c3_tests/pcm_tail.py --board http://192.168.100.4 --host 192.168.100.253 --serial-port COM9 --fixture-manifest .build/pcm-tail-fixtures/manifest.json --output .build/pcm-tail-board
```

The runner controls playback, starts its local server, and leaves the board
stopped. It does not flash or restore firmware. Supply `--tls-cert <server.pem>
--tls-key <server.key>` to add HTTPS; the image must trust that valid test CA
and verify the server hostname/address. Keep private keys outside saved evidence.

One warmup establishes cumulative counters, then 30 files per protocol check
fresh EOF, exact remaining frames, padded driver bytes, zero write errors and
inactive playback status. Missing, merged or out-of-order diagnostic records
fail the test. It stops at the first mismatch, preserving reports and raw
diagnostic rows. The 512-frame stereo output pads only its final partial block.

These counters prove submission to the driver, not physical DMA drain or
analog PCM identity. Idle queue-overrun counts are not a continuity test for
these tiny files. Run separate sustained and transition checks; see the
[original defect and repair](ESP32C3_PCM_TAIL_AUDIT_20261009.md).
The [2026-10-09 physical follow-up](ESP32C3_PCM_TAIL_BOARD_20261009.md) records
60 successful measured short-file cases plus sustained/all-codec regression,
with a frozen archive that can be replayed without a board.

The [RAM profile report](ESP32C3_AAC_RADIO_RAM_20261001.md) includes the physical
comparison and the distinction between elapsed decode-call time and total
FreeRTOS CPU utilization.

## TLS errors around an explicit reboot

Use the paired control when TLS messages appear near a requested reboot.
It compares full HE-AACv2 HTTPS playback against playback followed by Stop,
cleared PCM state and settled heap recovery. Three pairs reverse their order
in the middle cycle. Persisted action boundaries, numeric TLS errors and
software-reset causes distinguish playback, Stop and reboot intervals.

```powershell
python tests/test-reboot-tls-review.py
python tools/esp32c3_tests/reboot_tls.py --board http://192.168.100.4 --host 192.168.100.253 --serial-port COM9 --firmware firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/app.bin --ca <ca.pem> --cert <server.pem> --key <server.key> --cycles 3 --output .build/reboot-tls-new
```

The selected awake profiling image must already be installed and trust the
valid laboratory certificate in addition to the normal public roots. The
runner does not flash, preserves saved settings and leaves playback stopped.
Use an outer controller to restore the original application and playback;
keep keys and private settings out of archived evidence. Use a fresh output
directory for every run.

An operational trial passes only with full fixture format, one software reset
inside the explicit reboot interval, verified image/partition after boot and
no recorded decoder, allocation, panic, watchdog or capture fault. A TLS
message still yields `REVIEW_REQUIRED`, including during Stop or reboot.
The numeric code and controlled comparison must explain its scope; proximity
to a reset alone never makes it harmless. These short controls do not replace
sustained playback or analog checks.

## Experimental FLAC input capacity after decoder initialization

The [matched switching comparison](ESP32C3_SWITCH_CAPACITY_CONTROL_20261009.md)
adds a cross-stage recovery check: compare every later settled idle endpoint
to the first switch-cycle baseline, including after EOF and TLS record
growth. A new local baseline must not hide earlier contiguous-capacity loss.
Its frozen replay retains interrupted requests and original failed verdicts.

`CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS` defaults to `0`. With adaptive input,
the permanent TLS reserve and the custom FLAC decoder enabled, a nonzero
value lets the stream task restore additional packet slots after the current
FLAC generation produces PCM. The saved input-buffer target remains the
upper bound. AAC, MP3, Vorbis and Opus do not request this expansion.

At the usual minimum of four 2,060-byte slots, value `4` allows eight slots:
8,240 additional payload-storage bytes, plus allocator overhead. Before each
allocation, the producer checks for 32 KiB of remaining internal free heap.
This is advisory headroom, not a reservation: concurrent allocations and
fragmentation can still make allocation fail. A partial expansion is allowed.

The FLAC adapter allocates its channel workspace and encoded-frame window
while parsing STREAMINFO. Expansion is deferred until PCM exists, after
those initial allocations. It does not change sample precision or codec
arithmetic. Stop, EOF, errors and station changes reduce the slot limit again.
Ordinary shrink retains the earliest resident buffers and frees idle excess
slots immediately. Busy excess slots retire only after the consumer returns
them. A subsequent connection starts with the minimum limit even while old
leases are being returned. It must not replace idle baseline buffers with
later allocations that divide a previously contiguous free region. Actual
TLS allocation pressure can still reclaim any idle slot above the minimum
resident count; retention ranks existing pointers and tolerates those holes.

Host checks compile the actual queue, TLS allocator policy, HTTP disposal and
stream task under AddressSanitizer and UndefinedBehaviorSanitizer:

```powershell
python tests/run-adaptive-input.py --output .build/input-queue-new
python tests/run-tls-large-reserve.py --output .build/input-reserve-new
python tests/run-stream-connection-retry.py --flac-input-growth --output .build/flac-growth-stream-new
python tests/run-stream-connection-retry.py --adaptive-input --output .build/flac-growth-disabled-new
python tests/run-input-prefill.py --output .build/flac-growth-prefill-new
```

The reserve suite includes an enabled four-slot variant: insufficient heap,
partial allocation failure, changing heap headroom, a smaller saved target,
occupied-slot retirement, intact FIFO payloads and an unchanged live TLS
reserve. Queue and reserve regressions also cover idle baseline buffers with
busy added buffers (READING, READY and WRITING), Stop/new-connection overlap,
stable baseline addresses, and reclamation holes without dropping below the
minimum. The stream suite checks one expansion per generation, delayed
readiness, stale generations, AAC exclusion and cleanup after read errors.
Queue stress includes 30,000 packets with concurrent consumption, reclamation
and limit changes. These checks validate lifetimes, not hardware scheduling.

Before changing the default, compare matched firmware with extra slots `0`
and `4` on heavy HTTPS FLAC. Record whole-run and steady-state DMA events,
input waits, CPU, heap/largest block and settled recovery. Then exercise
FLAC-to-full-HE-AAC/PS switching, EOF, TLS record growth and OTA. Preserve all
failed observations; zero DMA events alone do not prove unchanged analog
sound quality.

The [input-retention study](ESP32C3_INPUT_RETENTION_20261009.md) adds continuous
allocation-owner snapshots and a 60-second idle period without HTTP polling.
Keep the initial free-region baseline as well as the first switch baseline:
loss during the first cycle or within a size-class tolerance must remain
visible. Its offline replay retains the original early TLS-server shutdown
faults and the corrected-harness comparison separately.

## WebUI TCP handshake diagnostic

`CONFIG_YORADIO_WEB_TCP_PROBE=y` is a default-off physical diagnostic,
requiring `CONFIG_YORADIO_NETWORK_HEAP_PROFILE`. It records port-80 handshake
metadata in a bounded 64-event ring (1,024 RTC bytes). It does not allocate
packets, change TCP return values, add retries or extend request timeouts.
The existing WebSocket status task drains the ring and requests network
snapshots once per second, independently of incoming HTTP requests. Its
profiling interval includes the diagnostic work; these builds are not
production CPU benchmarks.

TCP event frames contain a sequence number, low 32 bits of the device's
microsecond clock, peer port, direction (`0` receive, `1` transmit), flags,
PCB state before/after receive, output result, pending accepts and dropped
event count. State/pending `255` means unavailable; receive result `0` is
not evidence of packet acceptance. IPv4 SYN/SYN-ACK and RST output is
observed. Established data payloads, IP addresses, HTTP headers, URLs and
credentials are not retained. Outgoing success means acceptance by the IP
output path, not delivery to the computer.

Events are recorded on wrapper return: a SYN-ACK generated inside input can
appear before its corresponding received SYN. Serial arrival time includes
the consumer/logging delay. Reject incomplete sequences or nonzero dropped
counts as a complete connection trace. Listener frames report SYN_RCVD,
ESTABLISHED and listener counts, with `backlog_supported` explicitly stating
whether the SDK has TCP listen-backlog accounting. Zero pending/backlog
values with this flag off must not be interpreted as an empty accept queue.

Host wrapper checks free/mutate input packets inside the real-call double,
verify argument/result preservation, handshake states, filtering, queue
saturation and unsigned index wrap, under ASan/UBSan with backlog on/off:

```powershell
python tests/run-web-tcp-probe.py --output NEW_DIRECTORY
python tests/test-esp32c3-transport-trace.py
python tests/test-web-tcp.py
```

`TransportTrace(..., capture_socket_ports=True)` additionally saves the local
port before `socket.create_connection` closes a failed socket. It retains the
original connection attempt, timeout and exception. Pair that port and time
window with device events; do not count the enclosing request's repeated
exception as another failed TCP connection. A firmware ELF audit must verify
both input/output wrappers are actually linked into lwIP before deployment.

The [first physical TCP-probe repeat](ESP32C3_WEB_TCP_PROBE_20261009.md)
passes application checks but rejects the complete TCP trace because USB
output loses characters and merges lines. Preserve this distinction:
successful offline replay reproduces the failed telemetry gate too.

The current v2 wire format replaces verbose `PERF WEB_TCP` / `WEB_LISTEN`
lines with 58-byte records (59 after CRLF translation). Every frame has a
9-byte `PERF TC2:`, `PERF TL2:` or `PERF TS2:` header, five eight-digit
lowercase hex words, eight hex CRC digits and a newline. CRC-32/ISO-HDLC
uses seed zero over the first 49 ASCII bytes, including the frame type.
It uses the ESP ROM implementation and is computed outside lwIP's core lock.

| Frame | Five words, in order |
| --- | --- |
| TC2 event | Sequence; device microseconds; port in bits 0–15, direction 16–23, flags 24–31; before/after/signed result/pending as four bytes from least significant to most; dropped count |
| TL2 listener | Sample sequence; age in ms; SYN_RCVD low 16 bits and ESTABLISHED high 16 bits; listener/backlog/pending/backlog-supported as four bytes; reserved zero |
| TS2 watermark | Generated event sequence; device microseconds; dropped count; queued count; last emitted event sequence |

`tools/esp32c3_tests/web_tcp.py` decodes these frames and rejects malformed,
merged or CRC-damaged records. `window()` requires event/listener continuity,
zero drops and periodic watermarks; a watermark exposes missing final events
even if no further connection is made. It reports the actual first/last
qualified anchors and the unqualified edge durations explicitly. It rejects
watermark/listener coverage gaps exceeding 2.5 seconds. Do not repair damaged
text or treat bytes outside those anchors as complete telemetry.

Short records reduce output traffic but do not guarantee USB delivery.
Host sanitizer runs decode actual C-generated frames independently with
Python's CRC implementation. Parser tests also delete/change every hex digit,
merge lines and remove final events to check that corruption is rejected.
