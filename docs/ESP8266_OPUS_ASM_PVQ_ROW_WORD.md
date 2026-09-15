# Opus ASM: PVQ row-length word load

2026-09-15. Experimental candidate on accepted a4-word82.83819% CPU192.
Default unchanged. This document separates correctness from board speed.

## Change and ABI

Replace L8UI a6,a2,0 at0x4024db47 with CALL0 to0x4024e3e8. The9-instruction
leaf saves SAR in a11, uses the low address bits for byte extraction, reads
one aligned word and restores SAR. Source a2 is preserved, a6 is unsigned
byte result. a0/a11 are dead at the caller continuation; the original
function return was already saved to sp+108.

Reuse27 bytes of original encoder-only instructions,25 live plus2 padding
after RET. The independently authenticated encode=0 CFG retains every
audio-dependent branch and proves this storage dead. Its only incoming
edge at0x4024dbd5 is also dead; no fallthrough or interior entry exists.
This is a decoder-only storage contract, not a bitrate restriction.
All outside bytes/addresses, tables,112-byte frame, DRAM/IRAM and image size
903216 B are unchanged. No new target table, allocation or task stack.

## Local evidence

- [Census](ESP8266_OPUS_PVQ_ROW_WORD_PROFILE.md):3026 reads/0.24s at192,
  12608.33 reads per second of audio; includes LM==-1.
- Symbolic verification covers all32 word bits,4 byte phases, arbitrary SAR,
  unchanged a2 and every register other than result a6/dead a11.
- Actual linked interpreter checks all392 table bytes times64 SAR values,
  plus160080 prefix cases:23 rows,580 budgets including signed extremes,
  LM=-1/0/3 and N=1/2/3/32. Both split and full search outcomes are retained.
  Total185168 new word reads; instruction counts exclude old exception
  handling and must not be interpreted as CPU time.
- Original mode/index pointers,392-byte bits storage and210-byte signed
  row-index table verified in the ELF, including complete word bounds.
- Parent proofs independently recheck the existing a4/a10 helpers and
  exhaustive search. Private CALL0 liveness uses only actual a0/a11 clobbers,
  not the larger generic C caller-scratch set.
-24 host PCM/state/PLC/reset/OOM cases exact under ASan/UBSan, including
  320/510kbps, all phase fixtures and120ms compound packets.

Recipes: pvq_row_word.cjs, commented pvq_row_word.s, pvq_row_word_proof.cjs.
Candidate SHA256:80c1faedc43b99bc78a90138f2bb11d1a9820b3def222c64064b4ec51e9731df.
Control SHA256:fe34751b8dae0cbd87a58a1b767aa02a82b006aa8b452f66065446dbc9dbdae9.
Artifacts are under firmware/development/esp8266-opus-pvq-row-word-{control,candidate}-v1.

## Required physical qualification

Full136 related preflight regressions PASS,0 failures/skips,162.29seconds.
preflight-tests.log is retained beside the candidate image.

Pending10 A/10 B/10 A at160MHz/QIO40, identical RAM-preloaded fixtures,
no network input/output/function or stage profiling. Retain every attempt,
error, maximum and minimum RAM, including low-rate regressions. Compare both
controls using the high-bitrate gate; then restore ordinary radio via OTA.
No UART/GPIO3 commands or reset. A host pass is not an LX106 speed result.

Current80% goal and>=20seconds uninterrupted I2S PDM with WebUI remain unproven.
