# TCP half-close ownership fix — 2026-10-01

## Finding

The RTC TCP pool exposed a defect in the pinned esp-lwIP revision
`fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e` (ESP-IDF 6.0.2). It also exists with
the SDK's ordinary heap allocator. This is independent of Flash Auto Suspend:
the physical pool failures were captured with Auto Suspend disabled.

Rejected OTA uploads send an error response, call `shutdown(fd, SHUT_WR)`,
briefly drain incoming data, and let HTTPD close the socket. This preserves
the browser's response when an upload is rejected before its body is consumed.
The socket can still own a PCB after TCP enters TIME_WAIT or LAST_ACK.

Two missing ownership transitions matter:

1. `lwip_netconn_do_close_internal()` treats read shutdown after write shutdown
   as a full close for FIN_WAIT_1, FIN_WAIT_2 and CLOSING, but omits LAST_ACK and
   TIME_WAIT. Consuming EOF can set `TF_RXCLOSED` without detaching the netconn.
   LAST_ACK completion then frees the PCB without notifying the netconn because
   `TF_RXCLOSED` is set. A later socket close accesses freed memory. This matches
   the delayed-close/free followed by socket-close path observed on the board.
2. TIME_WAIT reclamation under PCB pressure, and normal 2*MSL expiry, free the
   PCB without notifying a half-close owner which has not consumed EOF yet.
   The old socket can later access the freed or reassigned memory.

The [original hardware evidence](ESP32C3_TCP_PCB_POOL_20261001.md) remains a
rejected image. Host tests establish a matching defect in real TCP code;
they do not retroactively prove every earlier crash had this one cause.

## Correction

`tools/patch_lwip_timewait.py` generates project-local copies of `tcp.c` and
`api_msg.c` during CMake configuration. SHA-256 checks reject unaudited SDK
sources. The shared SDK checkout is never edited; original license headers
remain in the generated sources. The C3 build replaces exactly those two source
entries in the existing lwIP component, retaining its flags and dependencies.

- Recognize LAST_ACK and TIME_WAIT when read shutdown completes a prior write
  shutdown. Use the existing full-close path to detach callbacks and netconn.
- On TIME_WAIT release, notify a remaining half-close owner with `ERR_CLSD`
  after freeing the detached PCB, as the existing delayed-close path does.
  Keep queued receive data and EOF available; do not report a reset.
- Restart the TIME_WAIT timer traversal after notification because callbacks
  may change the list. Fully closed PCBs receive no extra notification.

TCP timers, capacity, retransmissions, OTA body validation and the bounded drain
are unchanged. There is no added permanent buffer, codec change, rate cap or
PCM quantization. The optional RTC pool remains a separate configuration.

## Reproducible host checks

Run under Linux/WSL with `cc`, AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
python3 tests/run-lwip-half-close.py --allocator pool --output /tmp/pool-fixed.json
python3 tests/run-lwip-half-close.py --allocator heap --output /tmp/heap-fixed.json
```

Use `--lwip /path/to/esp-lwip` if the pinned SDK is not in the repository's
`.idf/v6.0.2` directory. Add `--unpatched` to reproduce the defect. That run
intentionally returns nonzero and must not count as a passing fixed test.

The harness compiles real TCP, netconn, socket and IPv4 code, creates a TCP
loopback connection with a real handshake, and sends the response and FINs.
It uses upstream's deterministic unit-test OS shim, adapting its invalid-mailbox
initializer for non-zeroed heap storage. No TCP state machine is mocked.
For LAST_ACK only, a packet wrapper delays the real final ACK until after EOF
has been consumed. Timer tests advance TCP ticks and invoke the real slow timer.

| Scenario | Original RTC pool | Original heap | Fixed RTC pool | Fixed heap |
| --- | --- | --- | --- | --- |
| TIME_WAIT reclamation after EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| Reclamation before draining data/EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| TIME_WAIT expiry after EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| Expiry before draining data/EOF | FAIL | FAIL: use-after-free | PASS | PASS |
| LAST_ACK: EOF before final ACK | FAIL | FAIL: use-after-free | PASS | PASS |
| Ordinary full close, control | PASS | PASS | PASS | PASS |

Pool failures are detected when the old socket corrupts the new socket's PCB
ownership. Fixed cases check exact response/data, EOF, ownership of all 16
replacement PCBs, complete TCP cleanup, and sanitizer success. Retained output
and source hashes are in
[`tests/results/esp32c3-lwip-half-close-20261001`](../tests/results/esp32c3-lwip-half-close-20261001).

These host checks do not simulate FreeRTOS scheduling, Wi-Fi or Flash writes.

## Physical firmware and OTA

Saved image: `firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin`.
ELF SHA-256: `7b9414f9d153c1762d250755267c6ab5bf3603991ad0bbf4379262d94466dae3`.
Application SHA-256: `2da9c04a2a34df7892e36be44d676e067a5896774fac69cf9c4f6f16c8f030d9`.
Source commit: `5c35db7b`; the image was built before that commit with identical
source content and reports the preceding HEAD with a dirty suffix.

Native C3, CPU 160 MHz, DIO 80 MHz, dynamic Wi-Fi RX/TX 16, full native AAC/SBR/PS,
RTC PCB pool on; Auto Suspend, deep sleep and pool diagnostics off. The build
compiles the generated TCP/API files exactly once with no original duplicates.
IRAM reservation 43520 B, DRAM data 12620 B and BSS 31384 B: no extra static RAM
relative to the original pool profile. Compared with the no-pool control, the
pool itself still reserves 2688 B RTC RAM plus 16 B ownership flags in DRAM.

Initial OTA from the conservative control passed in 20.500 s, app0 to app1,
with exact destination ELF hash and unchanged Wi-Fi/playlist/settings.
The fixed image then passed **all 15 repeat OTA checks**, with **serial-health
PASS**, 106 retained records and zero panic/capture-error markers:

- Ten rejection/interruption cases: wrong chip/project, corrupt/truncated image,
  extra byte, missing boundary, SPIFFS target, oversized request, disconnect, stall.
- Four accepted uploads: round trips to app0/app1, OTA during playback, slow OTA.
  Their measured durations were 21.078, 20.860, 21.234 and 37.578 s; each verified
  its image hash and destination slot.
- Saved-station restoration. Wi-Fi, playlist and settings equality passed for
  every case; their private contents are not retained.

The serial log contains exactly five software resets: four accepted updates
and the requested final restoration reboot. There are no extra reset records.

The fixed image also passes **21/21 mixed-codec switches** over three cycles:
MP3 320 kbps, 16-bit FLAC level 8, Vorbis q10, Opus 510 kbps, AAC-LC 48 kHz,
HE-AAC 48 kHz and HE-AAC v2 44.1 kHz, all stereo. The first HE/v2 cycle retains
full SBR/PS output. WebSocket format/reconnect and saved-station restoration
pass, and the filtered serial capture has no fault markers. The largest idle
block is 114688 B at every checkpoint, with 17 tasks; last idle free-heap samples
for the three cycles are 146032, 146072 and 145988 B, within measurement noise.

The matched 35-second AAC CPU/memory survey also passes all three playback
checks, evidence capture and Wi-Fi/playlist/settings restoration. Mean task
runtime counters use samples 5..35 seconds after the first PCM checkpoint:

| Input | Original pool total / decode CPU | Fixed total / decode CPU | Fixed minimum free / largest |
| --- | ---: | ---: | ---: |
| AAC-LC 48 kHz stereo | 37.067% / 18.767% | 37.183% / 18.867% | 77040 / 65536 B |
| HE-AAC 48 kHz stereo | 51.217% / 36.167% | 50.967% / 36.200% | 20648 / 10752 B |
| HE-AAC v2 44.1 kHz stereo | 56.000% / 40.750% | 56.720% / 41.080% | 20924 / 10752 B |

Decode CPU changes are +0.100, +0.033 and +0.330 percentage points, within the
short-survey tolerance. This is not a worst-case latency or acoustic-continuity
measurement. The fixed survey's `tcpip` stack minimum is 2644 B. OTA worker
stacks must still retain their separately measured, much smaller OTA margins.
The final read-only snapshot confirms this image in app1 playing the saved
AAC station at 44.1 kHz stereo. Auto Suspend and deep sleep remain off.

This addresses the hidden-panic failure which disqualified the earlier pool
image. The earlier Auto Suspend
`Illegal instruction` failure remains unresolved; this finding alone neither
attributes it to Flash nor qualifies that separate placement profile.

Broader acceptance remains open: full-rate HTTPS under load, long soaks,
in-stream implicit SBR/PS transitions, 24-bit FLAC, and physical deep-sleep/RTC
interaction. Passing these recorded cases does not qualify all formats or
justify enabling every experimental memory option by default.

### Build and replay

From the repository root with the configured ESP-IDF 6.0.2 dependencies:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-tcp-pcb-pool-fixed -Sdkconfig build-tcp-pcb-pool-fixed/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults',
    'sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults',
    'sdkconfig.iram-safe.defaults','sdkconfig.tcp-pcb-pool.defaults')
```

Archive a successful build's app/config/manifest before testing. The commands
below assume that exact image is already installed; substitute the actual
board address, test-server LAN address and native USB port:

```powershell
python tools/esp32c3_tests/ota_diagnostic.py --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 `
  --firmware firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin `
  --output .build/half-close-ota
python tools/esp32c3_tests/diagnostic.py run --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 --suite switch --suite websocket --cycles 3 `
  --case mp3-320 --case flac-level8 --case vorbis-q10 --case opus-510 `
  --case lc-48000-stereo --case he-48000-stereo --case hev2-44100-stereo `
  --sdkconfig firmware/development/esp32c3-tcp-pcb-pool-fixed/sdkconfig `
  --output .build/half-close-switch
python tools/esp32c3_tests/diagnostic.py memory --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 --seconds 35 --output .build/half-close-memory
python tools/esp32c3_tests/summarize_memory.py --input .build/half-close-memory `
  --output .build/half-close-memory/summary.json
```

Do not run hardware suites concurrently: they share the board, serial port,
playback state and fixture server. Validate the retained campaign with
`python tests/test-lwip-half-close.py` and
`python tests/test-esp32c3-half-close-hardware.py`.

References: pinned [TCP implementation](https://github.com/espressif/esp-lwip/blob/fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e/src/core/tcp.c),
[netconn implementation](https://github.com/espressif/esp-lwip/blob/fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e/src/api/api_msg.c),
and [raw TCP ownership contract](https://www.nongnu.org/lwip/2_1_x/group__tcp__raw.html).
