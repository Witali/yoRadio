# Opus ASM: four cached post-rotation table pairs

2026-09-14, LX106 CPU 160 MHz / QIO40. Control is accepted
[pre-rotation three-table pairs](ESP8266_OPUS_ASM_MDCT_THREE_PAIR.md).
The rejected MUL16S experiment is NOT included; all multiplications stay MULL.

- [x] Rewrite only post-rotation [0x402473a0,0x402474b4), 276 bytes.
- [x] Keep four immutable words in a0/a11/a12/a14 across adjacent iterations.
- [x] Reassociate yr sums to release a14, without another array or spill.
- [x] Prove exact PCM32/table-word arithmetic and in-place event sequence.
- [x] Check all four standard transforms, central pair and exit liveness.
- [ ] Complete 10 control / 10 candidate / 10 repeated control target runs.
- [ ] Save speed/RAM/maxima decision and restore ordinary radio via OTA.

## Mechanism and correctness scope

Two forward table pointers begin at low halfwords. Two reverse pointers
begin at high halfwords. On the first iteration, load four aligned words;
on the second, extract their remaining halves without a new flash read.
The reverse high-half addresses are aligned by subtracting 2, not by issuing
an unsafe16-bit load. Every original table access stays within the same
actual immutable standard-mode table. No new buffer, stack or RAM bytes.

The forward yr sum uses a10/a13 and reverse yr uses a7/a13. Each MULL,
SRAI15 and SLLI1 term keeps its own rounding/overflow semantics. Only ADD32
is reassociated modulo2^32. No MUL16S, combined rounding, approximation,
bitrate cap or format change. C fallback and saved GCC snapshot unchanged.

Actual linked N4=480/240/120/60, post-loop counts240/120/60/30: all even.
The generic C source also handles odd N4; this frozen diagnostic targets the
linked standard mode, not arbitrary custom modes. Other builds retain C.
Input stride affects pre-rotation only; this in-place post-loop advances
the original packed complex pointers by +8/-8 bytes, without a new stride.

Four PCM reads and four PCM writes per iteration retain exactly their
original interleaving: both rear samples read before the first front store.
The interpreter compares memory events, not just final arrays. This matters
for in-place operation. Mutable stack accesses likewise retain sequence;
only three proved-unchanged offset reads become once per pair, not twice.

225 symbolic pairs cover all table pairs/all standard transforms with
arbitrary PCM32 and table-word bits. Numeric tests run 16 full in-place
transforms: four N4 values, four aligned buffer offsets, extrema and seeded
random PCM32. Central pairs included. Separate negative tests alter phase,
rounding, reverse address, write order and exit scratch usage.

At exit original a0/ABI registers are restored or overwritten before use.
Fail-closed liveness follows 87 reachable instructions through TDAC/return.
Original96-byte frame, other function bytes/addresses/tables and SAR unchanged.
Per two-iteration proof: 195 instructions become173, eight table reads become
four, six invariant stack reads become three. Not a cycle/speed prediction.

## Reproduction

Generator: tools/esp8266_opus_asm/mdct_post_pair.cjs; commented ASM:
mdct_post_pair.s; symbolic/event proof: mdct_post_proof.cjs; reporter:
report_mdct_post_pair.cjs. Tests: tests/esp8266-opus-mdct-post-pair.test.js.
The negative liveness test was corrected to mutate the exit path, not an
earlier occurrence before the patch. Final pre-deployment 12 tests PASS.

Both images are903216 B under
firmware/development/esp8266-opus-mdct-post-pair-{control,candidate}-v1/app.bin.
Candidate SHA256:
5e5525a242f5145db2aa5888ea76bd8f4515e3f7910333ec5f7d12cedaced7d4.
Control SHA256:
9de8b4f8ea18ff9ec51eb71f699de12f68968e8309919fdb0f9f5e9955f7572a.
preflight.json, parent.elf.gz, patches.s/elf and sdkconfig archived beside app.

Host semantic parent testing is distinct from execution of the new Xtensa
instructions. Target PCM hashes and linked opcode/proof checks cover those.
No production/default change. Goal70% and continuous I2S/WebUI not yet proven.
