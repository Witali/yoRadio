# ESP32-C3 initial compressed-input prefill experiment

## Purpose and implementation

After the [fractional PDM clock comparison](ESP32C3_PDM_CLOCK_20261009.md),
20 DMA queue-overrun events remained near the beginning of the ten-minute
HE-AACv2 run. This experiment lets the existing compressed-input queue fill
before starting a new decoder, without allocating another audio buffer.

`CONFIG_YORADIO_INPUT_PREFILL_MS` is an experimental build option, default
**0** (disabled). `sdkconfig.input-prefill.defaults` selects **500 ms** for
the laboratory candidate. The decoder retains its first input packet and
waits until the queue cannot hold another full packet, the configured time
expires, or Stop/new Play changes the stream generation. Queue fullness uses
the actual adaptive capacity, including a TLS-reduced pool. Polling sleeps
for 10 ms, rounded to at least one RTOS tick.

This is a startup wait, not a delay per packet and not a guarantee of 500 ms
of buffered audio. Queue capacity, compressed bitrate and packet sizes affect
the amount accumulated. A short file may incur the full startup wait. The
nominal deadline is checked on task wakeup; scheduling can add a small delay.
The sustained HE-AACv2 trial records **509 ms**, ending by deadline rather
than a full queue. No new allocation or payload copy is introduced.

## Build and host checks

The candidate differs from the preceding fractional-clock laboratory image
only by `CONFIG_YORADIO_INPUT_PREFILL_MS=500`. It retains full compact
AAC/SBR/PS, original source rates, the existing dynamic TLS RX reserve and
adaptive input queue, QIO at 80 MHz, output/decode priorities 8/7, and the
same diagnostics. Fractional clock mode remains a laboratory option.

- 18 host cases execute the actual prefill function under ASan/UBSan:
  full queue, sparse input, deadline, cancellation, generation wrap, coarse
  RTOS ticks, and a TLS-reduced two-slot pool. Both adaptive and legacy-ring
  branches pass. These tests do not execute the complete decoder task.
- Linked AAC/SBR/PS and HTTP length-guard audits pass. The inactive unrelated
  CLZ benchmark is absent from the compiled image.
- Linked RAM sizes match the control: IRAM text 47,690 B, DRAM data 12,856 B,
  DRAM BSS 45,664 B. Application size grows from 1,619,328 to 1,619,760 B.
- Setup readback confirms the fractional divider for nominal 48,000 Hz and
  actual QIO 80 MHz operation. Four mapped application CRC32 checks match.

Firmware: `firmware/development/esp32c3-idf-6.1-r9a97-input-prefill500/app.bin`.
Version `idf61-prefill500`; app SHA-256
`44dc8d2d6f20aec49ec7a336211b9db876df3c72af1eaa6cfc1e4d2382159252`;
ELF SHA-256 `c3ca0caf7f9c780927093bc15b709adb8947e3b93287f4c06f9b108b210f4b9a`.
The exact IDF revision is `9a97f6c54ec638111ce55cd36581b3c192f15207`.

## Ten-minute HE-AACv2 HTTPS comparison

Both runs use the same 44.1 kHz stereo fixture, real-time 1.00x delivery,
concurrent WebUI polling, and settled idle measurements. These are sequential
trials with different binary layouts and radio conditions, not repeated
randomized measurements. No CPU-budget rejection threshold is applied.

| Measurement | Fractional clock, no prefill | Fractional clock, prefill 500 ms |
| --- | ---: | ---: |
| Original playback/heap gates | PASS | PASS |
| Strict CPU/decoder/heap/DMA telemetry | Complete | Complete |
| DMA queue-overrun delta | 20 | 0 |
| DMA write errors | 0 | 0 |
| DMA measurement interval | 585.969 s | 585.984 s |
| Total CPU busy, time-weighted | 62.083% | 61.088% |
| Minimum free heap | 24,920 B | 24,888 B |
| First / last three-sample median heap | 26,024 / 26,076 B | 25,996 / 26,044 B |
| Minimum largest free block | 14,336 B | 17,408 B |
| Settled idle heap before / after | 133,060 / 133,096 B | 133,086 / 133,124 B |
| Settled idle largest block before / after | 102,400 / 102,400 B | 106,496 / 106,496 B |
| Median RSSI | -66 dBm | -67 dBm |
| Maximum observed status-request latency | 438 ms | 1,093 ms |

The candidate passes the full requested 600-second playback observation and
the original recovery checks. Its complete selected DMA interval records no
queue overruns or write errors. Written PCM duration / wall duration is
1.0000364; decoded duration / wall duration is 0.9999710. Counter boundaries
exclude startup and short edge intervals; no zero-event claim is extrapolated
to those unmeasured intervals.

The result supports initial buffering as a useful follow-up to clock accuracy.
It does not establish causality from one pair or demonstrate an audible
improvement. The higher largest-block measurement is an observed allocation
layout result, not a new RAM saving. The larger maximum WebUI request latency
also remains in the record.

The separate HE-AACv2 network heap/receive correlation is **unavailable**:
its paired snapshot sequence is nonconsecutive. This gap remains rejected in
the saved analysis. The intact CPU/decoder/DMA series and original playback
and heap gates do not repair it or establish ownership of network allocations.

## Other physical checks

The finite-file matrix passes **44/44**: 11 retained fixtures, HTTP and HTTPS,
automatic detection and an explicit codec hint. It covers MP3, FLAC, Vorbis,
Opus, AAC-LC, HE-AAC and HE-AACv2, including mono and source-rate variants.
All 44 prefill events end on a full queue after 9–21 ms. Playback metadata,
status-level EOF and the original runtime checks pass.

The high-bitrate 48 kHz stereo FLAC fixture also passes **180 seconds** of
HTTPS playback with concurrent WebUI load and settled idle checks. The
610-second source file is streamed unpaced with TCP backpressure, matching
the preceding heavy-FLAC procedure; only the first 180 seconds are observed.
Its prefill ends after 20 ms on a full queue.

| Heavy-FLAC measurement | Result |
| --- | ---: |
| Original playback/heap gates | PASS |
| Strict CPU/decoder/heap/DMA telemetry | Complete |
| Selected DMA measurement interval | 165.125 s |
| DMA queue-overrun delta / write errors | 0 / 0 |
| Total CPU busy, time-weighted | 79.362% |
| Minimum free heap / largest block | 57,136 / 34,816 B |
| First / last three-sample median heap | 59,324 / 59,324 B |
| Settled idle heap before / after | 133,124 / 133,124 B |
| Median RSSI | -63 dBm |

Both in-stream AAC transition sequences, Stop/Play generation handling,
network drop/stall/error recovery, redirects, jitter and WebSocket reconnect
pass. Three mixed-codec cycles complete **12 station changes**, with settled
heap recovery. The five phase reports contain **65/65 passing entries**,
including idle baselines, recovery and runner cleanup entries. This total
must not be described as 65 different audio-format cases.

App-only OTA then restores production `idf61-qio80-8c1f2d2d`, app SHA-256
`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
The expected ELF identity, three playing-state observations and unchanged
Wi-Fi, playlist and settings are verified. No bootloader/NVS/SPIFFS rewrite
is used. These two successful application updates do not replace the full
OTA fault-injection suite. Production defaults remain unchanged.

The independent [staged PCM tail audit](ESP32C3_PCM_TAIL_AUDIT_20261009.md)
identifies a software EOF/same-rate-switch issue. The prefill candidate does
not include that repair. Status-level EOF checks alone therefore do not prove
that the final partial PCM block reaches the output.

## Reproduction

Run the host prefill cases without contacting the board:

```powershell
python tests/run-input-prefill.py --output .build/input-prefill-host
```

Windows requires GCC in WSL; Linux uses native GCC. The output directory must
be new. Physical testing requires a reachable board and a current trusted
laboratory TLS certificate. Private settings and TLS keys must not be archived.

Listening and analog noise measurements are unavailable. The exact-clock
option must stay disabled in production until its sound/noise tradeoff has
been checked; these diagnostics do not measure analog SNR or THD+N.

The [evidence archive](../tests/results/esp32c3-input-prefill-20261009/)
preserves original reports and filtered journals, source overlays, host tests,
build/linked audits, clock readback, restoration and a byte-exact SHA-256
index. Replay the saved analysis without contacting the board:

```powershell
python tests/results/esp32c3-input-prefill-20261009/summarize.py --output .build/input-prefill-replay/summary.json
python tests/results/esp32c3-input-prefill-20261009/verify_evidence.py --summary .build/input-prefill-replay/summary.json --output .build/input-prefill-replay/verified.json
```

Keep the rejected HE-AACv2 network-correlation sequence and all earlier
control failures. Before promoting this combination, repair the staged PCM
boundary issue, qualify the final production configuration, repeat continuity
checks under other delivery conditions, and assess fractional-clock noise.
