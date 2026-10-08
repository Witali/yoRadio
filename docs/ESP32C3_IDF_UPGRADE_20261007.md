# ESP32-C3 sequential ESP-IDF upgrade

## Scope and sequence

**Priority updated on 2026-10-08:** adapt and qualify the latest revision of
the official `release/v6.1` branch. Its checked head is
`9a97f6c54ec638111ce55cd36581b3c192f15207` (commit date 2026-09-22), newer than
the published `v6.1` tag `fff9895c82d744c7237be8847347bdd1b07c6643`.
The former SDK comparisons below remain historical controls. Further work
targets this exact revision instead of repeating the 6.0.3 upgrade sequence.

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

`idf/esp32c3-oled-native/idf-version.txt` selects the toolchain series, and
`idf-revision.txt` pins the full SDK commit. Setup places each revision in a
separate checkout; build verifies HEAD before using it. Tool installations
are shared within the series, with versions selected by the pinned SDK.
Each test image has its own build directory. The audio-codec archive stays pinned
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

### Latest revision adaptation on 2026-10-08

The SDK source and tools for `9a97f6c54ec6` are installed separately from the
release-tag checkout. The actual revised HTTP/TLS reader passes 85 ASan/UBSan
cases. The lwIP TCP and netconn sources still match the audited ownership fix;
all six host cases pass with each of the pool and heap allocators. The updated HTTP server already has
the same Content-Length overflow guard as 6.0.3. The build adapter recognizes
this reviewed revision and preserves the upstream source without rewriting it.
The full profiling build and linked AAC/TLS audits pass. The saved application
is `firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-dynamic/app.bin`;
its ELF identity is `e51ff9fd08123d5aa5da09441818777eb6c04eca99c0279dfd396d1e88247e75`.
It has the full PC19 configuration and a 32,744-byte SBR owner. This explicitly
labelled laboratory image adds the test CA to normal roots. Physical acceptance
of this revision remains open.

### Earlier release tag qualification

The original-default 6.0.3 sequence and matched 6.0.2 controls are complete,
with the failures detailed below. Original-default 6.1 builds and host/QEMU
tests also completed. The user then requested enabling the complete compact
HE-AAC configuration by default. The compact code passes fresh PCM/ownership
checks; the first physical profile exposed a fragmented-heap allocation failure.
The corrected system RAM profile passes the isolated full-rate HE/HEv2 matrix,
and all four firmware variants are built. The physical sequence is complete,
including a local backport of the HTTP length guard absent from the pinned 6.1
source. Compact AAC is enabled in fresh board defaults on this branch, and the
guarded awake production image is installed. Full release acceptance is **not
met**: sustained heap/allocation failures and public HE HTTPS failures remain.
Saved original-default images and every failed run remain separate controls.

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

### 6.1 compact defaults

At the user's request, `362667c9` enables the complete PC19 compact-storage
chain in fresh board configurations: compact SBR tables, high-QMF history,
PC19 side metadata, smoothing history, scoped low-QMF workspace, asymmetric
owner and late-SBR handling. AAC Plus remains enabled, including full-rate
SBR and PS stereo. No new sample-rate limit or arithmetic change is introduced.
Existing saved sdkconfigs retain their choices; use a fresh sdkconfig to adopt
the defaults. The new `sdkconfig.aac-native.defaults` overlay provides an
uncompacted AAC Plus control when applied after the board defaults.

Both awake images pass the actual ELF type, linked-call and patch-provenance
checks. The requested SBR owner decreases from 55,128 to 32,744 B: 22,384 B
(40.6%). The adapter is 204 B, including the 160-byte high-history runtime;
its 144-byte PC19 metadata must not be counted twice. These are allocation
sizes, not a claim that all runtime free heap increases by exactly that amount.
The decoder stack remains 16 KiB.

Against the stock 6.1 production image, IRAM (54,784 B), static DRAM data
(12,396 B), BSS (31,536 B) and linker heap capacity are unchanged. The compact
application is 1,439,024 B, an increase of 20,192 B in flash. The new physical
measurements use the `6.1-compact` label because both SDK and AAC configuration
differ from the 6.0.3 stock control.

#### PCM and ownership regression

The new 6.1 QEMU capture is byte-identical to the retained passing PC19 output
across all 865,280 transition/gap channel samples. Comparison with the retained
full-precision native-storage reference gives:

| Corpus | Channel samples | Changed samples | Maximum absolute error | RMS error |
| --- | ---: | ---: | ---: | ---: |
| LC to HEv2, absent/resumed SBR transition | 189,440 | 74 | 2 LSB | 0.02309 LSB |
| Four SBR-gap cases | 675,840 | 834 | 2 LSB | 0.04208 LSB |

There is no alignment, gain correction, resampling or discarded startup.
Both remain below the requested 3-LSB acceptance limit. This is a pinned
synthetic corpus, not a proof for every possible input or a physical PCM capture.
The previous five-recording results remain separate historical evidence.
The same run passes native metadata, PC19 side-metadata lifecycle, pointer
boundaries, late-SBR parity/retention, concurrent decoders, reset/cleanup,
four allocation-failure recoveries, four malformed-input recoveries and
69,376 valid FIL-parser comparisons.
The pointer audit executes 1,186,037 checks, with all 696 allocations matched
by frees. Minimum sampled decoder stack margin is 2,824 B in this QEMU run.
The ordinary-stream controller regression compares another 887,808 channel
samples exactly against the unchanged controller using the same storage.

All four physical variants build and are saved under
`firmware/development/esp32c3-idf-6.1-compact-{production,profile,deep-sleep,rtc32k}`.
Sleep and crystal variants receive compilation checks only in this stage.
The fresh native-control configuration check confirms that its overlay disables
all seven compact/late-SBR flags while leaving AAC Plus enabled.

The compact-default Python repeat covers 118 scripts/656 cases: 115 scripts
pass, with the same three missing historical-source failures and no skips.
The additional two cases since the earlier full run are the already documented
HTTP-header client tests. No new host-test failures were introduced.

The first physical installation through native application-only OTA passed
in 20.734 seconds. The running profile ELF hash is
`5c63accef7c56a648633589e9d23fe45f39b46199960dad2c7291a97a2042ac8`.
In-memory comparisons confirmed unchanged Wi-Fi, playlist and settings.
Physical regression and sustained-load results are recorded below as they finish.

#### Initial physical failure and RAM-profile follow-up

The first `6.1-compact` profile retains the original board's system RAM
settings. All six HE/HEv2 finite-file format checks fail with insufficient
playing samples; captured status is `decode failed`. The two AAC transition
checks also fail. This is a physical playback failure despite the passing
isolated QEMU PCM/ownership tests, and it prevents sustained qualification of
that initial profile. The complete original run is retained: 43 passes and
14 failures (six format checks, two transitions, six HE/HEv2 EOF checks).
Other-codec/LC EOF, network fault handling, WebSocket reconnect, untrusted TLS
rejection, both boot checks and restoration pass.

Passive serial evidence identifies the cause: the 32,744-byte SBR request
fails with 48,296 B free but a largest block of only 26,624 B. Subsequent
attempts reproduce the same largest-block limit and return decoder error -2
(memory lack). Total free heap alone is insufficient for this allocation.

The earlier passing PC19 network image also used smaller service stacks,
6 static Wi-Fi RX buffers, 16 dynamic RX/TX buffers and a flash-resident heap
allocator. Those system choices were absent from the initial compact defaults.
A separate `6.1-compact-ram-profile` experiment applies the existing
`sdkconfig.aac-reserve-ram.defaults` overlay: 8,192 B fewer requested service
stack bytes and the 6/16/16 Wi-Fi buffer counts. It keeps the 16 KiB decoder
stack, full TLS record sizes and allocator placement unchanged. This isolates
whether the smaller system footprint suffices; its results must pass before
these additional settings are promoted.

The isolated RAM-profile check passes all ten cases: the three full-rate
HE/HEv2 fixtures with AUTO and explicit AAC, both transition sequences,
Stop/Play generation isolation and restoration. Passive serial capture has
no allocation/decoder failure. After the first full HE frame, sampled free
heap is approximately 25–29 KiB and largest blocks are 8.5–9.5 KiB. This fixes
the initial SBR allocation, but is not yet a sustained HTTPS margin result.
Commit `da361bc7` therefore makes the 6/16/16 buffers and measured service
stacks part of fresh board defaults. The separate flash-heap option stays off.
The subsequent complete test sequence uses the `6.1-compact-ram` label;
its public HTTP/HTTPS checks precede load/soak tests to evaluate TLS headroom.

Fresh default builds of production, deep-sleep, RTC32k and QEMU complete.
The awake production image is 1,439,040 B, with ELF hash
`a39e1f6d01b5a2956d871abeb5fb805886d174511151eef59a78fd0f57a64d0b`.
Its linked type/call/patch audit passes. The saved profiling image was built
with the identical RAM choices via the explicit overlay; all four physical
configs pass a check of the complete AAC flags, buffer counts, full TLS records,
and absence of QEMU/Auto-Suspend/flash-allocator options.

The final QEMU repeat again matches all 865,280 retained PC19 PCM channel
samples byte for byte, with maximum 2-LSB error against native full precision.
The smaller service stacks do not change the shared decoder's stack size.
The short physical RAM check records minimum free stacks of 2,664 B (decoder),
1,204 B (audio output), 1,876 B (WebSocket status), 1,420 B (BOOT button) and
4,444 B (HTTP); sustained/OTA margins still need their own measurements.
For this compact stage the ten-minute soak targets HE-AACv2; AAC-LC remains
in the 60-second all-codec load matrix. The earlier 6.0.3 LC ten-minute result
is retained separately and is not substituted for the new HEv2 soak.

Saved evidence is split into the
[stock 6.1 controls](../tests/results/esp32c3-idf-upgrade-20261007/6.1/)
and the [initial compact run](../tests/results/esp32c3-idf-upgrade-20261007/6.1-compact/).
Their artifact indexes contain stored/original SHA-256 hashes. Large logs and
JSON files use lossless gzip compression; temporary flash images and TLS keys
are excluded. Final RAM-profile results are added separately after completion.

#### Complete RAM-profile format/EOF matrix

The complete matrix records 56 passes and one failure. All 22 AUTO/explicit
format checks, both AAC transition sequences, Stop/Play generation isolation,
all network-fault cases, WebSocket reconnect, rejection of the untrusted TLS
certificate, both boot checks and restoration pass.

The sole failure is `eof:he-44100-stereo:auto`: a status request times out
while observing the terminal transition. Its last response reports full
44.1 kHz stereo PCM, with RSSI -67 dBm; the observation ends after 5.516 seconds.
The following explicit-AAC EOF case passes. The serial record contains no
allocation/decoder failure, panic or heap-corruption marker. A separate repeat
of both AUTO and explicit EOF checks passes, as does restoration.
The initial timeout remains a failure with undetermined cause; the repeat
does not overwrite or qualify that original run. Follow-on tests are allowed
only after checking the same firmware/configuration hashes and that the repeat
covers every failed case. The continuation record preserves this distinction.

#### Public-stream memory checks

The RAM-only profile does not qualify sustained public HE playback: HTTP
AAC-LC and MP3 pass, but HE64 fails the largest-block budget, and HE32/HEv2
record actual allocation/decoder failures. The serial log includes a failed
1,700-byte network allocation with 5,540 B free and a largest block of 1,344 B.
SBR had already been allocated. This is a different failure from the initial
32,744-byte SBR allocation and shows insufficient remaining network headroom.
Idle recovery and settings restoration pass. The run was initially held before
HTTPS for the separate RAM experiments below, then resumed with the original
RAM profile. Its failures are retained in the `6.1-compact-ram` evidence directory.

The next diagnostic image, `6.1-compact-heap-profile`, moves the heap allocator
to Flash using the SDK option. Relative to the RAM profile it frees 8,704 B of
IRAM and 872 B of initialized data, increasing linker heap capacity by 9,568 B.
This is static capacity, not a guaranteed runtime allocation margin. Auto
Suspend remains disabled. A saved source/configuration audit checks the board's
GPIO, I2C, I2S and SPI ISR scope against the SDK's heap-placement requirements.

HTTP AAC-LC, HE32 and MP3 pass with this image. HE64 fails the progressive-heap
gate; HEv2 at 16 kbit/s fails the profile/channel check. HTTPS AAC-LC passes,
but all three HE streams fail their SBR allocation: 32,744 B requested with
only 19,456–24,576 B available as the largest block. HTTPS MP3 fails the
progressive-heap gate. Idle recovery and restoration pass in both transports.
Consequently allocator placement alone is not promoted or treated as a full
HE-AAC fix. The saved diagnostic app ELF is
`37341490d2fb648f5308ffcc75fc1a3f1426a27936ef149cc5500164f4b55fdc`.

The 16-kbit/s profile discrepancy also reproduces on a newly captured complete
ADTS recording in isolated QEMU, without Wi-Fi or TLS: FFprobe reports HE-AACv2,
32 kHz stereo, while the adapter reports HE-AAC with one source channel and
two PCM channels. Comparing its PCM against the native-history control is
required before attributing this to compact storage or changing its label.
Broadcast audio and raw PCM stay outside tracked results; retain hashes and
derived statistics only.

The independent follow-up resolves this case as **HE-AAC mono**, not lost PS.
The native-history control also produces duplicated mono. Unquantized FAAD
decodes all 188 frames at 32 kHz with one channel and zero PS frames; FFmpeg's
385,024 stereo pairs are identical. FFprobe's HEv2 classification is the
[implicit-mono heuristic in its AAC parser](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/aac/aacdec.c#L1851-L1865).
The new PC19/native comparison covers 770,048 channel samples: 88 changed,
maximum 2 LSB, RMS 0.012379 LSB, zero above 3 LSB. No samples are skipped.
This agrees with the earlier mono identification in the October 4 metadata
report and does not constitute a new PS decoder defect.

The public-stream runner now optionally resolves AAC profile/source channels
using a fresh complete HTTPS capture and the independent FAAD probe. It retains
the original FFprobe result and requires actual PS evidence for HEv2. The
initial format failure remains unchanged in its historical report. The added
reference tests pass, along with the 19 acceptance and six load-window tests.
A fresh five-second source check again decodes all 79 frames as HE mono with
zero PS frames. The TCP-pool-only follow-up still fails HTTPS HE64's SBR
allocation (32,744 requested, largest block 21,504 B); dynamic TLS is evaluated
separately while keeping 16 KiB receive capacity and certificate verification.

#### Combined TLS memory experiment (separate from defaults)

`6.1-compact-tls-profile` combines Flash heap placement, the RTC TCP PCB pool
and dynamic TLS record buffers with compact AAC. Full 16,384-byte RX capacity,
certificate verification and the ordinary certificate/configuration lifetime
are preserved. Auto Suspend remains off. The three pool/TLS trial images pass
the linked AAC type/call/patch audit.

All five HTTP stream checks pass, as do idle recovery and settings restoration:

| Input | Mean CPU | Minimum free heap | Minimum largest block |
| --- | ---: | ---: | ---: |
| AAC-LC 128 kbit/s | 49.34% | 56,676 B | 40,960 B |
| HE-AAC stereo 64 kbit/s | 63.26% | 19,152 B | 6,656 B |
| HE-AAC stereo 32 kbit/s | 60.64% | 17,668 B | 6,144 B |
| HE-AAC mono 16 kbit/s | 44.82% | 14,208 B | 4,608 B |
| MP3 256 kbit/s | 57.74% | 81,892 B | 63,488 B |

These are the runner's stable 15–60-second windows with 0.1-second polling;
descriptive 5–35-second summaries are saved separately and may have different
minima. They are not simultaneous or content-matched CPU comparisons.

HTTPS AAC-LC and MP3 pass. HE64 and HE32 now allocate SBR and show full 44.1 kHz
stereo, but fail later network allocations under the diagnostic/WebUI workload.
For example, a 1,700-byte request fails with 7,484 B free and a 1,472-byte largest
block. The HE-mono case fails during host reference probing with `TimeoutExpired`,
before board playback; it supplies no playback result. Idle recovery and
restoration pass. Thus this profile is not fully qualified.

The matching quiet production control installs through OTA and passes the
HE64 stereo and HE-mono HTTPS status/WebSocket checks plus restoration. This
control uses 0.4-second polling versus 0.1 seconds for profiling, so it does
**not** isolate diagnostic overhead or establish equivalent heavy-load
headroom. It has no CPU/heap counters and supplies no acoustic/IRQ guarantee.
Its ELF SHA-256 is
`48fa2de4999bef83047c56ab9b010b6eba2bb176174773fa8a6b25857c9feae2`.
The extra allocator/pool/TLS settings remain experimental; qualification of
the selected compact defaults continues separately on the RAM profile.

#### Selected-default load checks

After restoring `6.1-compact-ram-profile`, the remaining HTTPS run retains
failures for all three HE sources (SBR allocation), a progressive-heap-gate
failure for LC, and a pass for MP3. Idle recovery and restoration pass.
This does not prevent the independent local-source format/load measurements;
it does prevent claiming complete public HTTPS acceptance for these defaults.

The seven 60-second controlled-load cases then complete. No allocation,
decoder, panic or watchdog marker is recorded during these playback windows.
All seven settled post-Stop heap checks pass. Means below exclude the first
ten seconds; the original gate outcomes remain unchanged:

| Input | Mean CPU | Minimum free heap | Audio/wall duration | Load gate |
| --- | ---: | ---: | ---: | --- |
| MP3 48 kHz stereo | 57.9% | 64,592 B | 1.0017 | Progressive heap decline |
| FLAC 48 kHz stereo | 60.9% | 55,448 B | 1.0015 | PASS |
| Vorbis 48 kHz stereo | 70.7% | 53,504 B | 1.0016 | Progressive heap decline |
| Opus 48 kHz stereo | 77.3% | 64,404 B | 1.0018 | Progressive heap decline |
| AAC-LC 48 kHz stereo | 44.6% | 55,972 B | 1.0016 | PASS |
| HE-AAC 48 kHz stereo | 60.8% | 29,136 B | 1.0016 | PASS |
| HE-AACv2 44.1 kHz stereo | 64.8% | 29,444 B | 1.0014 | PASS |

The three non-AAC heap-gate failures also occurred in the matched 6.0.2/6.0.3
controls. Their CPU means differ from 6.0.3 by less than one percentage point
in this sequential run; this is not a randomized speed comparison. LC improves
from the earlier failed heap gate to a pass. HE and HEv2 now provide full-rate
measurements where the original-default controls could not allocate SBR.
Audio/wall progress is telemetry, not proof that every physical DMA sample
was delivered without a gap.

Sampled minimum free stacks in the complete load run are 2,656 B for the
decoder, 1,212 B for audio output, 1,884 B for WebSocket status, 1,420 B for
the BOOT button and 4,364 B for HTTP. The shared decoder retains its 16 KiB
allocation; the large scoped QMF workspace does not move into a smaller stack.

#### Selected-default switching and connection recovery

All 15 FLAC truncation checks pass, including bounded EOF, subsequent LC/FLAC
playback, runtime health and restoration. The station-switching suite completes
all 33 changes across three cycles without a format failure; heap recovery and
restoration also pass.

Connection recovery passes for LC and full-rate HE-AACv2. Stop, switching,
disabling pending retries, watchdog-off behavior, configured 3/10-second
timeouts, stalled-stream timeout and settings persistence all pass. Runtime
health and restoration pass too. The post-series largest-block gate fails:
the idle median changes from 81,920 B to 69,632 B, a 12,288-byte reduction.
Total free heap changes from 132,156 B to 130,660 B (1,496 B), with 17 tasks
before and after. The free-heap gate passes; the largest-block gate does not.

These measurements use the existing 12-second settled-idle observation. They
do not identify a 12 KiB leak: block layout and still-live network allocations
can affect contiguous space, and the cause is not established by this run.
The matched 6.0.3 retry series lost 4,096 B of largest-block capacity and passed
that gate, but failed HEv2 recovery and runtime health because SBR allocation
failed. Preserve both outcomes; the new series is not an unconditional pass.

#### Selected-default ten-minute HE-AACv2 run

The 600-second local HEv2/44.1 kHz stereo run **fails**. The original runner
reports a WebUI response above its two-second limit (maximum 3,078 ms).
Full-window replay also fails the runtime-memory gate. Passive serial capture
contains 45 failed 1,700-byte allocations; the first has 4,396 B free but only
a 1,536-byte largest block. It occurs about 369 seconds into playback.
The first five-minute subwindow already fails progressive heap decline;
the second also contains allocation failures. Restoration/reboot passes.

After the ten-second warm-up, mean CPU is 56.98%, peak 58.7%, and decoder time
is 42.77% of reported audio duration. CPU is informational, without a percentage
ceiling. Periodically sampled free heap falls from a 28,716-byte initial median
to 11,512 B; its sampled minimum is 6,060 B (the allocation-failure callback
captures lower transient values). Largest-block medians fall from 11,776 to
3,968 B. Minimum RSSI is -74 dBm.

The audio/wall ratio is 1.00159, but that counter cannot establish gap-free
physical audio in the presence of allocation failures. No panic or watchdog
marker is recorded. This is a sustained-memory limitation of the selected
full-radio profiling configuration; the short passing HE load checks and
QEMU PCM comparisons do not waive it. Quiet-production checks below evaluate
a different workload and cannot replace this failed ten-minute result.
Sampled minimum free stacks during the soak are 2,760 B for the decoder,
1,120 B for audio output, 1,880 B for WebSocket status, 1,420 B for BOOT and
4,444 B for HTTP. The recorded failures concern heap allocations, not a
reported stack-overflow event.

#### HTTP length guard retained across the SDK upgrade

The initial quiet image passes all 14 OTA cases and all 29 local production
checks (22 format selections, transitions, Stop/Play, WebSocket, two boots and
restoration). Its malformed-header test records two failures: the two lengths
above `UINT32_MAX` receive HTTP 400 instead of 413. The other three malformed
headers and restoration pass. These original results are retained.

Inspection of the pinned 6.1 source finds the old narrowing assignment in
`esp_http_server/src/httpd_parse.c`; it lacks the bounds check present in 6.0.3.
The 400 response alone does not prove rejection before truncation. The project
therefore generates a local parser source with the exact 6.0.3 guard before
conversion, including correct treatment of the no-body `ULLONG_MAX` sentinel.
The shared SDK is untouched. Reviewed source fingerprints accept only the
known 6.0.2/6.0.3/6.1 files after CRLF/LF normalization; an unknown change stops
configuration. Already-fixed 6.0.3 source remains byte-identical.

`tools/test_httpd_content_length.py` compiles the actual selected guard in a
32-bit request-length harness under ASan/UBSan. All 33 guarded boundary cases
pass (11 per SDK); each original 6.0.2/6.1 control fails four cases, including
`UINT32_MAX` being mistaken for the sentinel and oversized lengths narrowing.
Unknown-source rejection and both checkout line-ending forms also pass.
The first C3 integration build exposed a missing private include path for the
generated source; adding the original HTTP component's `src` path fixes the
build without editing the SDK.

The guarded production image is saved separately as
`esp32c3-idf-6.1-compact-ram-http-production`: 1,439,072 B, ELF
`7747cbbadf391666c1acf940e053e6081d9eac690befe13b70a9e4820faff998`.
Its SDK configuration is byte-identical to the preceding quiet image, and the
linked AAC audit again confirms the 32,744-byte owner, 204-byte adapter and
all compact/late-SBR options. Original profiling CPU/heap and QEMU measurements
remain results for their recorded images; they are not new measurements of
this HTTP-only rebuild. The initial physical pipeline deliberately stops before
quiet HTTPS so that the remaining check uses the guarded image.

On the guarded image, all five malformed-header cases plus restoration pass,
with the two oversized lengths returning 413. All 14 OTA checks pass again.
The targeted production repeat passes all 13 checks: AUTO/explicit LC 48 kHz,
HE 48 kHz and HEv2 44.1 kHz; changing formats, late SBR, Stop/Play, WebSocket,
two boots and restoration. Wi-Fi, playlist and exposed settings are preserved.
The profile, deep-sleep and RTC32k guarded variants also build and are saved
separately. All four configurations match their corresponding original variants
byte for byte, and compile commands confirm exactly one generated HTTP parser.
The guarded profiling image is build/audit-only; it has no new physical soak.

#### Final quiet HTTPS and board state

The guarded quiet image passes 60-second HTTPS AAC-LC/128 and MP3/256 checks.
HE stereo/64, HE stereo/32 and HE mono/16 all fail to produce PCM within the
15-second startup budget. The independent reference resolves profile/channels
before each run; the mono stream is not misclassified as a lost-PS defect.
This production run observes status and WebSocket behavior at 0.4-second
intervals; it supplies no CPU/heap trace identifying the exact allocation that
fails. Its failures are consistent with the earlier profiling limitations,
but the diagnostic allocation values must not be attributed to this image.
Restoration passes; Wi-Fi, playlist and exposed settings are unchanged.

The final independent read confirms ELF
`7747cbbadf391666c1acf940e053e6081d9eac690befe13b70a9e4820faff998`
in `app1`, with playback stopped and RSSI -69 dBm. The board uses the guarded
awake production image; deep sleep and the external-crystal variant were only
compiled. The branch remains separate from `main`.

| Selected compact configuration check | Result |
| --- | --- |
| Full profiling format/EOF/network matrix | 56 PASS, one status-request timeout; separate EOF repeat 3 PASS |
| Local 60-second HE and HEv2 load | Full rate, PASS; CPU approximately 61% / 65% |
| Ten-minute HEv2 with profiling/WebUI | FAIL: allocation failures, heap decline and 3.078 s maximum HTTP response |
| Station switching | All 33 changes PASS; restoration and heap checks PASS |
| Retry/timeout suite | 14 PASS; one largest-block recovery failure |
| Quiet local production matrix before HTTP backport | 29 PASS |
| Guarded-image local AAC/transitions/WebSocket/boot repeat | 13 PASS |
| Guarded-image malformed HTTP headers and restoration | 6 PASS |
| Guarded-image OTA including restoration | 14 PASS |
| Guarded-image public HTTPS | LC and MP3 PASS; three HE startup failures; restoration PASS |

The remaining work is sustained network heap/contiguous-block headroom,
including the retry-series largest-block loss, and successful HE HTTPS startup.
These are not resolved by the measured 2-LSB PCM precision result. Do not infer
gap-free audio from decoder counters, or call the entire SDK upgrade accepted.

The [final compact evidence archive](../tests/results/esp32c3-idf-upgrade-20261007/6.1-compact-ram-final/)
contains the original and guarded runs, boundary-test controls, exact build
configs, per-image hashes, failure reasons and the final board read. Its summary
retains original FAIL outcomes and distinguishes passing repeats. The earlier
initial compact/RAM archives remain unchanged.
