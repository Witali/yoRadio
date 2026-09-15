# Opus ASM: reuse both PVQ endpoint costs

2026-09-15. Experimental frozen-layout candidate over accepted bits-fourth.
Accepted experimental raw baseline after30 physical A/B/A runs.
Not production; continuous audio and the80% CPU target remain unqualified.

## Change and invariants

The nearest-endpoint tail has already loaded cache[hi] and (when lo!=0)
cache[lo]. Preserve their values in a10/a11 and publish the selected cost
directly to a8. For q=0 keep the original zero-cost exit. The later
remaining_bits loop still reloads the cost after decrementing q; it must
not reuse the cost of the previous q.

Eight point replacements,20 bytes total, preserve every instruction address
and width. Branches and their execution order are unchanged. Two register
self-copies intentionally retain the original slots. The instruction count
does not decrease: one duplicate L8UI becomes a register operation on each
nonzero-q outcome. This is not a claimed cycle saving.

The linked CFG proves a10/a11 dead until definition, call-clobber or return
at both continuation points. All other registers, q, cost, SAR, state stores,
stack frame and table layout stay unchanged. No RAM array or bitrate cap.
Inherited private decoder encode=0 contract is independently verified through
the accepted parent chain. Original C and GCC snapshots are not modified.

This differs from the earlier rejected cache-reuse: both endpoint costs,
not only the lower one, are retained; no instructions or literals move.
That older regression is still valid evidence, not overwritten.

## Local evidence

Host census:192kbps1648/1765 nonzero outcomes(93.37%);128kbps1074/1204(89.20%).
See [endpoint census](ESP8266_OPUS_ENDPOINT_COST_PROFILE.md). Frequency is not
CPU time.

Linked interpreter:378304 standard table/budget cases;1982 zero and376322
nonzero. Exactly376322 final duplicate reads removed; all earlier reads keep
their addresses and order. Both versions execute15984492 instructions.
Negative tests detect bypassed endpoint loads, lost upper cost, wrong selected
cost, out-of-row access and use of either supposedly dead scratch register.

Host semantic implementation passes24 exact PCM/state/PLC/reset/OOM cases,
including320/510kbps, phase variants and compound packets through120ms.
ASan/UBSan and existing arena/state checks pass. Host timings do not measure
LX106 performance.

107 related preflight regressions PASS,0 failures/skips,79.08seconds.
preflight-tests.log is retained beside the image. This is not the entire
repository test suite.

app903216 bytes; static RAM, IRAM, frame and arena deltas0.
Candidate SHA256:
85af3677670a985918bb17affef136ed291f5bcd030494dba932fd378e752dbc
Control equals accepted bits-fourth:
101d87acdc93a8396ed5b8c234c81aeac291ea6c9646f5ac6345ada9845633c0

Recipe endpoint_cost.cjs, commented ASM endpoint_cost.s, independent proof
endpoint_cost_proof.cjs. Artifact directory:
firmware/development/esp8266-opus-endpoint-cost-candidate-v1.

## Physical measurements

10 A /10 B /10 A with identical fixtures preloaded in RAM, CPU160/QIO40,
no audio output and no stage/function profiling. Save every attempt, maxima,
observation error and memory minimum; compare against both fresh controls.
No UART/reset on GPIO3. Restore ordinary radio through OTA afterwards.

All30 attempts completed, exact PCM and zero decoder/observation errors.
Medians of raw task CPU, percent:

| kbps | A: bits-fourth | B: endpoint-cost | A2: bits-fourth | Maximum call A/B/A2, us |
|---|---:|---:|---:|---:|
|12|23.08860|23.08867|23.09267|8347 /8227 /7751|
|24|54.26169|54.24246|54.25065|14768 /15328 /15665|
|64|64.24463|64.04844|64.23671|17080 /16933 /17141|
|128|76.07402|75.71290|76.11025|19438 /20073 /19507|
|192|86.47023|85.96527|86.49377|22206 /26714 /21444|

Relative time gain192:0.58397% /0.61103% against A/A2;128:0.47470% /0.52208%.
Both high-bitrate gates PASS. The tiny mono12 loss against A is0.00027%;
against A2 no low-bitrate median is worse. Accepted as the new experimental
raw baseline,85.96527% CPU192. Default is unchanged. Another6.94% reduction
in current decoder time is still needed to reach80%; not a live-speed claim.

Static RAM,IRAM,frame and arenas unchanged. Sampled free DRAM minima A/B/A2:
8040 /6800 /8896 B; minimum free stack1660 B in all groups.
Cleanup DRAM minima26296 /26300 /26300 B. These are free-memory observations,
not the decoder's allocation size or evidence of improved allocation.

No HTTP observation errors. All maxima retained, including candidate192
26.714ms and12820.073ms. Different accounting windows give task>wall on
mono12 in A/run4 by20us and A2/run2 by338us; retained, not clamped or removed.
Candidate192 range85.86350..86.17542%, mean85.98255%. The worse maximum than
both controls is not hidden by the better median; underrun-free audio is
still a separate requirement.

Raw JSON/log/SHA/OTA and independent comparisons:
[comparison.json](../firmware/development/esp8266-opus-endpoint-cost-candidate-v1/comparison.json).
The results regression independently recomputes every median, maximum,
minimum and speed gate from all30 archived attempts.

Final112 related regressions PASS,0 failures/skips,87.73seconds, including
independent physical report/restore checks and the new boundary census.
final-tests.log retained beside the image. Not the whole repository suite.

## Restore and remaining qualification

Ordinary live512-idle3s restored OTA to0x10000, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
CPU160/QIO40, C decoder, I2S PDM32/GPIO3,2x512 DMA; benchmark OFF.
Root HTTP200 returned27249 gzip bytes in97.9913ms; this is the document,
not full browser page loading. WebSocket/getindex, stopped station167,
empty error and unchanged playlist hash verified. Heap27628/min24748,
web stack2324 B,RSSI-69dBm. Playback was not started during restore.
Neither this restore check nor raw A/B/A proves20seconds uninterrupted I2S.
