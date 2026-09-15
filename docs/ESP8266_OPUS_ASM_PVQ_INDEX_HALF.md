# Opus ASM: phase-specialized signed index word extraction

2026-09-15. Independent experiment on accepted index-word80.08060% CPU192.
Host24 exact PCM scenarios and linked packaging complete; physical gate pending.
Current goal80% and20second continuous I2S/WebUI remain unqualified.

## Hypothesis and ABI

The index table contains int16, so the pointer has only two phases modulo4.
Test address bit1 with BBCI. For the upper half subtract2, load the aligned
word and arithmetic-shift16. For the lower half load, shift-left16 then
arithmetic-shift16. No variable shift, SAR save/restore or a0 scratch.
Each path executes five helper instructions versus ten in index-word v2.
This is an instruction count, NOT a measured timing advantage.

The helper occupies25 live bytes in the parent's proven29-byte slot.
Restore the original instruction order: the load redirect at0x4024db22
returns to0x4024db25; original return store stays at0x4024db36/sp+108.
Three patch ranges35 bytes, no new table, RAM, stack or allocations.
Original C fallback and GCC snapshots are retained unchanged.

The plan initially suggested rebuilding independently on endpoint-word.
Instead this reproducible overlay uses the now accepted immutable index-word
image as its direct control, restoring the same original load/store order.
Thus the board comparison measures improvement over80.08060%, not merely
over the older80.99456%. It never overwrites the previous candidate.

Preview confirmed BBCI support. ADDI.N does not encode-2, so use ordinary
ADDI (three bytes). Initial preview failure is retained, no failed app flashed.
A host registration edit exceeded Windows command length; the partial edit
was fixed with narrow patches and the failed host invocation was retained.

## Required validation

- [x] Host PCM/state/PLC/reset/OOM exact in24 cases, including320/510kbps,
  phase fixtures and120ms/48-frame compound packets, under ASan/UBSan.
- [x] Independently verify linked signed extraction for all65536 values,
  two phases and105 real indices; preserve all original GPRs/SAR/stack.
- [x] Authenticate parent's occupied helper, original dead-storage proof,
  last-word padding and complete table bounds; freeze all outside bytes.
- [x] Run positive and negative regressions; unchanged static RAM/frame.
- [ ] Physical10 A/10 B/10 A at160MHz/QIO40, RAM packets/no output/profiling.
  Preserve all attempts, errors, maxima, RAM and lower-rate regressions.
- [ ] Restore ordinary radio through OTA and verify station/playlist/HTTP/WS.
- [ ] Accept only measured speed without RAM growth, then qualify real audio.

Recipes:tools/esp8266_opus_asm/pvq_index_half.cjs and commented .s;
proof:pvq_index_half_proof.cjs. No default profile change.

Linked proof:131072 signed cases+6720 actual-table/SAR cases,137792 word
loads. Prefix instructions2618048->1929088:exactly five fewer per case,
excluding old exception costs. Three patch ranges/35 bytes; all outside
bytes/addresses,903216-byte image and static RAM/IRAM/frame unchanged.
Candidate SHA2560d76ec891f194e58e385339f1777e38c187b1bd0616a3c3bc8dfce91a033468e.
Control SHA25642f3b445aa7515c69cdcc1f563f9f177f7ed16b75bbabd4eb62358f0bbff5391.
Full160 related preflight regressions PASS/0skip,258.95seconds, log retained.
Fresh physical A/B/A is in progress; no speed conclusion yet.
