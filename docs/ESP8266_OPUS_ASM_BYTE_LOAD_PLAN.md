# Next Opus ASM experiment: narrow flash-byte access

2026-09-15. Hypothesis, not implemented or physically measured.
Control for future comparisons: accepted endpoint-cost, CPU19285.96527%.
No firmware default, CPU/flash clock or RAM budget change.

## Verified premise and prior failures

The actual SDK source components/freertos/port/esp8266/xtensa_vectors.S,
LoadStoreErrorHandler (around line150), explicitly emulates L8/L16 reads
from instruction address space using an aligned word read. Its path saves
registers/SAR, inspects the faulting opcode and restores the target register.
a5..a15 additionally use a jump table. Therefore an L8UI to a static mapped
flash table is not necessarily a cheap single-cycle load.

SDK repository commit89a3f254b63819035f65d9c5dcdae8864f1a6a8a;
local xtensa_vectors.S raw SHA256:
06a2952513565e2b5edf5dffc03c1852aec3610aa3e0df675f38884a2b712791.
Source inspected at:
C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk.

Accepted linked quant_partition still uses L8UI in the binary search,
including0x4024e1c3 and0x4024e1d6 (a10 from address a10).
The current endpoint-cost experiment removed only a final duplicate load.
Its whole-decoder gain must not be converted into a measured per-load cost.

[Earlier pulse-cache word experiments](ESP8266_OPUS_PULSE_WORD_BENCHMARK.md)
9e40898/f20ed03 already changed index, bits and caps access through C helpers.
Both were rejected: extra720/912B flash and substantial regressions in
important modes. Do not resurrect that switch and call it a new experiment.
The new distinction must be a narrowly scoped saved-ASM replacement with
other linked addresses, tables and register pressure kept fixed.

## Checklist

- [x] Inspect the actual SDK exception handler and remaining linked loads.
- [ ] Inventory eligible static table loads and their dynamic frequency;
  choose a small homogeneous set before changing every access.
- [ ] Prototype one word-extract sequence for the same source/destination
  register, preserving byte value, SAR and all live registers. Consider
  save-SAR/SSA8L/align/L32I/SRL/EXTUI/restore-SAR, not an unaligned L32I.
  Do not assume a spare register or free SAR at the insertion point.
- [ ] If a3-byte CALL0 replaces L8UI, prove a0 lifetime across all caller
  continuations, original return restoration and helper ABI. Helper storage
  may use only independently proven unused decoder-inaccessible code slots,
  excluding the sixth-probe stub already occupying0x4024e27b..0x4024e297.
  No new task stack or persistent RAM. A leaf helper is only a candidate:
  call/return overhead and flash placement must be measured.
- [ ] Prove each aligned word lies within the complete readable static table
  storage, not merely that the byte was valid. Account for row offsets,
  last byte, endianness and arrays requiring padding. Keep dynamic RAM/MMIO
  and unsupported/custom-mode accesses unchanged.
- [ ] Verify assembled instructions and all outside bytes/addresses, exact
  PCM/state/PLC/reset/OOM through510kbps and compound120ms packets, plus
  negative ABI/SAR/boundary tests. Keep original C and GCC ASM snapshots.
- [ ] Compare against accepted endpoint-cost with10 A/10 B/10 A at160/QIO40.
  All raw packets preloaded in RAM; no output/profiling; retain all errors,
  maxima, RAM and low-bitrate cases. A local load microbenchmark cannot
  substitute for this whole-decoder comparison.
- [ ] Keep only a demonstrated high-bitrate gain without RAM growth.
  Then80% raw threshold and20seconds live I2S/WebUI remain separate gates.

This can avoid exception overhead, but the previous negative word-access
experiments make it a hypothesis requiring an isolated test, not a guaranteed
speed improvement. Do not infer cache misses or exact instruction timings.
