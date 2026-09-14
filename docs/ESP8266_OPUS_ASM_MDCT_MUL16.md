# Opus ASM: exact signed16 MDCT products

2026-09-14. LX106 CPU160/QIO40. Control is accepted
[three-table pair](ESP8266_OPUS_ASM_MDCT_THREE_PAIR.md),87.687% raw CPU192.
Independent opcode-only experiment; no extra layout/arithmetic optimization.

- [x] Fail-closed signed-width dataflow over complete linked MDCT CFG.
- [x] Solve backedges to fixed point, join both successors of every branch.
- [x] Select16 MULL with BOTH operands provably sign-extended16.
- [x] Verify same3-byte MUL16S opcodes and every other ELF/app byte unchanged.
- [x] Check589824 numeric edge products plus full signed16 algebraic bound.
- [x] Preserve C fallback, saved GCC snapshot, RAM/frame/loads/stores/SAR/ABI.
- [ ] Complete10 A/10 B/10 A physical comparisons, exact PCM, all maxima/RAM.
- [ ] Save selection decision and restore ordinary radio over OTA/HTTP/WS.

Width w denotes signed interval[-2^(w-1),2^(w-1)-1]. All input registers
and loaded values start at width32. SRAI reduces width conservatively;
SLLI increases it up to32; EXTUI16 gives width17, NOT signed16. Calls kill
caller registers and preserve call0 callee registers. Unknown instructions,
callees and branch targets fail. Every branch joins facts; loop backedges
cannot preserve a narrower fact when another iteration widens it.

Of33 MULL in clt_mdct_backward_c,16 signed products qualify; the16 unsigned
low16 products and one pointer calculation remain MULL. Numerical domain:
int16(a)=a/int16(b)=b; product[-1073709056,1073741824] fits int32. Thus MULL
low32 and MUL16S agree for all signed16 pairs. No precision/bitrate assumption.
Tests enumerate every signed16 first operand against9 second-operand edges
and compare with BigInt. This enumeration supplements, not replaces, proof.

Each3-byte instruction differs by one opcode byte (82->d1 in little-endian
last byte), operands identical.16 code bytes change;32 digest bytes change;
unchanged XOR here because equal deltas occur an even number of times.
No text/RAM size, alignment, frame, table, control-flow or memory-access change.
No instruction-latency claim is inferred from using a narrower multiply.

Generator: tools/esp8266_opus_asm/mdct_mul16.cjs.
Reporter: tools/esp8266_opus_asm/report_mdct_mul16.cjs.
Tests: tests/esp8266-opus-mdct-mul16.test.js, including widening branch/loop,
unknown-op/call/target, wrong source, unsigned narrowing and profile mutations.
Commented patches.s, patches.o, parent.elf.gz, preflight.json and sdkconfig
saved beside candidate image. Both images903216 B:
firmware/development/esp8266-opus-mdct-mul16-{control,candidate}-v1/app.bin.
Candidate SHA256c92c52b5a57540d24c86b3bd820809bc6292e36c2cc3b86c2d925e62ecded57a.
Control SHA2569de8b4f8ea18ff9ec51eb71f699de12f68968e8309919fdb0f9f5e9955f7572a.

12 related Node tests PASS before deployment, fresh host semantic parent11
PCM scenarios through320/510/mixed/PLC/reset/OOM exact. Host does not execute
the new Xtensa instructions: actual-opcode/range proof and target PCM tests
cover those. Goal70%/continuous I2S not proved; production/default unchanged.
