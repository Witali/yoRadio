# Opus: allocate large DRAM blocks before the demux workspace

2026-09-17. Completed negative memory experiment; both runtime changes
reverted after physical tests. Not a decoder speed improvement.

The accepted ASM exp2-table32 raw median is 79.626521% CPU192. Its live
test failed: the later scratch allocation requested 6144 B with a largest
free chunk of 5076 B. This does not prove a leak or identify the cause of
the preceding network timeout. See
[the original evidence](ESP8266_OPUS_WORD_LOAD_BOARD_20260917.md).

The first candidate made `opus_allocate()` obtain state/scratch before the smaller
`OpusWorkspace`. Input/PCM allocations, native initialization, buffer sizes,
16-KiB IRAM arena, same-codec allocation-free reset and 4096-B reserve are
unchanged. Before workspace allocation succeeds the local pointers own the
two blocks. Each failure frees exactly the blocks it owns; after ownership
transfer the existing `opus_free()` handles destruction. No allocation is
added to frame decoding, no PCM/Opus arithmetic is changed.

The second candidate split allocation from initialization and reserved the
large blocks before input/PCM buffers as well. It reached the reserve check
but did not leave enough free heap. Neither change is retained in runtime
source: a synthetic first-fit success is not sufficient device evidence.
Normalized source snapshots and experimental lifecycle tests are archived.

## Checks

- [x] Real bridge/arena, all allocation-site faults, all codec switches,
  same-codec resets and reserve failures: 19 related tests PASS, 0 skipped.
- [x] A bounded first-fit model has one state+scratch-sized chunk and
  smaller fragments. Old order fails at scratch; new order fits exactly
  the same allocation sizes and returns every allocation after ten cycles.
  This is a synthetic model, not a reproduction of the measured heap map.
- [x] Test configurations include input1024/1536/2048, scratch6144/7680,
  diagnostics on/off, PCM queue and Opus disabled. The adapter is stubbed
  only in these lifecycle tests; they are not new decoder PCM golden tests.
- [x] Matched physical control/two-candidate runs, ten each, with
  state/scratch/reserve failure snapshots, heap and continuity evidence.
- [x] Reject allocation-order-only changes as a live-radio fix; restore
  original runtime code and re-run19 lifecycle/reconnect tests (all PASS).
- [ ] Before further live changes, measure TCP/pbuf and decoder live memory
  together and recover real DRAM, keeping the4096-B reserve and full scratch.
  Do not blindly repeat ordering changes or reduce guards to hide the error.
- [ ] Reintegrate the accepted ASM chain with any future useful live fix
  without losing its fixed-layout patches. C tests do not qualify ASM timing.

## Physical results

CPU160/QIO40, C backend, no raw benchmark/runtime stats, input1024,
scratch6144, I2S PDM32 GPIO3,2x512 DMA, idle timeout3000ms, LED10Hz.
Same saved60s noise+tones Opus192 stereo48k/20ms LAN fixture as the prior
ASM live test. Ten sequential starts per image,25s observation windows,
unchanged strict continuity criteria. Every HTTP timeout is retained.

| Observation | Original control | Large blocks before demux | Large blocks before all I/O |
|---|---:|---:|---:|
| Qualified uninterrupted windows |0/10|0/10|0/10|
| Initial status reports playing |2|1|1|
| Final init snapshot: scratch failure (stage8) |8|9|0|
| Final init snapshot: reserve failure (stage10) |0|0|9|
| Largest chunk at scratch failure, B |4192..5992|5712|n/a|
| DRAM free at reserve failure, B |n/a|n/a|3308..4020|
| Lifetime heap minimum observed, B |3748|3544|3132|
| Audio stack watermark observed, B |1464|1464|1464|

Initial status and final diagnostic are at different moments: these are
snapshots, not counts of all internal reconnects. Stopped neutral DMA
underrun counters must NOT be interpreted as active-audio drop rates.
The control's valid second window delivered13.9335s PCM in30.404s board
time (ratio0.45828); that is not a20s continuous pass or a CPU measurement.

All three images have identical allocated sections/relocations across115
Opus library objects and identical static RAM/IRAM sizes. The early variant
adds16B to the cold `helix_codec_create` frame (64->80), while the allocated
audio task stack is unchanged; workspace/init frames are64/96B. The first
candidate keeps the original64/96B create/allocator frames. App sizes:
885552 /885568 /885680B. Library archive hashes differ due to non-runtime
metadata; the compared runtime sections and their relocations are exact.

App identities (SHA256):

- Control:`b6aa35a66961fbb1972f3daf3ba2ecc6a55f6f89a24596399776695eeaf219b8`
- Before demux:`a1a23544f4ef4aaf8ba3e8694722406ab854915a513bab7f6b685b7cfdf62ce8`
- Before I/O:`719499c77f27642a544907a5b69dcd14d594ff95679ae2c8724a37ef9f509f6c`

These builds used temporary source states; manifest `source_revision`
alone does not identify them. Per-build bridge hashes, normalized source
snapshots, image hashes, layout/disassembly and full runs are retained under
`firmware/development/esp8266-opus-early-reserve-c-20260917/`.
`report_large_first.cjs` independently recomputes each window and refuses
dropped attempts or falsely qualified results. Results do not demonstrate
a heap leak, identify the initial timeout cause, or solve the live target.

Recovery: prior C diagnostic-radio app SHA661becd3... restored by OTA to
0x110000; stopped station167, volume100, balance0 and playlist SHA79b401c4...
unchanged. HTTP root200/gzip27249B in102.49ms, WebSocket getindex works,
RSSI-58dBm/free heap27628B. This is a stopped API/HTTP check, not a visual
browser or continuous-playing WebUI qualification. No serial reset or PC
Wi-Fi changes were used; the owned LAN fixture server was stopped.

The frozen raw artifacts and production defaults are not rebuilt or
relabeled by this change. Do not shrink scratch or lower the reserve to
make an allocation test pass.
