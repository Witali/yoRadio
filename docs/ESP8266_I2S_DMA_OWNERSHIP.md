# ESP8266 I2S PDM: explicit buffer ownership

Date: 2026-09-05. Wemos D1 mini, CPU 160 MHz, QIO 40 MHz, ordinary
first-order software delta-sigma PDM32 (not RCPDM), output GPIO3.
Nominal carrier 1.536 MHz; divider 8/13 gives 1,538,461 Hz.

## Fault and correction

The previous circular DMA chain revisited a buffer regardless of whether the
producer had completed it. EOF also cleared the just-read buffer and put it
back into the free queue even if the producer still held a partial write.
Consequences: missing prefixes, partial/stale blocks and simultaneous DMA/CPU
access. Increasing the buffer sizes alone would not fix ownership.

The producer and DMA now alternate two 512-word buffers (4096 payload bytes):

`FREE -> FILLING -> READY -> DMA -> FREE`

- `memcpy` writes only FILLING storage. Partial writes survive across calls.
- The producer publishes READY only after all 512 words and a memory barrier.
- Each SLC descriptor terminates with `next_link_ptr = NULL`. Hardware cannot
  prefetch the other, unfinished buffer. A software-ready flag on the old
  circular chain would NOT provide this protection.
- At EOF the memory read is complete. The ISR submits a READY buffer and
  wakes the blocked producer using the existing direct task notification.
  It does not reset I2S or its FIFO; final FIFO words cover handoff latency.
- If the other buffer is not ready, the completed DMA buffer is filled once
  with **audio zero: `0xAAAAAAAA` / `101010...`**, then reused for silence.
  This is 50% PDM density, not all-zero logic and not a repeated audio frame.
  The partially filled producer buffer is never cleared or submitted.
- Stop cancels partial/queued audio and requests neutral PDM at the next EOF.
  It never writes active DMA memory. The API has one producer; stop and write
  are serialized by the existing audio task, not called concurrently.
- A multi-buffer write uses one timeout budget, not a renewed full timeout
  for every acquired buffer.

The SDK I2S register setup and EOF mechanism were checked against the local
Espressif driver and the [ESP8266 Technical Reference, section 10](https://documentation.espressif.com/esp8266-technical_reference_en.html).
The finite-descriptor handoff is our implementation; its FIFO timing must be
verified on hardware, not inferred solely from the host ownership model.

## RAM and build checks

No additional task, payload buffer, allocator, or PCM copy was added.
Ordinary build `.dram0.data + .dram0.bss` is **20,840 bytes**, 8 fewer than the
previous ordinary build. The end of static IRAM remains **0x40106af8**.
Physical startup confirms `Reserved 16384+0-byte codec word arena (IRAM)`.

An early diagnostic prototype grew IRAM and caused the arena to fall back to
DRAM. It is NOT the final normal firmware. Redundant volatile byte accesses
and ISR masking calls were removed; state is protected by task critical
sections/ISR exclusion. Decoder, PDM, and ISR all remain compiled with -O3.
Profiling instrumentation itself can still change IRAM placement; always
check the startup arena line before comparing codec timings.

## Reproducible tests

1. `node --test tests/esp8266-nodac-buffer.test.js` compiles the production
   state machine as C. It interrupts each partial-copy word, delays publication,
   runs 2000 randomized blocks, checks every output word in sequence, verifies
   neutral underrun words, no stale replay, and stop/restart interleavings.
2. `node --test` runs the complete local regression suite: **331 passed,
   zero failures/skips**. The explicit neutral-word assertion was also rerun
   with the executable C test.
3. Build the tracked default configuration with
   `-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=ON`; keep tone/audio/memory profiles
   OFF. Capture TX only with `tools/monitor_esp8266.py`. GPIO3 is audio, so
   do not send application UART commands.
4. The isolated benchmark generates 48 kHz PCM, warms up 2 s, measures 10 s,
   then holds a partial DMA buffer for **65 ms** and compares its contents
   before completing it. It changes no persistent settings.
5. For optional live radio diagnostics use AUDIO_PROFILE with a 30 s report
   window and `tools/esp8266_audio_profile/dma_cases.cjs`. Supply the actual
   original station, volume and playing state; its finally block restores them.

Final isolated run on the physical board:

| Measurement | Result |
| --- | ---: |
| DMA completions in measurement | 941 |
| Producer underruns | 0 |
| Partial buffers blocked | 0 |
| I2S FIFO-empty flag observations | 0 |
| 65 ms delayed partial-buffer integrity | PASS |
| Output callbacks / measured wall time | 3764 / 10,007,925 us |
| Largest measured write | 9817 us |

Five short wall-time samples were rejected by the existing benchmark because
the SDK timer regressed; do not turn these wall-time totals into precise CPU
percentages. FIFO flags/counters and the byte comparison are separate checks.
No oscilloscope or acoustic recording was available: zero observed FIFO-empty
events is evidence for this test, not proof against every possible RF/ISR load.

## Live-radio limits

An early instrumented prototype started MP3 128 kbps and AAC about 318 kbps,
switched between them, and restored ROCK FM / volume 254 / stopped. Status
requests after starting took 50/52 ms; restoration check took 32 ms.

Its AAC 30 s window delivered only 16.137 s of audio (53.7% realtime), with
1309 producer underruns, 1307 blocked partial-buffer opportunities and zero
observed FIFO-empty flags. That prototype used DRAM codec fallback, so these
numbers must NOT be presented as a performance measurement of the final
IRAM-based build. They also demonstrate that correct DMA ownership alone
does not solve insufficient producer/network/decoder throughput. Such gaps
now contain neutral PDM; they are not corrupted partial frames.

Final ordinary firmware check (25 s per station): MP3 128 was playing with
12,484 bytes free heap and the intended 11,472 DRAM / 16,384 IRAM workspace.
AAC 320 decoded, but its stream ended/reconnected at the checkpoint
(`playing=false`, `connecting=true`). Thus stable AAC playback is **not passed**.
No PCM-write timeout or reset was seen in this capture. The original ROCK FM,
volume 254 and stopped state were restored; status responded in 24 ms with
24,252 bytes free, minimum 8,116. Wi-Fi RSSI ranged roughly -66 to -76 dBm.
The saved workload now explicitly fails a checkpoint that is reconnecting
instead of treating a successful HTTP status response as playback success.

Artifacts and raw captures are under `firmware/development/esp8266-native/`,
`firmware/development/esp8266-native-dma-benchmark/` and
`docs/benchmarks/esp8266-dma-2026-09-05/`.
