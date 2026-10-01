# Full-radio AAC RAM profiles — 2026-10-01

## Result so far

**The broader matrix still fails full-rate HE/v2 after preceding playback.**
Keep this profile experimental. The clean-start result below is insufficient
to qualify station switching; investigate allocator geometry and transient
network demand before changing product defaults.

The compact service/Wi-Fi profile plays the retained AAC-LC 48 kHz stereo,
HE-AAC 48 kHz stereo and HE-AAC v2 44.1 kHz stereo streams on the physical C3.
Each was observed for 35 seconds after a fresh boot, with WebUI polling.
The earlier baseline still falls back to core-only PCM for HE/v2.
This is an initial playback result, not completed production qualification.

No AAC arithmetic, sample rate, channel support or decoder allocation size
changes in this profile. The separate lossless SBR layout experiment is not
enabled. Deep sleep is off. The saved 10-block compressed buffer is unchanged.

## Before and after

Both columns use heap functions in Flash, USB INFO logs, no allocation tracer
and no runtime-profiler task. Values are observed free/largest heap bytes after
the first decoded frame, not exact isolated static savings.

| Input | Baseline output; free / largest | Compact profile output; free / largest |
| --- | --- | --- |
| AAC-LC 48 kHz stereo | Correct; 65208 / 43008 | Correct; 77768 / 47104 |
| HE-AAC 48 kHz stereo | **Failed:** 24 kHz core; 61644 / 43008 | Correct; 23556 / 7680 |
| HE-AAC v2 44.1 kHz stereo | **Failed:** 22.05 kHz mono core; 63412 / 43008 | Correct; 23704 / 7680 |

The compact profile's minimum-ever heap reaches **13636 bytes** during this
sequence. LC's observed free-heap difference is 12560 bytes. Do not subtract
HE rows as a RAM regression: only the new image allocates and runs full SBR/PS.
Wi-Fi traffic and allocator rounding affect these observations.

In the successful continuous sequence, elapsed decoder-call time divided by
generated audio duration is 18.00% for LC, 36.40% for HE and 41.01% for HEv2
([windows and calculation](../tests/results/esp32c3-aac-radio-ram-20261001/decode-work.json)).
This includes time spent inside decode calls and any preemption during them;
it is not total CPU utilization or a no-regression comparison against full HE
on the failing baseline. Dedicated task accounting remains to be measured.

The selected build profile, `sdkconfig.aac-ram.defaults`, changes:

- BOOT-button and output stacks: 4096 → 2048 bytes each.
- WebSocket status stack: 8192 → 4096 bytes. Total requested stack saving: 8192.
- Wi-Fi static RX buffers: 10 → 6, approximately 6400 payload bytes.
- Dynamic RX/TX limits: 32 → 16. These cap peak demand; they are not permanently
  reserved arrays whose full nominal size can be counted as freed RAM.
- Heap routines remain in Flash, as in the comparison baseline. This is not
  an additional saving relative to that baseline.

The shared **16384-byte decoder stack** remains intact for Opus. TLS buffers,
PCM/DMA queues and the user-selected compressed ring are unchanged. Reduced
service stacks still require worst-path WebUI/OTA measurements; reduced Wi-Fi
buffer limits require high-bitrate and reconnect tests.

## Rejected early-reservation experiments

`CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE` is a separate, disabled placement
experiment. It reserves the original 55128-byte SBR owner before PCM/core
allocations, then transfers it to the SDK through its allocation hook. It does
not save bytes. TLS slot 1 isolates decoder-task context; slot 0 is left for
the platform. Unused reservations are released after LC output or on close.
Actual SBR/control allocation failure is reported instead of allowing the
SDK's silent reduced-rate fallback.

Both early physical trials failed AAC opening, including LC. The first image
returned allocation error -2; adding the compact service profile changed the
observed error to -1 but did not produce PCM. These images are **rejected**.
The pinned AAC initialization code maps nested allocation failure to generic
failure -1. The current experiment therefore releases the pending reserve and
retries opening once for either error. That recovery has host tests, but is
not claimed physically qualified. The working radio profile keeps reservation
off and uses the normal allocation order.

Host ASan/UBSan checks cover transfer, zero initialization, task isolation,
early failure/retry, SBR/control OOM, LC release and clean close. On the actual
RV32 decoder in QEMU, the final reservation implementation produces **328770
stereo output frames byte-identical** to the retained reference, including
output conversion. This proves equivalence for the tested sequence, not that
its allocator placement is beneficial on the complete radio.

## Reproduction and artifacts

```powershell
./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-aac-ram-radio `
  -Sdkconfig build-aac-ram-radio/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults')
```

Use a new build/config directory when comparing profiles. Existing sdkconfig
values override defaults. The saved application is
[`esp32c3-aac-ram-radio/app.bin`](../firmware/development/esp32c3-aac-ram-radio/app.bin),
ELF identity `7cd52c51f8092ba3c78e0cd5a9f5558585f4c00d72a202ceb87e9e296d3d8e55`.
It is an application-only OTA image, not a merged factory image.

[Evidence](../tests/results/esp32c3-aac-radio-ram-20261001/) retains settings
equality checks, fixture hashes, status samples, RAM logs, failed trials and
QEMU provenance. Wi-Fi, playlist and exposed settings match before/after each
installation and memory survey; their contents are not included in reports.
Earlier physical binaries predate the final reservation retry; the evidence
manifest explicitly distinguishes them from the final host/QEMU sources.

Remaining acceptance: all-codec/EOF/switch/fault matrix, stack and physical CPU
load, sustained HE/v2, maximum compressed-buffer setting, HTTPS and OTA under
the compact profile. The known implicit LC→SBR transition with identical ADTS
headers also remains open. Product defaults have not been changed.

## Broader matrix on the same physical image

[Complete results](../tests/results/esp32c3-aac-radio-ram-20261001/acceptance/report.json):
46 PASS, eight playback/transition failures, and one unexecuted switching test
reported as FAIL because the invocation requested two cycles where three are
required. That last item is a test invocation error, not a firmware failure;
repeat it with profiling firmware and at least three cycles.

MP3, FLAC, Vorbis, Opus and LC pass both automatic detection and explicit codec
selection. All 22 terminal-EOF checks pass, as do network interruption, recovery,
redirect, jitter, Stop/Play generation ordering and WebSocket reconnect checks.
EOF pass is independent of full HE acceptance: the six HE/v2 HTTP cases and
both format-transition sequences still fail their full-output requirements.

At failed HE first-frame checkpoints, free heap is roughly 79 KB while the
largest block is 47104 bytes, below the 55128-byte SBR request. This distinguishes
the contiguous-block problem from simply running out of all heap. It does not
yet identify which live allocations prevent coalescing. Do not qualify the
profile from the earlier clean-start continuous-stream test alone.

## Physical CPU and stack measurements

The ordinary 4 KiB profiler-task build again fails the 55128-byte SBR request:
callbacks report 69680/72548 free bytes with a 51200-byte largest block.
Its HE/v2 CPU readings measure **fallback**, not full HE, and are excluded
from full-output comparisons. MP3, Vorbis and Opus pass; the generated long
24-bit FLAC fixture returns custom decoder error -4, also recorded in the
[older QIO/DIO acceptance](ESP32C3_QIO80_ACCEPTANCE_20260930.md).
[Profiler-task evidence](../tests/results/esp32c3-aac-radio-ram-20261001/profile/summary.json).

`CONFIG_YORADIO_CPU_PROFILE_HTTP` reuses the existing HTTP task for the same
counter sampling and eliminates the separate profiler stack/TCB. It remains a
diagnostic option. After a fresh boot this image passes the following 35-second
streams with the original full-rate decoder:

| Input | Total CPU, mean | Decode-task CPU, mean | Minimum free / largest in sampled window |
| --- | ---: | ---: | ---: |
| AAC-LC 48 kHz stereo | 36.75% | 18.65% | 75472 / 65536 B |
| HE-AAC 48 kHz stereo | 50.72% | 36.08% | 17316 / 8192 B |
| HE-AAC v2 44.1 kHz stereo | 55.60% | 40.47% | 19388 / 9728 B |
| Opus 48 kHz stereo | 61.72% | 42.32% | 89604 / 73728 B |

[Raw records, intervals and summary](../tests/results/esp32c3-aac-radio-ram-20261001/http-profile/summary.json).
Means use runtime-counter samples 5–35 seconds after the first PCM checkpoint.
They are short HTTP-polling measurements, not worst-case load or long-soak
certification. No new QEMU calibration coefficient is inferred from them.

Minimum unused stack over this sequence: HTTP 4372 B, WebSocket status 1896 B,
BOOT 1500 B, output 1228 B, decoder 5036 B. This supports the initial smaller
service-stack choice for these paths; TLS, OTA and broader stress remain gates.
The diagnostic image's heap layout also differs from the uninstrumented image.
Successful allocation here does not erase the latter's broader-matrix failures.

## Repeated switching and bounded Wi-Fi follow-up

The corrected three-cycle test runs 12 switches among Opus, LC48, HE48 and
HEv2 on the HTTP-profiler image. Five switches fail full HE/v2 output. Settled
idle heap returns to 145020–145036 B and the largest block to 94208 B; this
sequence does not demonstrate a growing leak. The earlier two-cycle invocation
has now been repeated correctly; the result remains a playback failure.
[Switch evidence](../tests/results/esp32c3-aac-radio-ram-20261001/http-profile-switch/switching.json).

The separate `sdkconfig.aac-bounded-wifi.defaults` caps dynamic RX and TX
buffers at six, after the compact profile's six static RX buffers. This is a
peak network allocation experiment, not a decoder payload reduction. The
uninstrumented physical image passes eight finite HTTP checks: LC48, HE48,
HEv2 and Opus, each with automatic and explicit codec selection. HE48 remains
48 kHz stereo and HEv2 remains 44.1 kHz stereo.
[HTTP evidence](../tests/results/esp32c3-aac-radio-ram-20261001/bounded-wifi/http/report.json).

This is not sufficient for a new production default: repeated switching,
high-bitrate/load, recovery, stack, TLS and OTA acceptance remain necessary.
The fixture server paces both finite-file and continuous routes at 1.02 times
playback rate; the previous failures cannot be attributed to an unpaced server.
