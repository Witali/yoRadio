# ESP32-C3 firmware testing

This document defines the acceptance tests added after the 2026-09-30 audit.
**A test exists, a test ran, and a test passed are three different states.**
Keep failed measurements. Never accept AAC-core fallback as successful HE-AAC.

The audio server is shared by **ESP32-C3, ESP8266, CYD and any other HTTP audio
client**. Only the device-control runner knows the native C3 WebUI API. The
server does not select a board, upload firmware, reset it or change credentials.

## Gaps found and corresponding tests

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
| C3-T16 | Future AAC buffer-reuse equivalence and error paths | Existing `run-esp32c3-stream-format.py`, new full-radio matrix and procedure below | New implementation must additionally pass PCM/state equivalence, ownership, cancellation/OOM and all HE/v2 acceptance cases. The optimization itself is still planned. |

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
```

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
