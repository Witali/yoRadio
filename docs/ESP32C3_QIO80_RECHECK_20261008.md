# ESP32-C3 DIO and QIO recheck on ESP-IDF 6.1

After this comparison, the user requested a
[quiet QIO production build and installation](ESP32C3_PRODUCTION_QIO80_20261008.md).
That separate deployment preserves the laboratory outcomes and qualification
limits below; the generic board default remains DIO.

## Why the previous promotion stopped

The [30 September full-radio comparison](ESP32C3_QIO80_ACCEPTANCE_20260930.md)
used ESP-IDF 6.0.2, before the EOF repair and subsequent compact AAC work.
QIO itself passed the [standalone bus/read/decoder checks](ESP32C3_FLASH_QUAD_20260930.md).
The radio also passed 30 software boots per mode and 15 QIO OTA checks.

Promotion stopped at the broader acceptance tests: EOF status failed for most
finite files, full HE-AAC could not allocate its 55,128-byte SBR owner, demanding
FLAC failed, and network/load/switch/soak tests were unsuccessful or incomplete.
Several defects occurred in both modes. RSSI differed substantially between
sequential runs; the evidence did not identify Quad as their cause.

## Matched builds for the repeat

This repeat uses pinned ESP-IDF 6.1 revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, full compact AAC and the current
EOF/network/decoder fixes. It uses two fresh laboratory builds with the same
profiling and memory settings as the [Rice control](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md):
copied network RX, six-segment TCP window, dynamic TLS, 17,058-byte RX reserve,
adaptive input minimum four blocks, and staged-output diagnostics. Bytewise
Rice and the separate CLZ experiment are disabled. CPU is 160 MHz, Flash is
80 MHz, tick is 1 ms, output/decode/stream priorities are 8/7/5, and deep sleep
is disabled. Normal TLS validation remains enabled; a laboratory CA is added
for the controlled HTTPS origin.

The semantic sdkconfig comparison differs only in DIO/QIO selection and its
compatibility/descriptor values. Both application images occupy 1,618,944 bytes.
Both have 47,690 bytes of IRAM text, 12,856 bytes of DRAM data and 45,664 bytes
of DRAM BSS. Main section addresses and sizes match. Their contents are not
byte-identical: configuration, version strings, constant layout and references
also differ. Retain this cache-layout limitation when interpreting small timing
changes. The compiled FLAC residual loop has identical bytes and address.

The saved variants are:

- `firmware/development/esp32c3-idf-6.1-r9a97-flash-dio80/`
- `firmware/development/esp32c3-idf-6.1-r9a97-flash-qio80/`

Each contains the application, matching second-stage bootloader, configuration
and provenance manifest. These diagnostic builds include experimental memory
overlays and are not production releases.

## Physical procedure and coverage

The board is the revision 0.4 C3 with 4 MiB XMC Flash, JEDEC `0x464016`, native
USB Serial/JTAG and no PSRAM. The controller saves a private full-Flash backup
and settings snapshot before installing the first variant. It verifies the
partition layout and writes only the matching bootloader and active application.
Application OTA alone cannot select the new bus mode.

`YORADIO_FLASH_MODE_PROBE=ON` adds an optional boot wrapper. It reads actual
SPI0 mode/clock registers, CPU frequency and Flash identity, verifies the
application image, and performs four CRC32 scans through mapped Flash. The host
compares every CRC and length with the saved application. The image exceeds the
cache; this probe does not explicitly invalidate cache. It waits eight seconds
for passive USB capture before running, then starts the ordinary radio even if
the probe fails, keeping recovery available. No mode register is changed by
the probe.

Each variant follows this sequence:

1. Two independently reset boots with verified SPI0 registers and mapped reads.
2. All 11 retained finite fixtures over HTTP and trusted HTTPS, with AUTO and
   explicit codec selection: 44 playback/format/EOF cases.
3. AAC format transitions, Stop/Play replacement, injected network faults and
   WebSocket format/reconnection.
4. Three switching cycles across LC, HE, HEv2 and FLAC, with settled heap checks.
5. A 60-second demanding FLAC HTTPS load and 600-second HE-AACv2 HTTPS load,
   both with frequent WebUI polling and before/after idle heap observations.
6. OTA rejection/interruption cases, roundtrip through both slots, slow upload
   and saved-settings verification; five software reboot/readiness samples.

DIO runs first, followed by QIO. Builds finish before playback tests begin.
This is a sequential comparison, not a randomized repeated crossover. CPU
percentage is informational. Existing format, progress, runtime, HTTP and heap
gates remain unchanged. CPU/decoder aggregates use complete intervals after
ten seconds; DMA deltas cover their actual observation windows.

The ten-minute load is not a one-hour soak. The eight-second probe delay is
included in these test-image boot times, so they are not production startup
times or directly comparable to the old 30-boot results. OTA during active
playback, cold power cycles, deep-sleep wake-up and acoustic/electrical output
capture are outside this repeat. DMA queue overruns are diagnostic events,
not an exact count of audible gaps.

## Results

### Acceptance overview

| Check | DIO 80 MHz | QIO 80 MHz |
| --- | --- | --- |
| Probed boots: actual mode, clock, image reads | 2/2 PASS | 2/2 PASS |
| HTTP: 11 fixtures, AUTO and explicit codec | 22/22 PASS | 22/22 PASS |
| Trusted HTTPS: same matrix | 22/22 PASS | 22/22 PASS |
| Format transitions, faults, WebSocket, restoration | 10/10 PASS | 10/10 PASS |
| Codec switching and settled heap | 3 cycles / 12 changes PASS | 3 cycles / 12 changes PASS |
| Heavy FLAC HTTPS / WebUI load, 60 s | **FAIL**, watchdog | **PASS** |
| HEv2 HTTPS / WebUI load, 600 s | **FAIL**, progressive heap loss | **FAIL**, progressive heap loss |
| Settled heap after each sustained case | PASS | PASS |
| OTA, including final settings check | 14/14 PASS | 14/14 PASS |
| Software reboot to WebUI | 5/5 PASS | 5/5 PASS |

The format matrix covers MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC and HE-AAC v2
at the retained fixtures' full rates/channel counts. It includes finite-file EOF
and does not reinstate the old 22 kHz AAC limit. OTA includes ten rejection or
interruption cases, two successful slot transitions, slow upload and final
restoration. The median/max readiness times are 15.687/15.969 s DIO and
15.625/15.953 s QIO, including the diagnostic probe delay described above.

### Actual bus mode and mapped reads

| Observation | DIO | QIO |
| --- | --- | --- |
| SPI0 CTRL, both probed boots | `0x00ac2008` | `0x012c2008` |
| Clock register / actual frequency | `0x80000000` / 80 MHz | `0x80000000` / 80 MHz |
| Four mapped application CRC32 reads per boot | `0x2df3d5b2`, PASS | `0xda2a6efd`, PASS |
| App length checked against saved binary | 1,618,944 bytes | 1,618,944 bytes |

The active slots differ because the DIO OTA sequence changes slots before QIO
installation: the probed DIO image is at `0x10000`, QIO at `0x1e0000`. Each probe
verifies its running image and the host checks the corresponding saved binary.
QOUT and Auto Suspend are disabled in both builds.

### Heavy FLAC over HTTPS

This is the retained 610-second, 48 kHz/stereo/16-bit stress fixture, observed
for 60 seconds with WebUI polling. Its average encoded bitrate is about
1,283 kbit/s. This test stresses the complete network/audio path.

| Measurement | DIO 80 MHz | QIO 80 MHz |
| --- | ---: | ---: |
| Original acceptance | **FAIL**, watchdog | **PASS** |
| Average total CPU busy | 100.00% | 78.49% |
| Decoder-task CPU | 19.98% | 19.59% |
| Stream-task CPU | 34.47% | 25.00% |
| Wi-Fi / TCP-IP CPU | 20.09% / 14.67% | 13.74% / 9.50% |
| Elapsed decoder ms per audio second | 198.84 | 195.36 |
| Decoded audio / elapsed time | 0.97833 | 1.00192 |
| DMA-written audio / elapsed time | 0.97916 | 1.00162 |
| DMA queue-overrun delta | 97 | 0 |
| DMA write errors | 0 | 0 |
| Watchdog event counter increase | 10 | 0 |
| RSSI median / minimum | -59 / -59 dBm | -63 / -67 dBm |
| Maximum observed HTTP latency | 156 ms | 125 ms |

These observations favor QIO in this demanding case. Most of the CPU difference
is in the stream, Wi-Fi and TCP/IP tasks; do not describe the 21.51 percentage
point reduction in total CPU as a 21.51% improvement of the FLAC decoder itself.
The runs are sequential and RF conditions and binary contents are not identical.
The report retains the raw DIO failure reason, `Serial panic or capture failure`;
the recorded cause here is task-watchdog starvation, not a confirmed reboot or
a separate processor panic. Register dumps are retained by the capture filter
under its generic `PANIC registers` label.

### Ten-minute HE-AAC v2 over HTTPS

The HEv2 fixture plays continuously at full 44.1 kHz stereo, with SBR/PS enabled
and WebUI polling every 0.1 seconds. Both runs complete the requested 600 seconds
and pass runtime/progress checks, but fail the existing progressive-heap gate.

| Measurement | DIO 80 MHz | QIO 80 MHz |
| --- | ---: | ---: |
| Original acceptance | **FAIL**, progressive heap loss | **FAIL**, progressive heap loss |
| Average total CPU busy | 70.70% | 60.48% |
| Decoder-task CPU | 45.89% | 41.03% |
| Elapsed decoder ms per audio second | 508.24 | 434.70 |
| Decoded audio / elapsed time | 1.00149 | 1.00158 |
| DMA-written audio / elapsed time | 1.00151 | 1.00161 |
| DMA queue-overrun delta | 6 | 0 |
| DMA write errors / watchdog events | 0 / 0 | 0 / 0 |
| Free heap, first / last medians | 26,404 / 16,432 bytes | 26,160 / 17,504 bytes |
| Free heap change | -9,972 bytes | -8,656 bytes |
| Largest free block, first / last medians | 14,336 / 4,864 bytes | 17,408 / 5,888 bytes |
| Minimum observed free heap / largest block | 14,856 / 4,608 bytes | 14,524 / 4,608 bytes |
| Settled idle heap before / after playback | 133,432 / 133,444 bytes | 133,232 / 133,152 bytes |
| Settled idle largest block before / after | 106,496 / 106,496 bytes | 106,496 / 106,496 bytes |
| RSSI median / minimum | -64 / -70 dBm | -64 / -74 dBm |
| Maximum observed HTTP latency | 391 ms | 203 ms |

The first/last heap figures are medians of the first/last three complete CPU
telemetry samples after warmup. Idle recovery is a separate before/after Stop
observation and passes in both modes. This does not establish a permanent leak
or identify the allocator/caller responsible for growth during playback. It
does establish that the behavior is not specific to QIO. Trace allocations
and separate audio, TLS and WebUI polling lifetimes before assigning a cause.

The [9 October paired-snapshot analysis](ESP32C3_HEAP_RECEIVE_20261009.md)
quantifies receive-credit correlation and identifies the test server's 2%
delivery surplus. It adds a rate-controlled follow-up without changing these
original acceptance results.

### Decision

**QIO 80 MHz works and remains a promising candidate.** The repeat clears the
old finite-file/EOF and full-rate HE-AAC failures, and the observed QIO load
results improve on DIO. In this run, QIO has no DMA queue overruns in either
sustained case. Acoustic continuity was not measured.

**Do not mark the complete radio acceptance green yet.** Both builds still fail
the ten-minute HEv2 heap gate, and restoration required a second reset. Keep
these as laboratory variants and retain the
current DIO production default until that behavior is explained or fixed and
the intended production configuration is qualified. This is not a finding of
QIO incompatibility, and high CPU utilization alone does not fail acceptance.

## Evidence and reproduction

The [retained evidence](../tests/results/esp32c3-qio80-recheck-20261008/README.md)
contains original reports, filtered runtime logs, CPU/decoder/DMA observations,
image/configuration/source hashes, build recipes and linked-code audits.
`summary.json` is derived by `summarize.py`; original failure records remain
intact. Firmware manifests point to `qualification.json`; neither laboratory
variant is marked qualified for production.

From the repository root, replay the parser and evidence checks without
contacting the board:

```powershell
python tests/test-flash-mode-probe.py
python tests/test-qio80-recheck-evidence.py
```

## Board restoration

The controller restored the original bootloader, OTA data and both application
partitions. A full 4 MiB readback matches the private pre-test backup byte for
byte. The partition table, NVS and SPIFFS match too; the restore operation did
not write those regions. The Flash status is `0x0200` before and after.

The first reset after restoration did **not** return the expected WebUI within
45 seconds, so the controller exited with an error. A second watchdog reset
through the board skill, without another Flash write, returned HTTP 200.
`restoration-recovery.json` preserves that unsuccessful first attempt. The cause
of this startup delay/failure is not established; it must not be silently counted
as a first-attempt pass or attributed to a particular bus mode.

The final WebUI identifies the original `compact-icy-quiet` image, ELF SHA-256
`da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0`.
Three observations five seconds apart confirm the initial playback state has
returned. Both variants passed in-memory Wi-Fi/playlist/settings comparisons
before restoration. The original controller's reference snapshot was lost on
exit, so no new snapshot-equality claim is made after the retry: persistence
evidence at that point is the exact NVS/SPIFFS readback and the last successful
pre-restore comparison. No private snapshots, full-Flash backup or TLS keys are
included in the committed evidence.
