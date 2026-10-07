# ESP32-C3 conservative IRAM profile — 2026-10-01

## Purpose

**Not qualified for production:** the smaller placement change recovers 3584
bytes of heap capacity, but HE/v2 still fall back to AAC-core output during the
first mixed-codec switching cycle. Successful clean-start playback is not enough.

The [larger IRAM/Wi-Fi trial](ESP32C3_WIFI_BUFFER_BALANCE_20261001.md) found an
`Illegal instruction` panic during OTA with Auto Suspend. Its cause remains
unresolved. This experiment keeps Auto Suspend **off** and retains Flash
driver, system, timer, logging, ROM-print and FreeRTOS ISR paths in IRAM.
It tests whether the smaller supported placement change can sustain full AAC
and the other existing codec families without relying on that failed profile.

Auto Suspend means automatically pausing a Flash write/erase to let the CPU
read code/data from that Flash, then resuming the write. It is unrelated to
MCU deep sleep. It permits additional code placement in Flash but depends on
chip support and timing; see [Espressif's explanation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/spi_flash/spi_flash_concurrency.html#flash-auto-suspend-feature).
This profile uses the normal cache-disabled Flash-write mechanism instead.

## Exact configuration and static result

- ESP32-C3 rev. 0.4, XMC-D embedded Flash, DIO 80 MHz, CPU 160 MHz, no PSRAM.
- Same compact service stacks and full native AAC/SBR/PS allocation/arithmetic.
  No PS relocation, PC16 representation, unpacked cache or early reservation.
- Static Wi-Fi RX=6, dynamic RX/TX=16. Six dynamic buffers were insufficient
  for the earlier high-bitrate FLAC transport, independently of code placement.
- Move ring-buffer ISR helpers and the OLED I2C master ISR into Flash using
  the SDK options. Disable posting events from an IRAM ISR; application GPIO
  handlers are registered with flags 0. Do not remove the event API itself.
- Deep sleep is off for hardware tests; the saved ten-block input ring is
  unchanged. All Flash encrypted-operation APIs remain enabled.

| Profile | Reserved IRAM | DRAM data | DRAM BSS | Static heap-capacity gain |
| --- | ---: | ---: | ---: | ---: |
| Matched baseline, dynamic Wi-Fi 6 | 47104 B | 12620 B | 31368 B | — |
| Conservative placement, dynamic Wi-Fi 6 | 43520 B | 12620 B | 31368 B | 3584 B |
| Conservative placement, dynamic Wi-Fi 16 | 43520 B | 12620 B | 31368 B | **3584 B** |

The [ELF/MAP inventory](../tests/results/esp32c3-conservative-20261001/inventory.json)
counts aliased IRAM/DRAM once. Dynamic limits change runtime peak demand, not
the static capacity. The [config comparison](../tests/results/esp32c3-conservative-20261001/config-diff.json)
against the previous conservative image contains only RX/TX limits and their
deprecated aliases, each 6 → 16. The linked application/codec source is unchanged.

The application uses its ring buffers from tasks. The SDK USB Serial/JTAG
driver registers its interrupt with flags 0, so it is masked when cache is
disabled. OLED I2C was already configured without `I2C_ISR_IRAM_SAFE`.
Re-audit these assumptions if an IRAM-safe caller is added. The name `safe`
in artifact paths is a historical short label, not a safety certification.

## Reproduce

Use a fresh build/config directory so previous saved settings do not override
the supplied defaults. Do **not** add `sdkconfig.iram-suspend.defaults` or
`sdkconfig.aac-bounded-wifi.defaults`.

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-iram-safe-wifi16 -Sdkconfig build-iram-safe-wifi16/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults', `
    'sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults', `
    'sdkconfig.iram-safe.defaults')
```

The saved app and exact config are under
`firmware/development/esp32c3-iram-safe-wifi16/`. ELF identity:
`fb48069ca32f416a82df70cc4776fb4fcfc03c5e125fe3b13a6e79f546858a0c`.
Build-source commit: `0a9b1f77`; size: 1538656 bytes.

The initial [application-only OTA](../tests/results/esp32c3-conservative-20261001/install-ota/report.json)
from the original non-Auto-Suspend firmware passed, with destination slot/hash
and in-memory settings/Wi-Fi/playlist equality checks. This installation alone
does not exercise OTA writes executed by the new image.

Use the diagnostic wrapper for subsequent memory or regression runs; it retains
panic PC/RA/cause and possible stack code addresses without raw stack contents:

```powershell
python tools/esp32c3_tests/diagnostic.py memory --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 `
  --output .build/conservative-memory
```

## Clean-start memory survey

After a software reboot, LC48, HE48 and HEv2 44.1 run in that order for 35 seconds
each, with 12 seconds stopped between streams. All three sampled playback checks,
the diagnostic-evidence check and settings/Wi-Fi/playlist equality pass.
[Raw survey](../tests/results/esp32c3-conservative-20261001/memory/report.json)
and [CPU/stack summary](../tests/results/esp32c3-conservative-20261001/memory/summary.json).

| Input / actual PCM | Total CPU, mean | Decoder CPU, mean | Sampled minimum free / largest |
| --- | ---: | ---: | ---: |
| LC, 48 kHz stereo | 36.950% | 18.800% | 79344 / 65536 B |
| HE, 48 kHz stereo | 51.167% | 36.217% | 22948 / 10752 B |
| HEv2, 44.1 kHz stereo | 56.033% | 40.967% | 23232 / 10752 B |

These are FreeRTOS runtime samples 5–35 seconds after first PCM, with ordinary
HTTP status polling, not the heavy WebUI-load test or a no-slowdown A/B result.
The minimum-ever free heap over the survey reaches 10476 bytes. Boot free heap
is 291584 bytes, 3584 above the matched baseline's 288000. Largest-block changes
reflect placement and allocator rounding; do not count them as extra RAM saved.
The decoder stack's large unused margin in AAC does not justify shrinking the
shared stack: the same task also runs the substantially deeper Opus decoder.

## Repeated mixed-codec switching

Three cycles of MP3 → FLAC → Vorbis → Opus → LC48 → HE48 → HEv2 execute 21
station changes. **19 pass; the first cycle's HE and HEv2 fail.** Actual output
is respectively 24 kHz stereo and 22.05 kHz mono, both with the AAC-core label.
The following two cycles produce full-rate HE/v2. WebSocket format/reconnect
and restoring playback after a software reboot pass.
[Report](../tests/results/esp32c3-conservative-20261001/switch/report.json),
[status samples](../tests/results/esp32c3-conservative-20261001/switch/status.json)
and [allocation log](../tests/results/esp32c3-conservative-20261001/switch/performance.json).

| First-cycle stage | Free heap | Largest block |
| --- | ---: | ---: |
| HE, before AAC core open | 128400 B | 94208 B |
| HE, after core open / failed 55128-byte SBR request | 75632 B | **47104 B** |
| HEv2, before AAC core open | 132056 B | 94208 B |
| HEv2, after core open / failed 55128-byte SBR request | 79340 B | **47104 B** |

In the successful later cycles, the largest block before core open is 106496 B
and after open 57344 B, allowing the unchanged SBR request. This is evidence of
a contiguous-block limitation; it does not identify the allocations that split
the heap. No growing leak is demonstrated: settled idle free heap ends each cycle
at 148080, 148640 and 148640 B, with largest blocks 94208, 114688 and 114688 B;
task count remains 17. Do not omit the first cycle or qualify the image using
only its later successes. There are two logged SBR allocation failures, with no
captured panic or heap-corruption marker in this switching run.

Reproduce the mixed-codec sequence with:

```powershell
python tools/esp32c3_tests/diagnostic.py run --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 --suite switch --suite websocket --cycles 3 `
  --case mp3-320 --case flac-level8 --case vorbis-q10 --case opus-510 `
  --case lc-48000-stereo --case he-48000-stereo --case hev2-44100-stereo `
  --sdkconfig firmware/development/esp32c3-iram-safe-wifi16/sdkconfig `
  --output .build/conservative-switch
```

## OTA executed by this image

The separate [repeatability run](../tests/results/esp32c3-conservative-20261001/ota-repeat/report.json)
passes all **15 checks**: eight malformed/unsupported requests, disconnect,
stall, two accepted slot changes, accepted upload during AAC playback, slow
upload and restoration of the saved station. All preservation checks compare
Wi-Fi, playlist and settings in RAM and save only equality booleans.

| Accepted upload | Destination slot | Upload through verified boot |
| --- | --- | ---: |
| Round trip, first leg | app1 | 20.469 s |
| Round trip, second leg | app0 | 21.031 s |
| While AAC is playing | app1 | 20.547 s |
| Paced upload, 80 ms per 4096 bytes | app0 | 37.671 s |

Each accepted upload verifies the exact app ELF hash and target slot. The
while-playing gate verifies the `audio` flag before upload; its short AAC
prelude is not a sustained-stream test. The serial capture records application
restarts with no panic, assertion, heap-corruption or interrupted-capture marker.
This covers the normal cache-disabled write path on the tested board. It does
not prove the cause of the previous Auto Suspend panic or certify power-cut
recovery, worst-case IRQ latency, sound continuity, or other Flash chips.

The filtered log also captures only 448/564 bytes of unused stack in the two
static WebUI workers during the negative tests. Do not shrink those stacks based
on their much larger unused margins in the ordinary AAC survey. No stack-overflow
marker was observed, but broader worst-path qualification remains necessary.

The exact orchestration source is retained beside the results, with its SHA-256
in `capture.json`. It runs the existing OTA suite and the shared audio server:

```powershell
python tests/results/esp32c3-conservative-20261001/ota-repeat/run.py `
  --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 `
  --firmware firmware/development/esp32c3-iram-safe-wifi16/app.bin `
  --output .build/conservative-ota-repeat
python tests/test-esp32c3-conservative-iram.py
```

## Decision and next step

Production defaults are unchanged. The test board remains on this awake image
in app0 after successful restoration of its saved settings/station; Auto Suspend
is disabled. The image is archived as **not qualified** because mixed-codec
HE/v2 switching fails even though all OTA checks pass.

Next, record which live heap blocks separate the large free areas before AAC
open and before SBR allocation, with minimal diagnostic RAM overhead. Existing
code inspection confirms that Stop closes the decoder and releases its reusable
PCM buffer; the recorded idle recovery does not demonstrate a persistent codec
leak. This inspection alone does not locate the allocations that prevent
coalescing. Do not keep changing allocation order without measuring that layout.

Remaining gates include reliable full-rate HE/v2 after other codecs, CPU/heap
under load, wider format/HTTPS coverage and the hardware checks in the
[testing guide](ESP32C3_TESTING.md).
