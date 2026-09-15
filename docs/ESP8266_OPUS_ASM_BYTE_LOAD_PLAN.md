# Next Opus ASM experiment: narrow flash-byte access

2026-09-15. [Narrow candidate accepted experimentally](ESP8266_OPUS_ASM_PVQ_BYTE_WORD.md)
after30 physical A/B/A and exact PCM; CPU19284.01121%.
Updated after the third experiment: accepted pvq-row-word82.00615% is the
control for future comparisons; earlier results below retain their history.
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
- [x] Extend the host model and actual-linked tests, then10 A/10 B/10 A
  against accepted pvq-byte-word. Preserve exact PCM through510kbps/120ms,
  all errors/maxima, stack and RAM. The extra live instructions can affect
  flash/cache even though total image size is unchanged.

[Candidate implemented and locally verified](ESP8266_OPUS_ASM_PVQ_A4_WORD.md):
three patch ranges, unchanged image903216 B/static RAM/frame. Actual linked
378304 search and79902 split-threshold cases, plus24 exact host scenarios.
Physical30 A/B/A completed: CPU19284.00988 /82.83819 /84.02250%, both gates
PASS. Exact PCM/static RAM/frame preserved, all observations retained,
ordinary restored OTA. Accepted experimentally;80%/live qualification pending.

## Next independent candidate: row length cache[0]

- [x] Count actual quant_partition entries/row-length loads on the audio
  corpus. Do not reuse only no-split or LM!=-1 counts for this unconditional
  target read at0x4024db47: L8UI a6,a2,0.
  [Host census completed](ESP8266_OPUS_PVQ_ROW_WORD_PROFILE.md):3026 reads
  per0.24s at192,12608.33/s.10 exact PCM files through510, state/scratch/
  guards unchanged; counts independently agree with earlier upper probes.
- [x] Prototype an a2-input/a6-output word leaf. Preserve a2 and every other
  live register/SAR, use only proven dead scratch, no stack/table/RAM growth.
  The original return is already saved at sp+108 before this site.
- [x] Locate and prove a new encoder-only slot: the original private-contract
  audit finds candidate spans0x4024dc95..0x4024ddd9 and0x4024e3e8..0x4024e433,
  outside existing helpers. Size alone is insufficient: verify all incoming
  branches, alignment and fallthroughs, preserve every outside byte/address.
- [x] Prove complete static-table bounds, exact PCM/state/split behavior,
  then10 A/10 B/10 A against accepted a4-word with all errors/maxima/RAM.

Important for liveness audits: private internal leaf CALL0 sites do not have
the full generic C call-clobber set. Current proofs use only a0/a11, which
these helpers actually overwrite. Do not infer that a8/a9 are dead merely
because deadReg stops at a CALL0; model each internal helper's real clobbers
before using any other scratch register.

[Row-length candidate built and locally verified](ESP8266_OPUS_ASM_PVQ_ROW_WORD.md):
27-byte encoder-only slot,25 live helper bytes; source a2 preserved, a6 result,
SAR/a0/a11 proven.185168 linked numeric cases and24 host scenarios exact.
Image903216 B, outside bytes/addresses/table/RAM/frame unchanged. Physical
30 A/B/A completed:19282.82325 /82.00615 /82.84056%,both gates PASS.
Accepted experimental control82.00615%;80% and live qualification pending.
All attempts retained, including two A2 observation timeouts,minDRAM800 B.

## Follow-up inventory after row-length implementation

Read-only linked inspection2026-09-15 found two remaining endpoint-cost
reads in quant_partition:0x4024e21f L8UI a10,a9,0 (upper),0x4024e22a
L8UI a11,a11,0 (lower when low index is nonzero). These are the original
endpoint reads, not the duplicate selected-cost read already removed.

- [x] Count each endpoint read on the same host corpus; do not assume the
  lower read always executes or equate source counters with measured target
  instruction timing. Check ownership/address provenance and full word bounds.
  [Completed host census](ESP8266_OPUS_PVQ_ENDPOINT_WORD_PROFILE.md):at192,
  1765 upper+1647 lower reads per0.24s,14216.67/s;10 files exact PCM/state/
  scratch/guards, matching independent first-search counts. Not target timing.
- [x] Try independent narrow word extraction. At the upper continuation
  a0/a11 are dead; at the lower continuation a0 is dead but a11 is the
  live result, not available as SAR scratch. Verify all actual private calls.
  For a single fixed continuation, a candidate may use a0 to save SAR and
  jump back directly rather than RET; prove recursion/return restoration,
  interrupt semantics and all live registers before using that pattern.
- [ ] Prove new encoder-only storage/entries and exact linked endpoint
  selection/cost/remaining_bits behavior, then host and10 A/10 B/10 A.
  Existing adjustment-loop read0x4024e258 is a separate candidate/census.

The index L16SI a2,a2,0 at0x4024db22 is another possible follow-up, but it
precedes the original saved return at0x4024db36. Blind CALL0 replacement
would lose that return. Read-only liveness with actual private clobbers
also finds a8/a10 live later at0x4024db88/0x4024db8a and a11 immediately
live at0x4024db39. Do not choose them as free scratch. A separate two-site
scheduling/return proof or save/restore is required, as is careful treatment
of the last halfword in the210-byte table (length not divisible by4).
None of these follow-up candidates is implemented or timed yet.

[Endpoint word candidate implemented and locally verified](ESP8266_OPUS_ASM_PVQ_ENDPOINT_WORD.md):
upper ADD destination changed to reuse the a10 leaf; lower fixed J fragment
preserves SAR via dead a0. Four patches56 bytes, same image903216 B and RAM/
IRAM/frame.50176 direct cases+378304 complete searches,804309 word loads exact;
24 host scenarios pass. Disconnected120 encoder-only instructions are still
in the ELF and independently proven dead; full outside-byte equality retained.
Physical10 A/10 B/10 A pending. Index/adjustment-loop candidates remain unbuilt.
