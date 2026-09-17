# Opus: allocate large DRAM blocks before the demux workspace

2026-09-17. Memory reliability experiment; not a decoder speed improvement.

The accepted ASM exp2-table32 raw median is 79.626521% CPU192. Its live
test failed: the later scratch allocation requested 6144 B with a largest
free chunk of 5076 B. This does not prove a leak or identify the cause of
the preceding network timeout. See
[the original evidence](ESP8266_OPUS_WORD_LOAD_BOARD_20260917.md).

`opus_allocate()` now obtains decoder state and scratch before the smaller
`OpusWorkspace`. Input/PCM allocations, native initialization, buffer sizes,
16-KiB IRAM arena, same-codec allocation-free reset and 4096-B reserve are
unchanged. Before workspace allocation succeeds the local pointers own the
two blocks. Each failure frees exactly the blocks it owns; after ownership
transfer the existing `opus_free()` handles destruction. No allocation is
added to frame decoding, no PCM/Opus arithmetic is changed.

This reduces one source of fragmentation; it cannot guarantee allocation
for every fragmented heap. It also does not prevent Wi-Fi starvation or
make a synchronous decoder meet every DMA deadline.

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
- [ ] Matched physical control/candidate runs, at least ten each, with
  state/scratch/reserve failure snapshots, heap and continuity evidence.
- [ ] Reintegrate with the accepted ASM chain without silently losing its
  fixed-layout patches. A C-backend memory experiment cannot qualify the
  ASM CPU target or establish uninterrupted ASM I2S playback.

The frozen raw artifacts and production defaults are not rebuilt or
relabeled by this change. Do not shrink scratch or lower the reserve to
make an allocation test pass.
