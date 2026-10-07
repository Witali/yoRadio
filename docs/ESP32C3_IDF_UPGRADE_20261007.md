# ESP32-C3 sequential ESP-IDF upgrade

## Scope and sequence

All upgrade work remains on `codex/esp32c3-idf-upgrade` in the dedicated
`.worktree/esp32c3-idf-upgrade` checkout. Do not merge the upgrade into `main`
without a subsequent user request.

Starting point: main `ff490cd4`, installed production image built from
`a06181cf` with ESP-IDF 6.0.2. Keep the saved image under
`firmware/development/esp32c3-main-production-20261007` available for rollback.

1. Record physical 6.0.2 format, EOF, transition, fault and WebUI controls.
2. Install 6.0.3 beside 6.0.2; build and test before advancing the SDK pin.
3. Install 6.1 separately; apply required API migrations and repeat the tests.
4. Save both sets of outcomes, binary/configuration hashes and comparisons;
   retain failures and distinguish regressions from failures present on 6.0.2.
5. Leave the board on a verified production image and preserve its Wi-Fi,
   playlist and settings. Do not overwrite an existing versioned release.

`idf/esp32c3-oled-native/idf-version.txt` is the SDK pin used by setup, build
and the dependent QEMU/benchmark tools. Each SDK has its own checkout,
tool directory and build directories. The audio-codec archive stays pinned
to the same revision so the SDK comparison does not also change the decoder.

## Validation matrix for each SDK

- Clean production and profiling builds; compile deep-sleep and external-32k
  variants. The connected board has no external crystal, so the crystal
  variant receives a build check only.
- C3/shared Node regressions, Python evidence/parser/ABI tests, ASan/UBSan
  stream-format, decoder ownership and EOF tests; SDK-specific lwIP checks.
- QEMU decoder PCM, retry and allocation-failure checks using the target SDK.
- Physical MP3, AAC-LC, HE-AAC, HE-AACv2, FLAC, Vorbis and Opus file matrix,
  explicit/AUTO selection, natural EOF, format transitions and Stop/Play.
- WebSocket reconnect/format consistency, reboot, network faults, configured
  availability timeout and settings persistence.
- OTA upgrade and repeatability, invalid-image rejection, interruption and
  slow upload; verify the running image and preserved settings/files.
- CPU/heap under HTTP load, codec switching, HTTP/HTTPS station playback and
  ten-minute sustained playback. CPU usage is recorded without an 85% limit.
- Production-image OTA and saved-station playback at the end of each stage.

Automated status/PCM/DMA evidence does not replace listening or a visual OLED
check. Manual observations and unavailable test prerequisites are reported
separately. Historical experiment evidence replay is not a new hardware run.
Physical SDK transitions use application-only OTA with the board's existing
bootloader, NVS and SPIFFS. Each clean build also produces its SDK's bootloader;
the QEMU tests use that corresponding bootloader. These checks do not claim
a physical full-flash/bootloader migration.

## Migration references

- [ESP-IDF 6.0.3 release notes](https://github.com/espressif/esp-idf/releases/tag/v6.0.3):
  HTTP-server Content-Length handling changed. The checked-out C3 parser
  rejects values above `UINT32_MAX` with HTTP 413 before conversion to 32 bits.
- [ESP-IDF 6.1 release notes](https://github.com/espressif/esp-idf/releases/tag/v6.1).
- [6.1 migration guide for ESP32-C3](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/migration-guides/release-6.x/6.1/index.html).

## Execution status

The original-default 6.0.3 sequence and matched 6.0.2 controls are complete,
with the failures detailed below. Original-default 6.1 builds and host/QEMU
tests also completed. The user then requested enabling the complete compact
HE-AAC configuration by default. New 6.1 compact builds and qualification
are in progress; saved original-default images remain separate controls.
A planned check is not a passed check.

### Controls and completed 6.0.3 checks

The physical 6.0.2 control has 48 passes and eight failures. The failures are
the six HE-AAC/HE-AACv2 AUTO/explicit full-format checks and two full-rate
transition checks. All 22 natural-EOF checks pass, including HE-AAC. Keep this
distinction: successful EOF does not qualify full-rate HE-AAC playback.

Production, profiling, deep-sleep and deep-sleep + RTC32k images built and are
saved under `firmware/development/esp32c3-idf-6.0.3-*`, with exact configurations
and image/ELF hashes. The awake profiling image was tested first, then OTA
successfully installed the quiet production image while AAC-LC was playing.
The external-crystal build cannot be tested on the connected crystal-free board.

| Check | 6.0.3 result |
| --- | --- |
| C3/shared Node tests | 243 passed, no skips |
| Python tests after historical-source repairs | 653 cases across 117 scripts; 114 scripts pass, three archival fingerprint failures, no remaining skips |
| Stream format / EOF / decoder ownership | Native ASan/UBSan checks and 17 custom-decoder terminal cases passed |
| FLAC bounds and prediction | Sanitizers passed; complete-file PCM matches FFmpeg |
| FLAC depth/stereo/predictor matrix | 120 fixtures × three core/adapter configurations passed; allocation-failure cleanup/reopen passed |
| Vorbis output in QEMU | Seven buffer/retry/EOF cases passed; ample-buffer PCM identical to the retained 6.0.2 raw-packet reference |
| Vorbis lifetime in QEMU | 210 cases passed, including 100 decode/close cycles and individual allocation failures |
| AAC in QEMU | Format/transition checks, guards, instruction-counter checks and calibration-window counts passed |
| Production static memory versus 6.0.2 | IRAM unchanged at 53,760 B; data +8 B, BSS +48 B; linker heap start +64 B including alignment |
| Production image size versus 6.0.2 | +1,632 B, total 1,402,640 B |

The AAC calibration gate compares frame counts, consumed input and PCM byte
counts with recorded hardware windows. It does not compare every PCM sample
or establish acoustic continuity. QEMU results do not establish the board's
Wi-Fi/decoder memory behavior.

The three remaining Python failures are missing historical source snapshots
for old IRAM/Wi-Fi experiments. Expected hashes and numerical gates were not
relaxed. See `tests/fixtures/historical_sources/README.md` for the absent hashes.
Their failures remain in the report; these are not new firmware measurements.

The first installation attempt ended with Windows connection error 10053;
the board remained on its original 6.0.2 hash. The attempt did not record its
failure phase, so it cannot establish whether upload had begun. A retry after
stopping playback installed the profiling image in 20.25 seconds and verified
unchanged Wi-Fi, playlist and exposed settings. Keep the failed attempt too.

### 6.0.3 hardware results so far

The first matrix completed with 49 passes and nine failures: the same eight
HE-AAC format/transition failures as the 6.0.2 control, plus a rejected test
invocation specifying two switching cycles where at least three are required.
The matrix also passed untrusted-TLS rejection, WebSocket reconnect and two
reboots. The separate three-cycle switching attempt later timed out after the
Opus observation, before completing its first cycle; restore/reboot passed.
A repeated switching run subsequently completed all 33 changes without a
transport timeout. Its nine failures were exactly the three HE-AAC fixtures
in each of the three cycles. Settled heap medians after each cycle were
120,148/120,692/120,692 B, largest block 69,632 B, and 17 tasks throughout.
The suite remains failed on formats; its later heap acceptance function is
not reached when format failures exist. The matched 6.0.2 run also completed
33 changes, with exactly the same nine HE-AAC format failures and no transport
timeout. Its settled heap medians were 121,152/121,196/121,196 B, largest
block 69,632 B, and 17 tasks throughout. The original 6.0.3 timeout remains
recorded as an intermittent failure; it was not reproduced by the repeat.

The 60-second controlled load runs used identical fixed fixtures and concurrent
WebUI requests. CPU has no acceptance ceiling. These descriptive metrics exclude
the first ten seconds and do not override the original failures:

| Codec | Mean CPU | Minimum free heap | Audio/wall duration | Load gate |
| --- | ---: | ---: | ---: | --- |
| MP3 | 57.6% | 53,296 B | 1.0018 | Progressive heap loss |
| Custom FLAC | 60.6% | 45,452 B | 1.0016 | Pass |
| Vorbis | 69.7% | 39,868 B | 1.0016 | Progressive heap loss |
| Opus | 77.7% | 50,856 B | 1.0018 | Progressive heap loss |
| AAC-LC | 43.5% | 42,560 B | 1.0016 | Progressive heap loss |

Both HE-AAC load inputs failed full-format acceptance; their core-fallback CPU
measurements must not be presented as full HE-AAC decoding performance. All
seven post-Stop heap-recovery checks passed. A matching 6.0.2 profiling build
was then installed and tested with the same five non-HE fixtures, order and
HTTP polling interval. All five acceptance results matched 6.0.3, and all five
post-Stop recovery checks passed. The four continuous-playback heap failures
therefore predate the SDK update.

| Codec | Mean CPU, 6.0.2 / 6.0.3 | Minimum heap, 6.0.2 / 6.0.3 | Acceptance in both |
| --- | ---: | ---: | --- |
| MP3 | 57.77% / 57.61% | 52,556 / 53,296 B | Progressive heap loss |
| Custom FLAC | 60.50% / 60.60% | 41,732 / 45,452 B | Pass |
| Vorbis | 70.36% / 69.72% | 41,512 / 39,868 B | Progressive heap loss |
| Opus | 77.64% / 77.66% | 48,868 / 50,856 B | Progressive heap loss |
| AAC-LC | 44.09% / 43.45% | 47,648 / 42,560 B | Progressive heap loss |

Audio/wall duration ratios were 1.0016–1.0018 in both runs. CPU differences
were at most 0.64 percentage points. These are single sequential Wi-Fi runs,
not randomized timing trials; heap minima also depend on network allocation
state. The table does not turn a failed memory gate into a pass.

All truncated-FLAC checks passed, including natural cleanup and subsequent
AAC/FLAC playback. The station-availability suite passed configured 3/10-second
deadlines, stalled-stream termination, Stop/switch/cancellation, invalid-value
rejection and settings persistence. HE-AACv2 recovery failed full-format
acceptance. The runtime gate also recorded failed allocations: 55,128 B during
HE-AAC, and 1,700-byte requests with less than 5 KiB free after a planned reboot.
Those failures remain part of the result.

The public-stream profiling checks passed Groove Salad 128 kbit/s AAC and
256 kbit/s MP3 over HTTP. The 64/32/16 kbit/s AAC cases failed runtime gates.
Over HTTPS, MP3 passed; the 128/64/32 kbit/s AAC cases failed runtime gates
and the 16 kbit/s case timed out. Allocation diagnostics include failed
1,700-byte requests with a largest free block below 1,700 bytes. These are
profiling-image results; a separate quiet-production status/format check is
planned and will not be treated as a CPU, heap or acoustic-continuity test.

The 600-second AAC-LC test had 557 successful status observations, a maximum
HTTP response time of 406 ms and an audio/wall duration ratio of 1.0016.
Mean CPU was 35.3%, peak 37.6%; no allocation/decoder/panic diagnostic appeared
in the captured playback window. The original test nevertheless **failed**
the progressive-heap-loss gate: the first/last three-sample heap medians were
50,548/35,240 B. Minimum heap was 32,916 B. The final 291-second subwindow
passed the same gate (36,984/35,240 B), suggesting the decline had mostly
settled; this does not erase the full-window failure or establish its cause.
Minimum observed RSSI was -78 dBm. Restore/reboot passed.

The profile-to-production OTA transition passed while the controlled AAC
stream was playing. The new image hash and slot were verified, along with
unchanged Wi-Fi, playlist and exposed settings.
All 14 subsequent OTA cases passed: invalid-image/request rejection,
disconnect/stall handling, two same-image slot transitions, slow upload and
restoration with settings verification.

The quiet-production HTTP/transition/WebSocket/boot matrix completed with
21 passes and the same eight HE-AAC format/transition failures as 6.0.2.
Two oversized `Content-Length` probes returned 413; negative and conflicting
duplicate lengths returned 400. A non-numeric probe ended with a connection
reset whose phase was not retained, so that original run remains failed.
The header-test client was corrected to stop after the complete response
header, avoiding an unnecessary error-page read; a reset before receiving
the header still fails. Three local transport tests pass. The physical 6.0.3
recheck passed all five rejection cases and restoration/settings verification.

The quiet-production HTTPS check passed AAC-LC 128 kbit/s and MP3 256 kbit/s.
The 64/32 kbit/s HE-AAC sources were independently probed as 44.1 kHz stereo,
but the board produced 22.05 kHz stereo PCM. The 16 kbit/s HE-AACv2 source
was 32 kHz stereo; observed PCM was 16 kHz mono before a timeout. These are
actual output-format differences, not merely a station-name/display mismatch.
Restoration and settings checks passed. This quiet-image test does not
provide profiling counters or qualify heap/CPU/acoustic continuity.

### Why these HE-AAC failures coexist with earlier fixes

The [main integration](ESP32C3_MAIN_INTEGRATION_20261007.md) includes the AAC
repairs but leaves compact SBR, high-history, scoped low-QMF and asymmetric
storage opt-in. The SDK comparison deliberately retains those main defaults:
`CONFIG_YORADIO_AAC_PLUS=y`, but `CONFIG_YORADIO_AAC_COMPACT_SBR` is off.
Profiling captures failed original 55,128-byte SBR allocations. The vendor
path can return core-only PCM when SBR storage cannot be allocated.

Earlier full-rate HE-AAC results, including the ten-minute HE-AACv2 run,
belong to different experimental configurations. Their implementation and
evidence are retained; successful decoder/PCM work was not undone by the SDK
upgrade. This migration's default-build failures must not be generalized to
all compact variants, or presented as a new 22 kHz limit. Compact AAC is not
silently enabled during those original-default SDK comparisons. The user's
subsequent explicit request now selects the complete PC19/asymmetric/late-SBR
chain for fresh board builds. New measurements are labelled `6.1-compact`;
their changes must not be attributed solely to the SDK version.

### 6.0.3 lwIP source audit

The first clean build correctly rejected the changed `api_msg.c` hash.
Compared with 6.0.2, this file only changes DNS result-count handling;
close/shutdown paths and `tcp.c` are unchanged. Added its exact normalized
source hash to the allowlist, retaining rejection of all unaudited sources.
SDK submodule revision: `c6f2f878e7b0f86033214b85547d579be43351e3`.

The actual 6.0.3 stack passed all six half-close scenarios with ASan/UBSan
for both heap and pool allocation after our fix (12 passes). Both unpatched
controls still fail the five ownership cases and pass the ordinary full-close
case. This demonstrates that the local fix is still needed on 6.0.3.

### Preparation for 6.1

The SDK was downloaded separately while the board continued its 6.0.3 tests.
SDK revision: `fff9895c82d744c7237be8847347bdd1b07c6643`. GCC remains
15.2.0 (`esp-15.2.0_20251204`); the codec archive is unchanged. The project
pin and installed firmware remain at 6.0.3 during this preparation.

A copied build helper with an explicit `v6.1` SDK path prepares separate 6.1
build directories without changing that pin or the board. Its source is
retained with the test evidence. The first quiet-production build succeeds
without application API edits: 1,418,832 B (+16,192 B versus 6.0.3).
Its linker heap capacity is 2,016 B lower; IRAM grows by 1,024 B,
DRAM data by 228 B and BSS by 776 B. These are static linker measurements,
not observed runtime free heap. Physical installation remains deferred until
the 6.0.3/control sequence finishes.

Application feature flags, Wi-Fi IRAM placement and the selected DIO/80 MHz
flash mode match 6.0.3. The only additional flag in that configuration subset
is `CONFIG_ESPTOOLPY_FLASHMODE_VAL=3`: 6.1 adds a one-based flash-mode value
to the application descriptor, where 3 denotes DIO. It does not select DOUT
or change the image-header flash-mode encoding.

The actual 6.1 `tcp.c` and `api_msg.c` are identical to 6.0.3, with the same
lwIP submodule revision. The existing strict source fingerprints therefore
accept them without extending the allowlist. The application already uses
the public `esp_rom_gpio_*` API, and its deep-sleep hold calls remain in the
6.1 public GPIO header. Compilation and runtime qualification are still
required; a source inspection alone is not migration acceptance.

All six actual-SDK lwIP ownership cases passed with ASan/UBSan for both heap
and pool allocation (12 passes). Both unpatched controls reproduced the five
ownership failures and passed the ordinary full-close case. The local TCP
fix remains necessary for 6.1.

The 6.1 preparation repeats passed all 243 Node cases. The Python run covers
118 scripts/654 cases, with the same three missing historical-source failures
and no skips. The subsequent HTTP-header client repair adds two passing local
cases; original reports are retained separately. Vorbis raw-packet PCM in
6.1 QEMU matches 6.0.3 byte for byte, and all seven output/retry cases pass.
All 210 Vorbis lifecycle cases pass, including the 100-cycle baseline and
209 handled fault cases. AAC format/guard/calibration checks pass, as do
the MP3/FLAC/Vorbis/Opus archive calibration runs. As with 6.0.3, the AAC and
archive calibration markers qualify byte counts and formats, not every PCM
sample or physical DMA continuity.
