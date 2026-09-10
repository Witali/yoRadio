# Opus: live stage attribution, 2026-09-10

Continuous playback is **not qualified**. These are diagnostic experiments,
not production defaults and not an assertion that HTTPS/Opus radio works.

## Measurement

`-Diagnostic -EnableOpus -OpusStreamTest` adds 64 bytes of DRAM counters,
no allocation/task/ISR changes. `GET /api/native/audio?stages=1` exposes four
cumulative rows: read/refill, decode/demux excluding nested PCM output,
PCM output including DMA wait, and the normal post-frame/empty-input wait.
Each row is `[total_us, maximum_us_since_boot, calls, DMA_misses]`.
Counters wrap modulo 2^32. Compare intervals shorter than 71 minutes,
without reset or generation changes. The saved runner restricts them further.
Opening, closing, prefill waits and other uninstrumented work are not attributed.
A DMA miss is an event, **not a precise measurement of silence duration**.

This is wall time, including Wi-Fi/RTOS preemption. It is not pure CPU usage.
`decode` includes Ogg parsing and callbacks outside the nested output span;
its call count also includes incomplete input, not just successful packets.
Output includes normalization, PDM generation and blocking for DMA capacity.

`run_stage_wall.cjs` makes two sparse snapshots separated by 27 seconds.
Each snapshot makes successive health/profile requests; these are not atomic.
Observed request pairs sometimes took 1–4 seconds, so an approximate residual
miss count can be negative. Do not use it as an exact causal partition.
Stage deltas use the profile's own clock; the strict continuity gate uses
health's own clock and counters. Maxima are since boot, not interval maxima.
Two initial SILK OFF runs overlapped in host time; they are not independent
replicates. Every timeout/failed measurement remains in the archive.

Reproduce after explicitly starting a diagnostic stream:

```powershell
node tools/esp8266_opus_profile/run_stage_wall.cjs --seconds 25 --output .build/opus-stage.json
```

The same zero-DMA-miss, >=20-second physical PCM progress gate remains enabled.
No accepted test may substitute a Playing flag or decode-only output for DMA.

## Selected observations, not cherry-picked acceptance results

CPU160/QIO40, fixed-point Opus, mono PCM48k, GPIO3 standard PDM32,
two 512-word DMA buffers; WordASM, PDM32 IRAM/batch ON. Input1024,
scratch6144. The source is our own tone/noise, not a remote station recording.

| Profile / own stream | Board ms | PCM ms | Added DMA misses | Min sampled free heap |
|---|---:|---:|---:|---:|
| ICDF OFF / SILK12 #1 | 28015 | 28050.67 | 68 | 6676 |
| ICDF OFF / SILK12 #2 | 28229 | 28260 | 61 | 6684 |
| ICDF OFF / CELT64 #1 | 28223 | 26820 | 1143 | 6528 |
| ICDF ON / SILK12 #1, reconnect | 28752 | 22353.5 | 889 | 6604 |
| ICDF ON / SILK12 #2 | 28223 | 28300 | 28 | 7256 |
| ICDF ON / CELT64 retry #2, reconnect | 31002 | 24073.5 | 1506 | 6484 |

All rows fail continuity. CELT OFF #2 and ICDF ON CELT retry #1 also have
missing HTTP samples. ICDF ON CELT initial attempts never started decoding;
later runs again hit TCP timeouts. They cannot establish a CELT speed gain.

Steady SILK OFF: read ~2.64%, decode ~65.2%, output+DMA wait ~29.3%,
post-frame wait ~2.6% of elapsed time. Steady SILK ON: 2.64%, 64.67%,
29.83%, 2.67%. This modest live difference does not prove gap-free playback.
The decoder-only ICDF comparison already showed 1.09–4.54% acceleration
with exact PCM fingerprints; see ESP8266_OPUS_FIXED_POINT.md.

CELT OFF: read 3.83%, decode 78.55%, output 14.18%, wait 3.10%, but PCM
covered only 95.0% of elapsed time. Misses occur primarily in decode/output,
even in an interval with no latched transport failure. Decode wall maxima
reached 30.5 ms on SILK and 46.9 ms after CELT. This points to deadline
headroom, not merely average throughput or an extra one-tick frame sleep.

The earlier DMA-aware sleep experiment was removed after no demonstrated
improvement: see ESP8266_OPUS_DMA_YIELD_EXPERIMENT.md.

## Memory and startup failure

The profiling image is 884816 bytes; ICDF ON adds 48 bytes. DRAM BSS rises
from 0x4808 to 0x4848 (exactly64 bytes); IRAM sections do not change.
The DMA ISR remains identical: 387 bytes, 151 instructions.
Measured audio stack watermark: 1704/5120 free on SILK, 1624/5120 on CELT.
Sampled free IRAM can fall to36 bytes during network activity; no extra
IRAM function is safe to add on these observations alone.

A CELT startup failed at stage8 (scratch allocation/reserve guard):
free DRAM9980, requested6144, reserve4096. This is 260 bytes short of the
guard, not evidence of a leak or slow arithmetic. After cleanup current DRAM
was27164. A later explicit retry started. The 4096-byte reserve was NOT lowered.

Post-OTA health reported reset_reason7; no additional uptime/generation
reset occurred in the valid windows. This does not identify the exact reset
moment or prove a decoder watchdog bug. SDK RX error counters do not observe
all radio/closed-driver losses, so zero counters cannot exonerate the network.

## Fixtures and artifacts

Archived profiles: `firmware/development/esp8266-opus-stage-wall/` and
`firmware/development/esp8266-opus-stage-wall-icdf/` (manifests pin sources).
All raw JSON observations and OTA reports accompany the corresponding image.
Files in `tools/esp8266_opus_profile/live-fixtures/` preserve the exact HTTP
bodies used here. Both are180-second finite files. Serve `/test.opus` through
`serve_fixture.cjs`; the ESP reconnects on natural EOF, so exclude crossing
that boundary from unexplained-stall attribution, not from failure recording.

SILK is a loop/re-encode of `tests/fixtures/opus_native/mono-12.opus`:
FFmpeg `-stream_loop -1`, `-t 180 -ar 48000 -ac 1 -c:a libopus -b:a 12k
-vbr off -frame_duration 20 -application voip`.
CELT uses FFmpeg8.1.1 lavfi stereo tones997/10007Hz and1703Hz plus seeded
white noise7349, 48k, 180seconds, libopus64k, CBR20ms, applicationaudio.
Ogg serials can differ on regeneration; use the archived bytes for exact A/B.

| File | Bytes | SHA256 |
|---|---:|---|
| silk12.opus | 284055 | 807878b973cbe75f518338d5afacb3fcf5c168999bee6420c7813df42b3002aa |
| celt64.opus | 1454185 | 7c74081965bc8dc3f17433870b1c0aee0e8dd5c6dd16cede6b6da1cf1a89cbfb |

## Next checks

- [x] Separate refill, decode/demux, nested output and task waits without ISR growth.
- [x] Preserve failed samples and use the existing strict continuity gate.
- [x] Measure full-path stack headroom for SILK and CELT (not a worst-case proof).
- [ ] Qualify a stable, repeated live ICDF A/B; current reconnects prevent this.
- [ ] Measure shortened PDM publication loans without changing 2x512-word DMA capacity.
- [ ] Test the **full** decode→PDM→DMA path from flash, not just the existing
  raw RAM packet decoder benchmark. Include deterministic tone/noise PCM checks.
- [ ] Separate PDM compute from its DMA wait, and record deadline-tail distribution.
- [ ] Reproduce transient startup memory pressure without weakening the reserve.
- [ ] Finish real HTTP Opus station playback >=20seconds without misses,
  then a longer soak with WebUI; only then change production defaults.
