# ESP8266 playback continuity investigation, 2026-09-08

Status: standalone physical DMA progresses; continuous live radio and responsive
WebUI together have NOT passed acceptance. No analog recording was obtained.

## Historical RAM-source physical output (MP3 workload invalid)

Correction: inspection found that the old MP3 selector repeatedly decoded
the initial silent Info seek-table frame, not representative MP3 audio.
Retain its counters below as historical observations ONLY: they establish
DMA progress with generated silence, not music decoding capacity. Do not use
this MP3 row or older repeated-Info results as an MP3 speed/continuity claim.
The replacement sequential tone/noise benchmark skips metadata, checks
nonzero PCM, and reads complete files in order from internal flash.

Wemos D1 mini, CPU160/QIO40, Helix mono MP3 SSO/AAC, I2S PDM32 GPIO3,
two 512-word DMA buffers. Wi-Fi off, 1500 repetitions of an embedded frame
after warm-up. The physical-output benchmark includes DMA backpressure;
its elapsed time is NOT decoder CPU consumption.

| Codec | PCM duration | Measured wall | DMA EOF | Underruns | FIFO empty | Free heap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MP3 Info frame, INVALID audio workload | 36.000 s | 35.893457 s | 3375 | 0 | 0 | 81972 B |
| AAC, 320 kbit/s fixture | 32.000 s | 31.905115 s | 3000 | 0 | 0 | 83656 B |

Task stack margin was 1504 bytes. Fifty decoder lifecycle iterations returned
heap from 90508 to 90508 bytes. UART source: local diagnostic build
`.build/esp8266-continuity-ram/baseline.log`.

## Live network and timing observations

- AAC from Radio Caprice Celtic, HTTP port 8002, continued decoding for several
  minutes with output disabled. This initially also freed about 4.7 KiB because
  unused I2S code/state was discarded by the linker, so it was NOT a controlled
  proof against RAM pressure or DMA interaction.
- A subsequent control retained DMA and its memory, toggling only the GPIO3
  mux every 30 seconds. AAC reception continued in both mux states. This did
  not establish GPIO3 contention as the cause. The timed GPIO3 experiment was
  reverted. NoDAC now leaves unused BCK/WS pins alone; this change alone has
  NOT been demonstrated to cure Wi-Fi failures.
- With 22.05-kHz AAC and the 512-word output, typical five-second diagnostic
  windows delivered 95-96% of wall time as audio. Decode-core wall time was
  about 30-31%; gain/mix/PDM about 8%; waiting for DMA about 59%. These are
  elapsed stage times, can include preemption, and are not additive CPU loads.
  Full decode calls / PCM gaps sometimes exceeded 20-23 ms. Periodic UART
  profiling itself delays this same audio task; it is disabled for acceptance.
- A 25-second requested live MP3 128-kbit/s test produced 21.904 s PCM over
  27.391 s board time, with 3812 neutral underrun events: FAIL. HTTP requests
  ranged from about 18 to 261 ms in that sample; minimum sampled heap 9388 B.
- Both firmware startup and ongoing playback experienced Wi-Fi failures;
  RSSI varied roughly -65 to -89 dBm. Router reachability from the wired PC
  remained good. Network adapter configuration on the PC was not changed.
- One-second stream inactivity recovery was exercised and reopens streams,
  but also interrupts streams that merely deliver in bursts. A 3000-ms
  diagnostic override was used for comparison; the configurable source
  default remains 1000 ms as requested.
- A two-by-1023-word trial costs 4088 extra bytes compared with 512 words.
  It did not obtain a valid live continuity window: the connection stalled
  after the initial AAC PCM. It is NOT promoted to the default configuration.

## Why compressed input does not guarantee continuous PCM

The native build currently uses one audio task, not the optional KaRadio
producer task. It reads at most 1024 bytes into the 1536-byte codec input,
decodes complete available frames synchronously, and calls the PCM output
callback, which may wait for DMA. Afterward it returns to network reading.

At nominal 48-kHz output, one 512-word PDM32 buffer contains 10.667 ms.
Both buffers together hold at most 21.333 ms, but one is usually being played
and the other may be partially filled. The time before the next PCM callback
must be shorter than the remaining *ready* output, not the allocated capacity.
Enough average compute capacity is insufficient when a decode/interrupt/network
gap exceeds that deadline. Input occupancy was not measured in the failing
window, so a full compressed queue must not be assumed.

Next diagnostic: measure input occupancy, ready DMA words and the longest
PCM-production gap together without periodic audio-task printing. Separate
network starvation from a missed decoder/output deadline before changing
buffer sizes or adding a task. A larger input queue alone does not fix the latter.

See [stream recovery](ESP8266_STREAM_RECOVERY.md) for timeout and cancellation
semantics. `/api/native/audio` and the continuity script now reject decode-only
or non-progressing DMA runs instead of treating a Playing flag as proof of sound.
