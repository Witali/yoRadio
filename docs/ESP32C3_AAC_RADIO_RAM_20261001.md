# Full-radio AAC RAM profiles — 2026-10-01

## Result so far

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
