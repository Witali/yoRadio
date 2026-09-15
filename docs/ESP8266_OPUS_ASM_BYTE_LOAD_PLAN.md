# Next Opus ASM experiment: narrow flash-byte access

2026-09-15. [Narrow candidate accepted experimentally](ESP8266_OPUS_ASM_PVQ_BYTE_WORD.md)
after30 physical A/B/A and exact PCM; CPU19284.01121%.
Control for the next experiment: accepted pvq-byte-word, not endpoint-cost.
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
- [x] Inventory eligible static table loads and their dynamic frequency;
  choose a small homogeneous set before changing every access.
- [x] Prototype one word-extract sequence for the same source/destination
  register, preserving byte value, SAR and all live registers. Consider
  save-SAR/SSA8L/align/L32I/SRL/EXTUI/restore-SAR, not an unaligned L32I.
  Do not assume a spare register or free SAR at the insertion point.
- [x] If a3-byte CALL0 replaces L8UI, prove a0 lifetime across all caller
  continuations, original return restoration and helper ABI. Helper storage
  may use only independently proven unused decoder-inaccessible code slots,
  excluding the sixth-probe stub already occupying0x4024e27b..0x4024e297.
  No new task stack or persistent RAM. A leaf helper is only a candidate:
  call/return overhead and flash placement must be measured.
- [x] Prove each aligned word lies within the complete readable static table
  storage, not merely that the byte was valid. Account for row offsets,
  last byte, endianness and arrays requiring padding. Keep dynamic RAM/MMIO
  and unsupported/custom-mode accesses unchanged.
- [x] Verify assembled instructions and all outside bytes/addresses, exact
  PCM/state/PLC/reset/OOM through510kbps and compound120ms packets, plus
  negative ABI/SAR/boundary tests. Keep original C and GCC ASM snapshots.
- [x] Compare against accepted endpoint-cost with10 A/10 B/10 A at160/QIO40.
  All raw packets preloaded in RAM; no output/profiling; retain all errors,
  maxima, RAM and low-bitrate cases. A local load microbenchmark cannot
  substitute for this whole-decoder comparison.
- [x] Keep only a demonstrated high-bitrate gain without RAM growth.
  Both controls confirm192 gain2.22% and128 gain1.66–1.68%; mono12 loss
  0.065–0.080%. Static RAM/IRAM/frame unchanged; every observation retained.
- [ ] Reach80% raw CPU and qualify20seconds live I2S/WebUI separately.

This can avoid exception overhead, but the previous negative word-access
experiments make it a hypothesis requiring an isolated test, not a guaranteed
speed improvement. Do not infer cache misses or exact instruction timings.

## Next independent candidate: two a4 byte probes

Read-only inventory of the accepted linked image found two same-register
L8UI a4,a4,0 sites:0x4024db52 (upper cost before split decision) and
0x4024e1ad (first binary-search probe). Current deadReg traversal proves
a0/a11 dead after both instructions; this alone is not a complete proof
of a new helper or a measured speedup.

- [x] Count each selected load on the actual audio corpus. The existing
  search census gives1765 first probes per0.24s at192, but does not count
  every pre-split upper-cost read; do not extrapolate that count blindly.
  [Completed census](ESP8266_OPUS_PVQ_A4_WORD_PROFILE.md):1765 first probes
  and2596 upper reads per0.24s at192,18170.83/s total.10 exact PCM files
  through510, unchanged scratch/state/guards, ASan/UBSan and3 regressions PASS.
- [x] Prototype an a4-input/output leaf with saved/restored SAR and dead a11,
  retaining a0 return correctness. A possible25-byte slot is0x4024de08:
  inside the old helper's32-byte unreachable padding, aligned4. Prove no
  branch/fallthrough/external entry reaches it, no overlap with the first
  helper or sixth-probe stub, and preserve every outside byte/address.
- [x] Prove static-table provenance and complete aligned-word bounds at
  both sites, all byte phases/SAR/live registers, split/no-split paths and
  recursive decoder calls. Inherit the prior verified private encode=0
  contract explicitly; do not treat arbitrary unreachable code as free.
- [ ] Extend the host model and actual-linked tests, then10 A/10 B/10 A
  against accepted pvq-byte-word. Preserve exact PCM through510kbps/120ms,
  all errors/maxima, stack and RAM. The extra live instructions can affect
  flash/cache even though total image size is unchanged.

[Candidate implemented and locally verified](ESP8266_OPUS_ASM_PVQ_A4_WORD.md):
three patch ranges, unchanged image903216 B/static RAM/frame. Actual linked
378304 search and79902 split-threshold cases, plus24 exact host scenarios.
The candidate has not yet been flashed; physical comparison is pending.
