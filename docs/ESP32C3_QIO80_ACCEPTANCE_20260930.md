# ESP32-C3 full-radio QIO 80 MHz acceptance — 30 September 2026

## Decision

**Keep DIO 80 MHz as the production default.** The full-radio acceptance gate
is not green. QIO is functional on this board, but these runs do not establish
that all radio functions remain as reliable as the DIO baseline. This is a
decision to defer promotion, not a finding that Quad causes the observed
network failures.

The separate [flash experiment](ESP32C3_FLASH_QUAD_20260930.md) passed actual
SPI0 mode/clock assertions, repeated image reads and standalone AAC decoding
at QIO 80 MHz. Its 10–15% reduction in decoder work remains valid for that
isolated workload. It does not certify Wi-Fi, OTA or total radio CPU usage.

## Images and method

These results describe the images **before** the subsequent EOF status
correction. Later results for that correction
must not be substituted for failed cases in this record.

The physical board is the same ESP32-C3 SuperMini OLED revision 0.4, with
embedded XMC 4 MiB flash (`0x464016`), CPU 160 MHz and no PSRAM. All full-radio
images used internal RTC timing and **disabled deep sleep**. ESP-IDF is v6.0.2;
both Wi-Fi IRAM speed options remain disabled, as in the current production
RAM policy. No AAC formats or rates were disabled to obtain a pass.

| Image | Purpose | App bytes | ELF SHA-256 |
| --- | --- | ---: | --- |
| `esp32c3-oled-native-production` | Existing quiet DIO baseline | 1,392,688 | `b0f5c3a1e55bc3b309f6f56f197b7d40bf0d3b4c1c1196de9b2c8288b72832f3` |
| `esp32c3-oled-native-qio80-candidate` | Quiet QIO candidate | 1,392,688 | `6e18d7e6c1ce989c50fdd9e17a197e91dc47a4c193f18819162cbb762ee3f251` |
| `esp32c3-oled-native-dio80-profile` | Fresh DIO CPU/heap control | 1,539,952 | `d556e2d950c0f9dfb575d9a62082b6765882190ec469c1077c1542bc9d5e5d5e` |
| `esp32c3-oled-native-qio80-profile` | QIO CPU/heap candidate | 1,539,952 | `3ec5716866f9d77087289c3dc59772194c21fa357a8e599830b0e77e430434f6` |

The three new images were built from `6c3da5e9`; their binaries, matching
bootloaders, exact sdkconfigs and manifests are in `firmware/development/`.
The two profiling configurations differ only in their DIO/QIO choice and
compatibility aliases. The old quiet DIO image predates the new candidates;
the newly built profiling control provides the matched-source comparison.

The matching second-stage bootloader was installed for each bus mode. An
app-only OTA update cannot switch an old DIO bootloader to QIO. ESP-IDF's DIO
image header is intentional even for a QIO build; see the flash report.

The tests use the existing [acceptance procedures](ESP32C3_TESTING.md).
Thresholds were not relaxed: HTTP <2 seconds, peak CPU ≤85%, real-time PCM
progress, bounded heap loss and correct full decoded format. A failed test is
retained even if another run of that test passes. One test-runner correction
now saves partial REST observations on a transport exception; it preserves
failure status and stores no private exception text (`716f7964`).

## Network comparison limits

Recorded RSSI medians were −84 dBm in the first QIO load run, −77 dBm in the
matched DIO run, and −86 dBm in the repeated QIO run. No causal link between
RSSI and flash mode was established. These were sequential runs, not controlled
RF measurements. The first run also overlapped host builds/tests; the QIO
repeat was performed after those had finished. Neither the initial nor repeated
QIO load run passed the complete matrix.
The final DIO repeat had a −74 dBm RSSI median and again passed AAC-LC, Vorbis
and Opus. That repeat still did not pass the entire matrix, and the different
RF observations prevent attributing transport timeouts to the bus interface.

## Results

The [retained reports](../tests/results/esp32c3-qio80-acceptance-20260930/)
contain each case, exact image identity, fixture hashes, test-source hashes,
observations and failure reasons. `summary.json` counts full cases, including
restoration; decoding a file successfully is not a full case pass if EOF fails.

### Quiet production candidate

- HTTP: all sixteen non-HE cases (eight fixtures, AUTO and explicit codec)
  reached the expected decoded format, then failed EOF status. All six HE/v2
  cases failed full-rate format validation. The old DIO report had fifteen EOF
  failures out of those sixteen non-HE cases; one FLAC AUTO attempt passed.
- Stop/Play generation replacement, recovery from a stall and HTTP 503, and
  WebSocket format/reconnection passed. Both HE transitions failed. Redirect
  and jitter failed at EOF. The corrected 20-second truncated-body test still
  failed to observe stopped state; its older seven-second result is not used
  as proof here.
- Trusted HTTPS: 22 cases BLOCKED because no trusted fixture origin was
  available. The separate untrusted-TLS test did not observe the required
  certificate-rejection alert, so rejection is unverified, not proven insecure.
- OTA: **15/15 checks passed**, including ten negatives/interruption cases,
  both app slots, active playback, slow upload and final restoration. Each
  successful boot matched the exact uploaded ELF; Wi-Fi, playlist and exposed
  settings compared equal in memory.
- Boot: **30/30 attempts passed in each mode**. Median reboot-to-WebUI was
  **5.586 s DIO / 5.711 s QIO**; maximum/p99 with this sample count was
  **12.093 s / 6.328 s**. The preselected 1.25× p99 / 30-second absolute gate
  passed. These are sequential network-dependent measurements, not pure Wi-Fi
  association or flash throughput timings.

### CPU and memory under HTTP load

| Fixture | QIO first run | Matched DIO | QIO repeat |
| --- | --- | --- | --- |
| AAC-LC 48 kHz stereo | HTTP >2 s | Timeout | PASS |
| HE-AAC 48 kHz stereo | Wrong decoded format | Request error | Wrong decoded format |
| HE-AAC v2 44.1 kHz stereo | Wrong decoded format | Wrong decoded format | Wrong decoded format |
| MP3 48 kHz stereo | Request error | Progressive heap loss | HTTP >2 s |
| FLAC 48 kHz stereo | Insufficient playback | Insufficient playback | Request error |
| Vorbis 48 kHz stereo | Request error | PASS | Timeout |
| Opus 48 kHz stereo | Progressive heap loss | PASS | Timeout |

The final DIO repeat passed AAC-LC, Vorbis and Opus (mean CPU 43.80%, 45.18%
and 68.53%); HE/v2 again failed full-rate validation, MP3 failed the heap-loss
budget and the long FLAC fixture lacked sufficient playback. Both repeats and
all initial attempts are retained.

The passing QIO AAC-LC repeat measured **33.92% mean / 34.7% peak total CPU**,
32,308 bytes minimum free heap, 14,848-byte minimum largest block, PCM/wall
ratio 0.9978 and 1,532 ms maximum HTTP latency over 40 seconds. This is one
passing case, not a passing all-codec benchmark.

The DIO Vorbis and Opus cases measured mean CPU 44.97% and 68.22% respectively.
They cannot be compared as passing A/B speed results against QIO cases that
failed acceptance. No new emulator correction factor is derived from them.

Full-radio HE-AAC still fails its 55,128-byte SBR allocation and decodes only
the AAC core. This is a known [memory limitation](ESP32C3_AAC_MEMORY_20260930.md),
also present in DIO; it is never counted as successful HE-AAC. The generated
long FLAC fixture also failed with a decoder error in both profiling modes.

### Switching and long playback

The requested three-cycle codec switch test aborted on a transport error.
The one-hour AAC-LC, HE-AAC and HE-AAC v2 soak attempts also aborted on network
errors before completing their durations. They are **failed attempts**, not
one-hour passes; settled heap recovery across three cycles is unverified.
The subsequent stop command failed too, and the board was recovered through
the native USB reset procedure before installing the quiet candidate.

The separate QIO memory survey passed AAC-LC playback and captured the required
allocation/stack evidence. HE and HEv2 failed full-rate validation. Survey
evidence and restoration passed; the survey does not replace a passing soak.

### Host verification

- 42 Python checks passed initially; after the partial-observation fix the
  acceptance suite passed all 15 checks (one more than the initial suite).
- 151 ESP32-C3 and shared WebUI Node tests passed.
- Native C/C++ tests passed for stream formats/Helix transitions/AAC framing,
  the deep-sleep clock, 16 RTC pin configurations, OTA streaming and OTA HTTP.
  Host clock tests do not qualify physical QIO deep-sleep wake-up.
- Four firmware archive checks passed after removing an obsolete hard-coded
  source revision from the manifest test (`c4eb5f33`). It now checks the actual
  embedded app version, size and hash.
- A broader repository Node run had 1,111 passes, 39 failures and 22 skips
  out of 1,172 tests. Most failures concern ESP8266 historical build/evidence
  files, missing tools, line endings or host timeouts. The stale C3 archive
  assertion was corrected separately. This broad run is not an all-green
  repository result and is not evidence of a C3 Quad regression.

## Coverage boundaries

After this comparison, the original DIO bootloader, both app slots and OTA
selector were restored. A full 4 MiB readback matched the private pre-test
backup byte for byte, including NVS and SPIFFS. The original production ELF
and HTTP service were verified; Wi-Fi, playlist and exposed settings compared
equal. `restoration.json` records this checkpoint before subsequent EOF-fix
testing. Private backups and credential values are not included in the archive.

Trusted HTTPS needs the documented trusted test origin; none was available.
Browser automation failed to initialize because of a Windows sandbox helper
error. REST/WebSocket or OTA protocol checks do not replace visual browser,
OLED or acoustic inspection. External interrupt timing, physical power cuts,
cold power cycles, deep-sleep wake-up, voltage and temperature margins were
not tested. No external 32.768 kHz crystal is installed on this board.

Before promoting QIO, repeat the failed network-dependent comparisons under
stable conditions, complete switching/soak tests, and resolve or explicitly
scope existing format/EOF defects. Keep the production default and the
existing DIO-based QEMU calibration unchanged until the applicable gate passes.
