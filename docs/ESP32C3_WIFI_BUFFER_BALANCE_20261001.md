# ESP32-C3 Wi-Fi buffer balance after the IRAM audit

**Not qualified for production:** the matched Auto Suspend/six-buffer image
later panicked with `Illegal instruction` during an OTA write. Earlier passing
OTA/playback results do not override this failure. Keep the larger IRAM
relocation profile disabled until the crash is diagnosed and regression-tested.

## Scope

This follows the [IRAM placement audit](ESP32C3_IRAM_REDUCTION_20261001.md).
Its 23392-byte DRAM capacity gain allows testing a larger **dynamic** Wi-Fi
buffer limit while retaining the full native AAC decoder. Moving code must
preserve functionality; neither successful compilation nor a larger heap is
sufficient acceptance evidence.

The test board is ESP32-C3 rev. 0.4, XMC-D embedded Flash (`0x464016`), DIO
80 MHz, CPU 160 MHz, no PSRAM. Deep sleep is disabled. The experimental image
uses compact service stacks, supported SDK placement options and Flash Auto
Suspend. It retains all Flash APIs, full AAC/SBR/PS, rates and channels. No AAC
compression, PS relocation, early scratch allocation or unpacked cache is used.
Production defaults remain unchanged.

## Configuration and hypothesis

Compared with `esp32c3-iram-suspend`, `esp32c3-iram-wifi16` changes only the
dynamic RX and TX buffer limits from 6 to 16, including the SDK's two deprecated
aliases. Static RX buffers and the RX block-ack window remain 6. The
[ELF inventory](../tests/results/esp32c3-wifi16-20261001/inventory.json) records
identical static totals: reserved IRAM 25600 B, DRAM data 10723 B and BSS 31368 B.
The buffer-limit change itself releases **zero additional static RAM**.

Dynamic limits cap concurrent allocations; they do not permanently reserve
every buffer. Larger caps can improve throughput but raise peak heap demand.
In particular, dynamic RX buffers remain allocated until the upper stack has
consumed them. See Espressif's
[Wi-Fi performance guide](https://docs.espressif.com/projects/esp-idf/en/v6.0-rc1/esp32c3/api-guides/wifi-driver/wifi-performance-and-power-save.html)
and the locally tested ESP-IDF 6.0.2 `components/esp_wifi/Kconfig`.

The previous FLAC failure did not demonstrate an EOF state-machine defect:
the server had not finished transmitting the file. CPU was mostly idle while
the decoder waited for input. The following diagnostic separates host socket
behavior from the firmware profile; it does not measure actual Wi-Fi packet
drops or independently attribute the result to RX versus TX limits.

## Initial transport diagnostic

`tools/esp32c3_tests/transport.py` serves the same 1771852-byte, 11-second,
48 kHz stereo 16-bit FLAC fixture at 1.02 times its average bitrate. Only the
accepted host audio socket's `TCP_NODELAY` changes, in the order off/on/on/off.
The runner records the option's readback, sent bytes, completion, technical
status, CPU/heap windows and Wi-Fi power-save transitions. Private settings
are compared in RAM and never serialized.

| Installed profile | Trials | Complete transfers | Server duration | Playback / EOF |
| --- | ---: | ---: | --- | --- |
| Original bounded Wi-Fi 6, without new IRAM placement | 4 | 0/4; only 326656–424960 B sent | 17.0–19.4 s before termination | 4 FAIL |
| Auto Suspend with dynamic Wi-Fi 16 | 4 | 4/4; all 1771852 B | 10.797 s each | 4 PASS |

TCP_NODELAY did not resolve the six-buffer condition. The captured power-save
state was disabled while streaming. The original diagnostic also retained one
HTTP `URLError` and a failed restoration `TimeoutError`; do not relabel that
restoration as a pass. Later independent status/identity checks found the board
running its saved station. The candidate's restoration and settings equality
checks passed.

These first two profiles differ in both IRAM placement and dynamic limits.
The earlier audit also reproduced the FLAC failure with Auto Suspend and six
buffers. A matched comparison is required before isolating the buffer limits
from code placement; RF conditions are not controlled by these tests.

Raw results: [original profile](../tests/results/esp32c3-wifi16-20261001/bounded6-transport/report.json),
[candidate](../tests/results/esp32c3-wifi16-20261001/wifi16-transport/report.json).

## Mixed-codec and load results

The candidate [matrix](../tests/results/esp32c3-wifi16-20261001/matrix/report.json)
passes all 22 recorded cases: 14 finite-file checks, five network fault/recovery
or redirect/jitter cases, switching/heap, WebSocket reconnect and restoration.
All **21 station changes** pass, including full-rate HE-AAC and HE-AAC v2 after
the other codec families. Three settled idle checkpoints are 167884, 168236
and 168236 B free, each with a 114688-byte largest block and 17 tasks. There is
no declining idle-heap trend in these cycles. Maximum sampled HTTP latency is
266 ms. No captured allocation failure, decode failure or panic is reported.

The separate [40-second HTTP-load runs](../tests/results/esp32c3-wifi16-20261001/load/report.json)
pass five codec cases and fail two. Status requests are repeated with a 100 ms
pause after each response, giving approximately five requests per second.
Do not replace the two failed acceptance results with a successful playing flag.

| Input | Acceptance | Mean total / decode-task CPU | Peak total CPU | Minimum sampled free / largest heap |
| --- | --- | ---: | ---: | ---: |
| MP3 320 kbit/s, 48 kHz stereo | **FAIL: declining heap** | 63.167% / 30.067% | 64.4% | 100872 / 86016 B |
| FLAC level 8, about 1284 kbit/s, 48 kHz stereo, 16-bit | PASS | 71.900% / 23.467% | 73.2% | 89552 / 69632 B |
| Vorbis q10, about 507 kbit/s, 48 kHz stereo | PASS | 75.950% / 40.050% | 78.5% | 89236 / 73728 B |
| Opus 510 kbit/s, 48 kHz stereo | **FAIL: peak CPU above 85%** | 83.517% / 48.417% | 85.6% | 100096 / 81920 B |
| AAC-LC 48 kHz stereo | PASS | 48.533% / 19.217% | 49.3% | 99124 / 65536 B |
| HE-AAC 48 kHz stereo | PASS | 61.783% / 36.817% | 62.7% | 42716 / 10752 B |
| HE-AAC v2 44.1 kHz stereo | PASS | 66.533% / 41.600% | 67.3% | 43008 / 10752 B |

To include failed cases consistently, the table uses the independent diagnostic
window **5–35 seconds after the first PCM checkpoint**, reconstructed by
`summarize_load.py` from raw FreeRTOS counters. The acceptance runner uses its
own window after a ten-second warm-up; its exact metrics remain in the original
report. The summary never changes the original PASS/FAIL outcome. The five
passing cases have decoded-audio/wall-time ratios 1.0013–1.0016 and maximum
HTTP latency 110–141 ms. These are aggregate progress checks, not electrical
audio-underrun measurements.

MP3's sampled free heap falls from 118528 to about 100876 B and starts to
plateau near the end of the short test. A longer continuous connection and
post-stop idle comparison are needed to distinguish bounded buffer growth from
a continuing leak. Opus still produces real-time PCM in the retained raw
windows, but the CPU margin criterion fails; retain this speed/headroom work.
Minimum observed decoder and output-task stack headroom is 4896 and 1220 B.

## Matched buffer-limit control

After the load runs, application-only OTA changes `wifi16` back to the saved
`iram-suspend` image: both execute the same firmware code with the same IRAM
placement, profiler and native AAC options. Their sdkconfigs differ only in
dynamic RX/TX limits and aliases. Source commits differ only by the intervening
audit/tools/config-profile documentation, not linked application source.

The [matched six-buffer diagnostic](../tests/results/esp32c3-wifi16-20261001/matched6-transport/report.json)
again fails both socket modes: 388096 B in 17.640 s and 416768 B in 22.250 s,
both incomplete. The second case retains an HTTP `TimeoutError`. Settings
restoration passes. This strengthens the buffer-limit explanation without
isolating RX from TX or establishing a packet-loss mechanism.

The [OTA initiated from the 16-buffer image during AAC playback](../tests/results/esp32c3-wifi16-20261001/matched-to6-ota/report.json)
passes in 22.531 s including reboot, writes the other slot, verifies its exact
ELF hash and preserves Wi-Fi, playlist and settings. This exercises Flash
writes with the relocated Flash-driver/system code active. It does not prove
unchanged worst-case interrupt latency.

The reverse [six-to-sixteen OTA](../tests/results/esp32c3-wifi16-20261001/matched-back16-ota/report.json)
**fails after 91.828 s with `ConnectionResetError`**. Passive serial records
`Guru Meditation ... Illegal instruction`, followed by a new boot. The board
returns to the unchanged active `app1` identity of `iram-suspend`; the intended
16-buffer image is not activated. The filtered serial capture did not retain
the register dump/backtrace, so the exact instruction/cause is not established.
Do not assume Wi-Fi starvation alone caused the panic or that the 16-buffer
variant is immune: it shares the same relocation settings.

The planned return-to-16 transport repeat and longer MP3 pool-settling run were
therefore deferred in favor of restoring the original non-Auto-Suspend app.
`pool_settle.py` is retained as a planned diagnostic with host lifecycle tests;
it has not been executed on this physical candidate. It preserves failed
initial-window results, keeps one audio connection open across two observation
windows and compares settled idle heap after stopping.

## Recovery and remaining work

The original `esp32c3-aac-bounded-wifi-radio` application (without Auto Suspend)
was written through the ROM loader, bypassing the failed application's Flash
driver. The physical partition table was read first: active `app1` starts at
`0x1e0000` with size `0x1d0000`. Only its 1533536 application bytes were written;
esptool confirmed the data hash. Bootloader, partition table, OTA selection,
NVS and SPIFFS were not written. The expected original ELF identity is
`dd13414b890572c97dcbc825604ccecf8ce2ff9aaff68af34ae37af5b5f5ad77`.

The supplied C3 recovery skill issued a watchdog reset, but HTTP verification
timed out. A subsequent RTS reset also did not restore HTTP reachability.
Native USB remained enumerated; passive serial captures after those resets
were empty. The [initial recovery failure](../tests/results/esp32c3-wifi16-20261001/rom-recovery/recovery.json)
is retained, with the exact recovery script and esptool write-verification log.

**Startup was then verified after the user manually reset the board.** The
user reported a reset, not a complete power cycle. The
[final check](../tests/results/esp32c3-wifi16-20261001/rom-recovery/after-manual-reset.json)
confirms the original ELF hash above in `app1`, client-mode WebUI and saved
AAC 44.1 kHz stereo playback. Do not infer from this that a full power cycle
was necessary or that sticky Flash state caused the earlier failure.

The in-memory private-settings snapshot was lost when the recovery process
exited on its reset-verification failure, so no post-recovery byte-equality
claim is made. The recorded write bounds establish which partitions were
touched. Earlier successful OTA/transport steps separately verify settings
equality; the final check verifies actual startup and saved playback.

Next gates, in priority order:

1. **Done:** verify the original app's identity, client-mode WebUI and
   saved-station playback after the user's manual reset.
2. Retain Flash driver/system critical paths in IRAM while qualifying the
   smaller conservative relocation separately. Its 3584-byte static saving
   remains build-only evidence, not a proven full-HE memory solution.
3. Before retrying Auto Suspend, capture panic PC/register/backtrace evidence
   and isolate Flash chip suspend/resume and cache-off callers. A successful
   OTA on one occasion is insufficient; do not infer the cause from the USB
   or HTTP error alone.
4. Resume the 16-buffer control and MP3 settling diagnostic only on a justified
   test profile. Keep the initial MP3 failure and investigate Opus CPU margin.
5. Complete the format, transition, HTTPS, long-soak and hardware feature gates
   in the testing guide before changing production defaults.

Validate retained evidence and the unexecuted pool diagnostic's host lifecycle:

```powershell
python tests/test-esp32c3-wifi-balance.py
python tests/test-esp32c3-pool-settle.py
```

## Reproduce

Build with a fresh sdkconfig; existing saved values override defaults. Omit
`sdkconfig.aac-bounded-wifi.defaults`: the RAM profile already sets static RX=6
and dynamic RX/TX=16.

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-iram-wifi16 -Sdkconfig build-iram-wifi16/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults', `
    'sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults', `
    'sdkconfig.iram-safe.defaults','sdkconfig.iram-suspend.defaults')

python tools/esp32c3_tests/transport.py --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 --output .build/transport-result
```

The saved candidate is `firmware/development/esp32c3-iram-wifi16/`, with the
exact sdkconfig and image hashes. Application-only OTA preserves bootloader,
NVS and SPIFFS. Use `ota_transition.py` to verify the current image, exercise
an update initiated during AAC playback and verify the destination slot/hash.

Generate longer high-bitrate files for continuous CPU/heap/HTTP checks:

```powershell
python tools/audio_test_server/generate_stress.py `
  --output .build/audio-stress-60s --seconds 60
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP `
  --serial-port COM9 --suite load `
  --fixture-manifest .build/audio-stress-60s/manifest.json `
  --case stress-mp3-48000-2ch-16bit-60s `
  --case stress-flac-48000-2ch-16bit-60s `
  --case stress-vorbis-48000-2ch-16bit-60s `
  --case stress-opus-48000-2ch-16bit-60s `
  --case lc-48000-stereo --case he-48000-stereo --case hev2-44100-stereo `
  --sdkconfig firmware/development/esp32c3-iram-wifi16/sdkconfig `
  --output .build/load-result
```

The generator uses fixed-seed noise and independent stereo tones, explicitly
16-bit PCM, MP3 320 kbit/s, FLAC level 8, Vorbis q10 and Opus 510 kbit/s. It is
board-independent and contains no flashing/control commands. Keep generated
audio in ignored `.build/`; retain its hashes and encoder provenance.
This additional 16-bit FLAC transport fixture does **not** replace the existing,
unresolved 24-bit FLAC qualification failure.

The deferred pool-settling experiment can later use the same shared generator:

```powershell
python tools/audio_test_server/generate_stress.py `
  --output .build/audio-mp3-180s --seconds 180 --codec mp3
python tools/esp32c3_tests/pool_settle.py --board http://BOARD_IP `
  --host PC_LAN_IP --serial-port COM9 `
  --fixture-manifest .build/audio-mp3-180s/manifest.json `
  --case stress-mp3-48000-2ch-16bit-180s --output .build/pool-settle
```

Run this only after establishing a suitable firmware profile; the retained
180-second fixture manifest is preparation evidence, not a physical test pass.

Load acceptance checks actual decoded audio/wall-time progress, CPU windows,
heap and largest-block margins, status correctness and HTTP latency. A playing
flag alone cannot establish continuous audio. External audio/IRQ timing, long
soaks, HTTPS, AP/OLED/controls and deep-sleep regressions remain separate gates.
