# PVQ byte phase: seven-instruction a10 helper

2026-09-17. Experimental ASM candidate; no physical speed result yet.
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
- [ ] At least10 physical raw A/B/A trials each; exact PCM hashes,
  CPU medians/maxima, all memory minima and failed observations retained.
- [ ] Accept only under the existing high-bitrate tradeoff gate. Then
  qualify live I2S separately; raw timing alone is not continuous playback.

Tools: `pvq_byte_phase.cjs`, `pvq_byte_phase_proof.cjs`, commented
`pvq_byte_phase.s`. Images and proof bundle are in
`firmware/development/esp8266-opus-pvq-byte-phase-{control,candidate}-v1/`.
This frozen image does NOT contain the separate live allocation-order
experiments. Their reintegration requires a separately validated build.
