# ESP32-C3 firmware testing

This document defines the acceptance tests added after the 2026-09-30 audit.
**A test exists, a test ran, and a test passed are three different states.**
Keep failed measurements. Never accept AAC-core fallback as successful HE-AAC.

The [2026-09-30 physical results](../tests/results/esp32c3-acceptance-20260930/README.md)
record passing OTA checks and outstanding HE-AAC, EOF and HTTP-load failures.
Tests not run are identified separately from failures.

The subsequent [EOF correction and regression tests](ESP32C3_EOF_STATUS.md)
separate terminal playback status from full-rate HE-AAC acceptance. They include
a deterministic delayed-output regression and FFmpeg/FDK complete-file references.

For allocation phases, per-task stack margins and reproducible SBR structure
sizes, see the [AAC memory investigation](ESP32C3_AAC_MEMORY_20260930.md) and
`tools/esp32c3_tests/memory.py`. Its survey is separate from a passing load/soak test.

The audio server is shared by **ESP32-C3, ESP8266, CYD and any other HTTP audio
client**. Only the device-control runner knows the native C3 WebUI API. The
server does not select a board, upload firmware, reset it or change credentials.

The [IRAM placement audit](ESP32C3_IRAM_REDUCTION_20261001.md) compares matched
ELF/MAP files and physical playback/OTA evidence. The standalone
`tools/esp32c3_tests/iram_inventory.py` reports aliased SRAM capacity without
double-counting IRAM as additional DRAM. Auto Suspend is an optional,
hardware-specific experiment, not a global default.

The [physical DIO/QIO comparison](ESP32C3_FLASH_QUAD_20260930.md) records passing
standalone QIO 40/80 MHz tests with register checks, repeated flash reads and
AAC decoding. Run `python tests/test-esp32c3-flash-quad.py` to validate retained
evidence and rejection paths. This does not replace full-radio QIO acceptance.
The subsequent [full-radio QIO 80 MHz results](ESP32C3_QIO80_ACCEPTANCE_20260930.md)
retain both failures and passes; the production default remains DIO 80 MHz.

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
| C3-T08 | Long continuous playback on the full radio | `run.py --suite soak` | Default one hour, correct format throughout, responsive HTTP, real-time PCM progress, CPU/heap budgets. A shorter run is only a smoke test. |
| C3-T09 | CPU and memory with concurrent WebUI requests | `run.py --suite load` | 40 seconds per selected fixture, 100 ms polling, at least three stable CPU/decode windows, no allocation failure or core fallback. |
| C3-T10 | OTA regression against the exact current app | `ota.py` | Both slots used, uploaded ELF identity checked after boot, negative cases preserve active app, Wi-Fi/playlist/settings unchanged. Includes slow and playing-state uploads. |
| C3-T11 | Live browser-channel metadata after reconnect | `run.py --suite websocket` | Two fresh WebSocket connections receive `fmt` and playing state matching REST. Host stream-format tests already check OLED formatting and generation changes. |
| C3-T12 | Quantified Wi-Fi-placement boot/readiness A/B | `run.py --suite boot-time`, `compare_latency.py --kind boot` | At least 30 samples per configuration, same board/network conditions and selected regression/budget limits. This measures reboot-to-WebUI, not pure association time. |
| C3-T13 | Interrupt-latency A/B under flash/Wi-Fi load | Manual procedure below + `compare_latency.py --kind irq` | External edge timing, full provenance, at least 30 samples and an explicit absolute deadline. Host HTTP timing cannot substitute. |
| C3-T14 | Real browser rendering, OLED appearance and physical audio | Manual procedure below | Upload form/progress/errors are usable; whole OLED updates; stereo channels and audio continuity are checked physically. |
| C3-T15 | Power interruption during OTA | Manual procedure below | Dedicated recoverable test board boots the previous/new valid app after interruption at each stage; do not assume automatic rollback exists. |
| C3-T16 | AAC buffer-reuse equivalence and error paths | `run-esp32c3-stream-format.py`, `run-esp32c3-memory-trace.py`, `compare-pcm-wav.py`, real-decoder QEMU and full-radio matrix | Adaptive ADTS and 8 KiB PCM pass host OOM/retry checks and byte-identical fixture output. Full-radio HE/v2 and internal-state/exhaustive-profile coverage remain open. |
| C3-T17 | Stable terminal status after buffered decoder output | `tests/run-esp32c3-eof.py`, `run.py --suite eof`, `reference_eof.py` | EOF follows queued PCM; stopped REST/WebSocket status stays stopped and clears stream parameters. Exercise all eleven fixtures with AUTO/explicit codecs, late metadata, stale generations, cancellation and failures. Profile/rate acceptance remains a separate requirement. |

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
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --suite tls-rejection --https-origin https://PC_LAN_IP:8771 --tls-cert .build/untrusted-tls/cert.pem --tls-key .build/untrusted-tls/key.pem --output .build/c3-tests/tls-rejection
```

The negative test also requires the local TLS listener to record a certificate
rejection alert. An unreachable server alone cannot make this test pass.

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

Current acceptance budgets: CPU peak ≤85%, free heap ≥8,192 bytes, largest
block ≥4,096 bytes, decoded audio/wall time between 0.9 and 1.1, HTTP response
<2 seconds. Switching permits ≤2,048 bytes of settled free-heap loss and
≤4,096 bytes largest-block loss after the warm-up cycle, with no extra tasks.
These are regression thresholds, not proof of a worst-case execution bound.
At least three CPU and decoder windows are mandatory; quiet production cannot
pass a CPU check by supplying no logs. Physical DMA underruns and audible
quality require T14's capture, not inference from REST status.

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

## CPU diagnostics without a separate profiler stack

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

The [RAM profile report](ESP32C3_AAC_RADIO_RAM_20261001.md) includes the physical
comparison and the distinction between elapsed decode-call time and total
FreeRTOS CPU utilization.
