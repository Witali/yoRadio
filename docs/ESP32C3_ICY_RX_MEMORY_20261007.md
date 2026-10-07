# ESP32-C3 ICY and network receive memory — 2026-10-07

These experiments use the separate `codex/esp32c3-idf-upgrade` branch and pinned
ESP-IDF 6.1. Compact PC19 HE-AAC remains the board default, with full SBR/PS and
full output rates. This work does not change AAC arithmetic or its precision
policy. Network experiments below are **not defaults**.

## ICY title storage

The stream task previously retained the entire 4080-byte ICY metadata block
plus a terminator, although the published title accepts only 191 bytes. It now
parses each incoming chunk and keeps the published prefix plus parser state.

| Measurement | Before | After | Saving |
|---|---:|---:|---:|
| ICY state symbol | 4081 B | 204 B | 3877 B |
| Linked `.dram0.bss`, including alignment | See `icy-size.json` | See `icy-size.json` | **3888 B** |

The two quiet builds have identical sdkconfig settings. The BSS result is an
actual ELF measurement; it differs from the symbol-size subtraction because of
alignment. The replacement does not allocate memory, reduce title capacity or
change audio framing. It consumes the rest of the declared metadata block after
finding a title. A missing title preserves the previous one; an explicit empty
title clears it. The old quote-semicolon preference and bare-quote fallback are
preserved, as are generation guards against stale titles after Stop/switch.
Debug logging now prints only the retained title prefix.

Validation completed:

- 57,227 differential comparisons with the old whole-block parser under
  ASan/UBSan: PASS. Boundary cases include every split, byte-at-a-time input,
  4080-byte blocks, UTF-8, embedded NUL, quotes and resets.
- 49 selected Node tests, including that native test and C3 integration guards:
  PASS; three Python fixture-server tests: PASS.
- Both ordinary diagnostic and quiet production builds: PASS. Linked AAC
  verification retains a 32,744-byte SBR owner, 204-byte adapter and all eight
  required AAC/compact/late-extension feature flags.
- Physical diagnostic image: seven ICY cases, runtime checks and restore all
  PASS. Each case checks full-rate HE-AACv2 playback and the WebUI title. This is
  a functional/framing test, not an acoustic continuity measurement.

## Matched receive-copy experiment

The pair differs only in `CONFIG_LWIP_L2_TO_L3_COPY` and its compatibility alias.
Both include the previously separate flash-heap placement, RTC TCP PCB pool,
dynamic full-capacity TLS buffers and CPU/network profiling. Both **precede the
ICY change**. They preserve the 11,520-byte TCP receive window, mailbox size 10,
Wi-Fi static/dynamic RX/TX counts 6/16/16, 16 KiB TLS input capacity and 16 KiB
decoder stack. Auto Suspend and direct DMA are disabled.

The native SDK copy path allocates an appropriately sized RAM pbuf, copies the
received frame and releases the Wi-Fi receive buffer immediately. The ordinary
path retains that driver buffer until the pbuf is released. No custom packet
copy implementation or reduced protocol capacity is introduced here.

Each test played the same local HE-AACv2 44.1 kHz stereo fixture continuously for
600 seconds, with status polling every 0.1 seconds and 12-second idle checks
before/after. The source is paced at 1.02 times its nominal rate. CPU is
informational; no former 85% limit is applied.

| Measurement | Ordinary receive buffers | SDK L2-to-L3 copy |
|---|---:|---:|
| Original ten-minute gate | FAIL: runtime allocation failure | FAIL: progressive heap loss |
| Observed allocation failures | 3 × 1700 B | **0** |
| Sampled minimum free heap | 11,460 B | **20,432 B** |
| Sampled minimum largest block | 3,200 B | **6,400 B** |
| Mean / peak busy CPU | 71.33% / 72.9% | 71.48% / 73.1% |
| Decoder elapsed time / represented audio | 51.01% | 50.95% |
| Represented audio / wall time | 1.00159 | 1.00162 |
| First / last heap medians | 36,336 / 16,912 B | 36,368 / 24,084 B |
| First / last largest-block medians | 17,408 / 4,608 B | 19,456 / 8,192 B |
| Last 290-second subwindow | FAIL: allocation failure | PASS |
| Stop/idle memory recovery | PASS | PASS |
| RSSI median / minimum | −69 / −77 dBm | −70 / −78 dBm |

The minimum sampled heap is not the instantaneous minimum at an allocation
failure: the control failures reported only about 9.9 KiB free and a 1536-byte
largest block. Playback progress alone does not make these failures acceptable.
Receive-credit counters measure logical outstanding data, not allocated RAM;
they must not be added to or subtracted from the heap as a claimed saving.

Host firmware builds overlapped both soaks. Recorded maximum source pacing
lateness was 31.9 ms / 31.0 ms. This one pair supports further testing of the
copy path, not a precise CPU-speed claim or proof of long-term leak freedom.
The original full-window failures are retained even though later copy samples
and memory recovery pass. DMA/physical audio continuity was not captured.

The TCP snapshots support receive-queue filling as part of the explanation:
median uncredited receive data increases from zero in the first minute to
9472.5 B / 10,192.5 B in the last minute for control/copy. A source paced 2%
faster than playback builds a backlog until backpressure limits it. This is
consistent with the later plateau and recovery, but does not account for every
allocated byte or prove that all long-term memory problems are resolved.

### Public HTTPS probes in this pair

The control began full-rate HE-AAC decoding, then a WebUI status request timed
out after seven samples. The copy run timed out during the host reference-probe
stage, before issuing board playback. Both are retained as FAIL; they do not
form a usable HTTPS A/B result and neither is relabelled as a format failure.

## Combined ICY and receive-copy candidate

The combined profiling image preserves the experimental network settings and
adds the bounded ICY parser. Independent FAAD reference probing and physical
60-second tests of Groove Salad HE-AAC 64 kbit/s pass over both transports:

| Measurement | HTTP | HTTPS |
|---|---:|---:|
| Playback/load gate and stop/recovery | PASS | PASS |
| First observed PCM | 0.625 s | 2.609 s |
| Mean / peak busy CPU | 63.58% / 64.1% | 64.54% / 65.5% |
| Sampled minimum free heap | 26,692 B | 21,584 B |
| Sampled minimum largest block | 15,360 B | 5,888 B |
| Maximum status request time | 125 ms | 125 ms |

These are tests of one public source with live content, not an isolated ICY
speed comparison or coverage of every TLS record pattern.

The subsequent 600-second local HE-AACv2 test completed with zero recorded
allocation/decoder failures and successful stop/heap recovery. Its original
full-window verdict is still FAIL for progressive heap loss; the last
290-second subwindow is PASS. Sampled minimum free heap is **25,968 B**, minimum
largest block **9728 B**, mean/peak busy CPU **70.77% / 72.0%**, and represented
audio/wall time **1.00162**. The maximum status-request time was 156 ms; minimum
RSSI was −76 dBm. First/last heap medians are 40,352 / 28,472 B and largest-block
medians 23,552 / 14,848 B. These observed improvements over the earlier pair
are not a substitute for the isolated 3888-byte static saving.

## Quiet production and OTA

The board was returned to `compact-icy-quiet`, which uses the current board
defaults and the ICY improvement, with deep sleep disabled. The experimental
copy/flash-heap/RTC-pool/dynamic-TLS combination is not enabled in this image.
Its exact ELF hash is
`da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0`.

All **14 OTA cases pass**: malformed/wrong-target images, incomplete/stalled
uploads, two alternating-slot round trips, a slow valid upload and restoration
of saved settings. This run does not include OTA while playing.

The first quiet ICY run has eight FAIL results because the original test
required UART records and the quiet image intentionally emits none. It retained
zero serial rows, not a panic trace. All seven cases had already passed their
WebUI-title and full-rate playback checks before the missing-log gate. That
original report is preserved. The runner now requires diagnostic firmware for
UART coverage, or an explicit `--functional-only` selection that checks
playback/title/restore and records UART coverage as not requested. This does
not turn missing UART evidence into a passed runtime-fault check.

The explicit quiet functional repeat passes **all seven title/playback cases
and settings restoration**. UART runtime-fault coverage remains unrequested
and unavailable on this quiet image; the diagnostic image's nine checks above
provide the separate logged result. No public-HTTPS certification is inferred
for the quiet default image from the experimental profiling image's results.

## Evidence and reproduction

Commands, reports, exact app/config hashes, source snapshots and build logs are
retained under `tests/results/esp32c3-icy-rx-memory-20261007/`; `index.json`
verifies stored and decompressed content. Broadcast audio and private settings
are not included. Firmware is retained under `firmware/development/`:

- `esp32c3-idf-6.1-memory-control-profile` and `...-memory-rxcopy-profile`:
  the matched pair, before ICY changes.
- `esp32c3-idf-6.1-compact-icy-debug` and `...-compact-icy-quiet`:
  ICY change with current board defaults; the latter adds the quiet production
  overlay. The debug build directory happens to end in `-production`; its
  saved sdkconfig and artifact name correctly identify it as diagnostic.
- `esp32c3-idf-6.1-memory-icy-rxcopy-profile` and `...-memory-icy-rxcopy-quiet`:
  combined experimental network profile plus ICY saving; not board defaults.

See the [testing guide](ESP32C3_TESTING.md#bounded-icy-song-title-parsing) for
parser and physical ICY commands, and the
[SDK qualification report](ESP32C3_IDF_UPGRADE_20261007.md) for earlier failures.
Successful compilation and a compact AAC layout do not certify every public
radio station or all TLS record sizes under concurrent WebUI load.

Before promoting the experimental network settings, repeat the broader
LC/HE/HE-mono/MP3 HTTPS and multi-codec switching matrix, test full 16 KiB TLS
record allocation under sustained load, and validate OTA during playback on
the exact candidate. Also compare the same copy/ICY improvements with static
TLS buffers: preserving maximum record capacity is distinct from having a
contiguous allocation available when a dynamic buffer grows.
