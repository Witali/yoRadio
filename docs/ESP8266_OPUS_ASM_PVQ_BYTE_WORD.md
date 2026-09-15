# Opus ASM: word extraction for five PVQ byte probes

2026-09-15. Experimental candidate over accepted endpoint-cost, not production.
Physical speed not yet established. CPU160, runtime QIO40; no RAM growth.

116 related preflight regressions PASS,0 failures/skips,103.42seconds.
preflight-tests.log and the generator/host/helper-test logs are retained
beside the candidate image. This is not the whole repository test suite.

## Why this differs from rejected pulse-cache helpers

The SDK LoadStoreErrorHandler emulates narrow reads from instruction space.
The old broad C pulse-cache changes9e40898/f20ed03 increased code size and
regressed important modes. They remain rejected. This variant leaves every
other linked instruction and every table at its original address, changes
only five homogeneous L8UI a10,a10,0 probes to CALL0, and uses existing
decoder-inaccessible bytes for a leaf helper. No new lookup table or flag in
the production profile. See [the hypothesis](ESP8266_OPUS_ASM_BYTE_LOAD_PLAN.md).

## Helper and ownership

Calls:0x4024e1c3,0x4024e1d6,0x4024e1ea,0x4024e204,0x4024e284.
The helper occupies0x4024ddec..0x4024de25:57 bytes previously proved
encoder-only under the inherited private encode=0 decoder contract.
It has25 live bytes/nine instructions and32 unreachable padding bytes.
The existing sixth-probe stub0x4024e27b..0x4024e297 is untouched.

From the saved fourth/fifth-step audio census at192kbps: three mandatory
probes x1765 calls,1000 fifth probes and221 sixth probes =6516 selected
loads per0.24seconds, or27150 per second of audio. These are logical
occurrences, not CPU cycles or a promised speedup; the uniform exhaustive
test distribution must not replace these corpus frequencies.

a10 is the byte address on entry and zero-extended byte on return.
a11 saves/restores SAR and is clobbered; CALL0 changes a0. Independent
all-successor liveness checks prove both dead at every caller continuation.
The original main-function return is still restored from its original stack;
the leaf adds no frame, stack write, allocation, table or persistent state.
All other registers, memory stores and caller branch paths stay identical.

The sequence saves SAR, uses SSA8L to select a byte, aligns the pointer,
reads one L32I word, shifts/masks the byte, restores SAR and returns.
Only immutable mapped-flash table data are selected; no MMIO/DMA access,
prefetch, table-end overread, bitrate cap or C fallback change.

## Local verification

- Actual linked table at0x402d57fc,392 bytes, aligned4; its contents match
  cache_bits50, and the static mode's +92 pointer matches that address.
- Symbolic proof covers all32 word bits, all four byte offsets and arbitrary
  SAR, not a handful of PCM values.
- The actual assembled helper and full search execute378304 standard
  row/budget cases, preserving logical read order, q/cost, live registers
  and SAR.1218362 aligned word loads stay inside the complete table.
- Original instruction count15984492 vs new26949750 excludes the old
  exception handler. More explicit instructions does NOT measure slowdown:
  target timing is still required.
-24 host PCM/state/PLC/reset/OOM cases exact under ASan/UBSan, including
  320/510kbps, phase variants and compound packets through120ms.
  The model executes word extraction and asserts complete-word boundaries.
- Four dedicated regressions pass, including invalid storage reachability,
  live a0/a11, wrong byte extraction, bad SAR restore and invalid alignment.

Two initial harness assumptions failed before any candidate OTA:
the expected display of RET.N was written RET, and the C insertion anchor
matched three identical comparisons. Both were corrected and the completed
checks rerun. Neither failure was a target decode failure or omitted trial.

app903216 bytes, static RAM/IRAM/frame/arenas unchanged; function frame112B.
Candidate SHA256:
a53e2684fbfbe7c52743c0fcb0ec50301b7d6106a4b055a8659d84ffe7817b05
Control is accepted endpoint-cost:
85af3677670a985918bb17affef136ed291f5bcd030494dba932fd378e752dbc

Recipe pvq_byte_word.cjs, commented ASM pvq_byte_word.s, proof
pvq_byte_word_proof.cjs. Original C/GCC snapshots unchanged.

## Physical protocol

10 A /10 B /10 A with the same packets preloaded in RAM, no audio output
or function/stage profiler. Preserve every attempt, maximum, memory minimum
and observation error. Compare both fresh controls at128/192 and lower
bitrates, then restore ordinary radio through OTA. No GPIO3/UART commands.

The80% raw CPU goal and20seconds continuous I2S PDM/WebUI remain unproven.
