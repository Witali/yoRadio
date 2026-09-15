# Opus ASM: word extraction for five PVQ byte probes

2026-09-15. Experimental candidate over accepted endpoint-cost, not production.
Physical gain confirmed by30 A/B/A. CPU160, runtime QIO40; no static RAM growth.

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

## Physical results

All30 attempts completed with exact PCM and no decoder/HTTP observation
errors. Median raw decoder CPU, percent; A/A2 are accepted endpoint-cost:

| kbps | A | B: byte-word | A2 | Maximum call A/B/A2, us |
|---|---:|---:|---:|---|
|12|23.08269|23.09767|23.07910|8625 /8310 /7875|
|24|54.24179|54.19331|54.24304|14581 /16054 /14562|
|64|64.10235|63.43875|64.01488|17057 /17118 /17257|
|128|75.70981|74.43904|75.69485|19277 /21842 /19288|
|192|85.91985|84.01121|85.91904|22101 /21428 /21069|

Both high-bitrate gates PASS:192 relative time gain2.22143% /2.22050%,
128 gain1.67848% /1.65905%, exceeding mono12 loss0.06489% /0.08043%.
Accepted as the new experimental raw baseline,84.01121%; default unchanged.
Another4.77461% reduction in current decoder time is needed to reach80%.
Candidate192 range83.95267..84.18454%, mean84.03786%.

Static RAM/IRAM/frame/arenas unchanged. Minimum observed free DRAM A/B/A2:
8860 /1252 /7492 B; minimum free stack1660 B in every group. B/run1 had
the1252 B minimum on12/24/64/128, retained without filtering. At192 the
minima are9800 /9800 /9808 B. Cleanup free DRAM minima26300 /26164 /26308 B.
These are observations, not new allocation sizes or a live-memory safety
claim. No OOM occurred; the cause of the low B/run1 memory is not established.

All maxima retained: B19221.428ms is lower than A but higher than A2;
B12821.842ms is worse than both controls. Average acceleration does not
establish a safe DMA deadline. Different accounting windows give task>wall
on mono12 A/run1 by478us, B/run3 by521us, A2/run9 by24us; retained, not
clamped or excluded. No timing measurement is replaced by an empty-loop
subtraction. See the archived comparison and all30 JSON/log pairs:
[comparison.json](../firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/comparison.json).

Final118 related regressions PASS,0 failures/skips,116.90seconds. The results
test independently recomputes every median, maximum, minimum and acceptance
gate from all30 archived attempts, rechecks the linked proof and validates
the ordinary restoration. final-tests.log retained beside the image.
This is the related Opus suite, not all repository tests.

## Restore and remaining qualification

Ordinary live512-idle3s C-backend radio restored OTA to0x10000, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
CPU160/QIO40, I2S PDM32/GPIO3,2x512 DMA; benchmark OFF. Stopped station167,
playlist hash, empty error, getindex and WebSocket playerwrap verified.
Root HTTP200:27249 gzip bytes in105.8124ms, heap27628/min24748, RSSI-62dBm.
This measures the root document, not full browser loading; playback was
not started in this restoration check. No UART/reset or SPIFFS upload.

The80% raw CPU goal and20seconds continuous I2S PDM/WebUI remain unproven.
