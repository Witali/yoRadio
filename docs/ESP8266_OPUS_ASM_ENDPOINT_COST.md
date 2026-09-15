# Opus ASM: reuse both PVQ endpoint costs

2026-09-15. Experimental frozen-layout candidate over accepted bits-fourth.
Not production; speed and continuous audio are not established by local proof.

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

## Physical protocol and pending work

10 A /10 B /10 A with identical fixtures preloaded in RAM, CPU160/QIO40,
no audio output and no stage/function profiling. Save every attempt, maxima,
observation error and memory minimum; compare against both fresh controls.
No UART/reset on GPIO3. Restore ordinary radio through OTA afterwards.

The candidate is not yet accepted. Local correctness does not establish
the80% CPU192 target or20seconds continuous I2S PDM with WebUI.
