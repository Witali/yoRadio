# ESP32-C3 radio production acceptance, 2026-10-15

## Decision

**Accepted for the normal-playback objective on this ESP32-C3 OLED board.**
The saved quiet image passes 139 campaign checks plus six post-install checks
and is installed on the board. AAC-LC, HE-AAC, HE-AAC v2, MP3, FLAC, Vorbis and
Opus have the playback, recovery and numerical evidence summarized below.
No allocation failure, watchdog event or unexpected reboot was observed in
the accepted campaigns. The explicit network-starvation and measurement limits
below remain; this decision does not turn separate research plans into completed
work or guarantee playback through every possible interruption of the source.

## Exact application under review

- Artifact: [esp32c3-idf61-raw-tail-quiet](../firmware/development/esp32c3-idf61-raw-tail-quiet/manifest.json).
- Embedded version: `idf61-rawq-20261015`; source commit: `453cd451950abd1d6b5a6a6436ee8c8a6a302ff8`.
- Application SHA-256: `90334aabe2d62cbec10b0686433eba43d8c79bd62c5c191db337dace5e571aeb`.
- ELF SHA-256: `8d63aee7c134d8c994d254bb8bdea3a66ad33d552ad3ef4ba2426d99b4cbc2e5`.
- Application size: 1,474,288 bytes; ESP-IDF revision: `9a97f6c54ec638111ce55cd36581b3c192f15207`.
- QIO 80 MHz, nominal fractional 48-kHz output, output task priority above decoder.
- Quiet application, no deep sleep, normal public TLS roots; no laboratory CA.
- Full-rate compact AAC/SBR/PS, PC19 history, late SBR and early compact owner.
- TLS RX reserve 17,058 bytes; bounded input pool with tail coalescing;
  2,048-byte reads, 250-ms read timeout and 1,000-ms startup prefill.

Configuration equality does not establish binary identity. Qualify and install
the saved application above; a new build must have its own recorded identity.

## Requirements and current evidence

| Requirement | Evidence | Assessment |
| --- | --- | --- |
| AAC-LC, HE-AAC and HE-AAC v2; preserve SBR/PS and full decoded rate | HTTP matrix includes LC 22.05/44.1/48 kHz, mono/stereo, HE 44.1/48 kHz and HEv2 44.1 kHz; implicit/late SBR and mixed-family transitions | Passed tested cases; no 22-kHz cap or core-only substitution |
| Other implemented native codecs | MP3, FLAC, Vorbis and Opus, AUTO and explicit hints; natural EOF; public HTTPS FLAC/Vorbis/Opus; 600-s FLAC/Vorbis/Opus | Passed tested cases |
| Safe parameter/decoder changes | 11/11 transition checks: rate/profile changes, implicit SBR, MP3/AAC changes and Stop/Play generations | Passed |
| No crashes or allocation failures; recover memory | Lifetime health, settled recovery and active memory-trend gates in each campaign | Passed completed campaigns; numerical free-heap floors are diagnostic |
| HTTPS and network recovery | Normal certificate verification; five public AAC/MP3 profiles; 600-s HE-AAC and AAC-LC; drop/stall/error/redirect/jitter recovery | Passed tested cases |
| Correct terminal and browser state | Natural EOF in file matrix, WebSocket metadata/reconnect, stopped-state checks | Passed |
| Safe OTA and preserved settings | 15/15 invalid/interrupted/round-trip/playing/slow-upload/restoration checks; final install and six post-install checks | Passed; exact saved image installed, settings unchanged |
| Production numerical tolerance of 3 PCM LSB | Revalidated recording statistics and retained pinned-SDK PCM comparisons | Peak 2 LSB on the measured corpus; not a universal input bound |
| Reproducible production options | Fresh and reused directories through `build-production.ps1 -TestedRadioProfile` both match all 1,603 normalized candidate values | Passed |

Implemented native codec support here means the AAC/MP3/FLAC/Vorbis/Opus
set compiled into this application. xHE-AAC, additional containers, optional
deep sleep and other boards remain separate development work; they are not
claimed as tested by this report.

## Completed campaigns

| Campaign | Checks passed | Evidence |
| --- | ---: | --- |
| Public HTTPS files | 16/16 | [Reports](../tests/results/esp32c3-raw-tail-quiet-20261015/qualification/public-files/report.json) |
| Local HTTP files | 28/28 | [Reports](../tests/results/esp32c3-raw-tail-quiet-20261015/qualification/http/report.json) |
| Transitions | 11/11 | [Reports](../tests/results/esp32c3-raw-tail-quiet-20261015/qualification/transitions/report.json) |
| Network recovery | 11/11 | [Reports](../tests/results/esp32c3-raw-tail-quiet-20261015/qualification/network/report.json) |
| WebSocket | 7/7 | [Reports](../tests/results/esp32c3-raw-tail-quiet-20261015/qualification/websocket/report.json) |
| OTA | 15/15 | [Reports](../tests/results/esp32c3-raw-tail-quiet-20261015/qualification/ota/report.json) |
| Public HTTPS radio: 600-s HE-AAC plus four 60-s AAC/MP3 cases | 17/17 | [Audit](../tests/results/esp32c3-raw-tail-quiet-20261015/public-radio/audit.json) |
| Sustained FLAC/Vorbis/Opus: 600 s each | 27/27 | [Audit](../tests/results/esp32c3-raw-tail-quiet-20261015/sustained/audit.json) |
| Public AAC-LC HTTPS repeat: 600 s | 7/7 | [Audit](../tests/results/esp32c3-raw-tail-quiet-20261015/public-lc-repeat/audit.json) |
| Final OTA installation: HE-AAC 48 kHz, HEv2 44.1 kHz, recovery/settings/health | 6/6 | [Audit](../tests/results/esp32c3-raw-tail-quiet-20261015/final-deployment/audit.json) |

The first five playback suites contain 2,096 health samples; the public-radio
campaign adds 1,572. Each campaign has a consistent boot identity and no
reported allocation, decoder-failure or watchdog events. OTA intentionally
reboots the application. Controllers verify application identity and unchanged
Wi-Fi, playlist and settings without saving their private contents.

The three sustained cases add 1,621 health samples on one boot, with zero
reported allocation, decoder or watchdog faults and no failed traced request.
All playback windows have zero completion drops and write errors. After each
Stop, the largest free block returns to 114,688 bytes. These are continuously
encoded 610-second synthetic fixtures, paced at 1.0, not looped short files.

| Sustained codec | Measured steady output | Minimum free heap / largest block |
| --- | ---: | ---: |
| FLAC, 48 kHz stereo | 584.049 s | 62,440 / 45,056 B |
| Vorbis, 48 kHz stereo | 584.854 s | 69,612 / 53,248 B |
| Opus, 48 kHz stereo | 584.166 s | 80,384 / 65,536 B |

The 16-kbit/s public source is **HE-AAC mono**, duplicated to two output
channels; it is not PS evidence. HE-AAC v2 has separate fixture and PCM coverage.

The separate AAC-LC repeat has 1,119 health samples, zero recorded allocation,
decoder and watchdog events, and no traced HTTP failure. Its 584.694-second
steady output window has zero completion drops/write errors. Minimum free
heap/largest block are 58,440/32,768 bytes; maximum paired status/health response
is 583.672 ms. Settled recovery and original application/settings restoration
pass. The completed physical campaigns now contain **139 passing checks**.

The [numerical audit](../tests/results/esp32c3-raw-tail-quiet-20261015/evidence-audit/)
rechecks five recording statistics (12,505,088 channel samples, peak 2 LSB)
and directly compares 865,280 retained pinned-SDK late/resumed-SBR PCM samples
with full-precision and PC19 references. Existing policy/evidence tests pass
24 checks. This reuses identified historical captures; it is not a fresh
physical PCM recording. The codec archive matches, while later wrapper and
owner changes are explicitly recorded rather than assumed identical.

## Failures and limits that remain visible

- The first final-install smoke runner failed to import its local test-server
  module before playing audio. Its controller restored the original image and
  verified settings. The [failed harness and rollback](../tests/results/esp32c3-raw-tail-quiet-20261015/final-deployment-import-failure/)
  are retained. Correcting the import order, with no firmware change, gives
  the separate six-check passing final installation above.
- Earlier quiet candidates had spontaneous AAC-LC/FLAC output failures and
  WebUI TCP timeouts. They remain in the [investigation](ESP32C3_FLAC_OUTPUT_20261015.md).
  Current successful windows do not establish the cause of every historical
  fault. The exact-image ten-minute AAC-LC repeat now passes; the earlier failed
  reports remain unchanged.
- Diagnostic FLAC with injected 100/250/500-ms delivery pauses still has a
  failed output gate: 32 completion drops. It recovers without an allocation
  failure or crash. No claim of uninterrupted audio under arbitrary network
  starvation is made, and this failed experiment is not rewritten as passing.
- Output acceptance measures counter **increments during playback**, excluding
  startup warmup and idle. Absolute idle completion counters are not faults
  attributed to a codec. These measurements do not replace analog loopback.
- Some internal FLAC errors can be resynchronized without incrementing the
  generic decoder-failure counter. Separate EOF, duration, output and retained
  decoder/byte-identity evidence are needed; zero telemetry alone is insufficient.
- No new rate/channel restriction, reduced AAC profile or relaxed PCM error
  threshold was introduced to obtain a pass. CPU utilization is not a release
  gate in these quiet tests; actual playback faults and recovery are checked.

## Completed acceptance actions

1. **Done:** exact-image 600-second FLAC/Vorbis/Opus campaign archived,
   including recovery and verified restoration of the original application,
   private settings and stopped playback.
2. **Done:** 600-second public AAC-LC repeat passes and is archived separately.
3. **Done:** tested-radio defaults applied; fresh and reused directories through
   the normal wrapper match every candidate configuration value. The reused
   case starts from the older production configuration with the new features
   disabled. [Wrapper evidence](../tests/results/esp32c3-raw-tail-quiet-20261015/profile-wrapper/)
   supplements the earlier standalone preflight. Documentation subsequently
   fixes boot-file selection and two text-encoding errors; those edits do not
   change the configuration or application. All 24 PowerShell blocks parse,
   and the current variant's application/boot-file hashes pass the guide's checks.
4. **Done:** exact saved image installed through app-only OTA, with HE-AAC/PS
   playback, natural EOF, output, memory recovery and unchanged settings verified.
   Final identity is `idf61-rawq-20261015`, partition `app1`, ELF SHA-256
   `8d63aee7c134d8c994d254bb8bdea3a66ad33d552ad3ef4ba2426d99b4cbc2e5`.
   Playback is stopped; Wi-Fi, playlist and settings are preserved.
5. **Done:** artifact qualification records this decision and the exact-image
   evidence. Prior candidate failures and diagnostic starvation tests remain
   unchanged. The first-install USB procedure is checked offline; its separate
   fresh-board hardware validation is not claimed by the OTA campaign.

The [final read-only audit](../tests/results/esp32c3-raw-tail-quiet-20261015/completion/)
checks all 145 report cases against the installed ELF identity, artifact hashes,
both complete configuration comparisons and current profile sources. A fresh
board read confirms the same boot, stopped playback and no allocation/watchdog
event after deployment. Source comparison from the application build commit
shows only profile/Kconfig documentation and README changes under `idf`,
`yoRadio` and `tools`; executable audio/network code is unchanged.
