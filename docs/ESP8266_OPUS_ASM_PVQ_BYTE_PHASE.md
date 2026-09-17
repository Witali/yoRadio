# PVQ byte phase: seven-instruction a10 helper

2026-09-17. Physical A/B/A completed: **candidate rejected**. Fewer executed
instructions made the complete decoder slower; keep accepted exp2-table32.
Control is the accepted exp2-table32 image, SHA256
`7209b07ddde4febf7078e90100bfac3b3e4d9a7538e1ce44beaac95c30738649`.
Its measured raw CPU192 median is79.626521%; this document does not replace
that result with an instruction-count estimate.

The old leaf saves SAR, sets a variable byte shift, loads one aligned word,
extracts the byte and restores SAR. The candidate keeps the address phase
in caller-dead a11, aligns by subtraction, loads the same word and chooses
EXTUI0/8/16/24 using two BBCI decisions. It never accesses SAR.

- Six existing CALL0 sites:4024e1c3/e1d6/e1ea/e204/e21f/e284. The upper
  endpoint is included; this is not a global replacement of L8UI.
- Seven executed instructions including RET vs nine in the old leaf.
  Two branches can offset the saved instructions. No guaranteed speedup.
-37 live bytes in42 authenticated encoder-only bytes at4024dcc4; calls
  remain at their original addresses. Seven patch ranges total60 bytes.
- The old25-byte a10 leaf remains unchanged but becomes unreachable.
  The accepted a4 helper at4024de08 occupies the rest of its former57-byte
  storage and MUST remain reachable/unchanged.
- CALL0 existed before: its return address and final a0 are identical.
  Only a11 differs (phase instead of saved SAR); all six continuations
  prove it dead. All other registers, stack, memory accesses and SAR agree.

## Evidence

Actual linked instructions are symbolically executed at every one of392
valid byte addresses with32 independent symbolic word bits. Each path
returns the exact unsigned byte, performs the same single in-bounds aligned
load and touches no stack/memory. Decoder-only storage, predecessor and
incoming edges are authenticated against the parent proof chain. Outside
the helper/calls every image byte is unchanged except the image checksum.

App903216B, no RAM/IRAM/frame growth. Candidate SHA256:
`8eb6355671ee63479e22705e736d7f40feee78bf025d3d52fc718d81898c2bd2`.
The parent24 exact PCM/state/PLC/reset/OOM cases through510kbit/s and120ms
remain parent evidence, not newly measured target PCM. C fallback unchanged.

Initial proof attempts correctly refused two overly broad assumptions:
the old57-byte slot also contains the live a4 helper; and the generic a0
liveness walker did not model RSR.SAR on the endpoint continuation.
The final proof uses the precise25-byte leaf and proves identical a0
from unchanged CALL0/RET semantics, rather than ignoring that instruction.
No refused candidate was flashed.

- [x] Assemble and authenticate actual linked helper, table bounds,
  storage, six callers and unchanged image layout.
- [x] Three independent regression tests PASS/0skip in92.35s, including
  changed phase/extraction/alignment, stack/SAR writes, a4 corruption,
  wrong call target, modified dead storage and the complete parent chain.
- [x] At least10 physical raw A/B/A trials each; exact PCM hashes,
  CPU medians/maxima, all memory minima and failed observations retained.
- [x] Apply the existing high-bitrate tradeoff gate: FAIL against both
  controls. Do not integrate this candidate or change the default.
- [ ] Qualify live I2S separately for an accepted candidate; raw timing
  alone is not continuous playback. This rejected candidate is not qualified.

Tools: `pvq_byte_phase.cjs`, `pvq_byte_phase_proof.cjs`, commented
`pvq_byte_phase.s`. Images and proof bundle are in
`firmware/development/esp8266-opus-pvq-byte-phase-{control,candidate}-v1/`.
This frozen image does NOT contain the separate live allocation-order
experiments. Their reintegration requires a separately validated build.

## Physical result: 30 attempts, none excluded

CPU160 MHz, runtime QIO40, packets preloaded in RAM, no PDM output or
function/stage profiling. Wi-Fi/WebUI remain enabled. Task timing includes
charged ISR and measurement bookkeeping: it is not a Wi-Fi-free CPU test.
Each A/B/A group has10 attempts, each with all five fixtures and exact PCM.

| Fixture | Before A, CPU% | Candidate B, CPU% | After A2, CPU% |
|---|---:|---:|---:|
| mono12 | 23.080438 | 23.096146 | 23.091313 |
| mono24 | 54.073271 | 54.089438 | 54.073813 |
| stereo64 | 62.665583 | 63.251500 | 62.687792 |
| stereo128 | 71.839771 | 72.508813 | 71.860083 |
| stereo192 | 79.618646 | 80.282333 | 79.643604 |

These are uncorrected raw task-budget medians, not minimum/best runs.
At192 the candidate is0.8020–0.8336% slower in relative decode time;
at128 it is0.9028–0.9313% slower. Both high-bitrate acceptance gates fail.
The new candidate also fails the raw80% threshold, as well as78%.
The accepted control remains about79.63%; do not replace that baseline
with the candidate or reinterpret the control as a newly discovered gain.

No decoder/HTTP observation errors. Candidate run6/mono12 has task timing
712us greater than the narrower wall window; it is retained without
clamping, subtracting or dropping the attempt. All maxima are archived.
The largest192 decode call is20.375 /20.681 /21.991ms for A/B/A2;
candidate128 maximum18.936ms. These maxima do not qualify live DMA output.

Minimum observed free DRAM across the measured cases:8168 /8032 /8352B.
For192 alone:9800 /9484 /9624B. Task free-stack watermark1660B in every
case; scratch5488B plus15600 word-arena bytes at192, unchanged. Static
RAM/IRAM/frame and903216-B app size remain identical. Free-heap variation
under networking is not evidence of a leak or a changed allocation size.

Interpretation: two BBCI decisions, target placement and instruction-fetch
behavior can outweigh removing RSR/WSR SAR. This whole-decoder measurement
does not isolate their individual cost, and does not measure cache misses.
Do not copy this branch-based helper into other register families on the
strength of its lower instruction count.

Reproduce reporting with `node tools/esp8266_opus_asm/report_pvq_byte_phase.cjs`.
The immutable proof chain, all30 JSON/log pairs, OTA slot/hash observations,
comparisons and independent regression tests are saved with the candidate.
Ordinary-radio restoration is checked separately from raw decoder timing.

Final14 regression tests PASS/0skip in95.26s (final-tests.log). They replay
the linked semantic/negative proof chain, independently recompute all30
attempts and speed/CPU gates, reject dropped/corrupt observations, and
verify the restoration. Prior diagnostic C-radio (not a new production
qualification) restored by OTA to0x110000, SHA256
`661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b`.
HTTP200/gzip27249B in107.34ms; WebSocket current167, volume100, balance0,
stopped station and identical playlist verified. No UART/reset or settings
change. One stopped HTTP sample is not a live WebUI responsiveness test.
