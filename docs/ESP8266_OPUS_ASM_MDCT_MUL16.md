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
- [x] Complete10 A/10 B/10 A physical comparisons, exact PCM, all maxima/RAM.
- [x] Save selection decision and restore ordinary radio over OTA/HTTP/WS.

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

## Result: no confirmed speedup, candidate rejected

All30 target attempts completed (state3/error0), all five PCM hashes exact.
All numbered attempts, original timing fields and maxima retained.

| Input | A median CPU % | B median CPU % | A2 median CPU % |
|---|---:|---:|---:|
| mono12 |23.096083|23.088792|23.089375|
| mono24 |54.562417|54.503229|54.529667|
| stereo64 |64.938875|64.882542|64.859833|
| stereo128 |76.925958|76.921125|76.921188|
| stereo192 |87.669646|87.686833|87.671417|

192 median relative time changes are -0.019605%/-0.017585% gain (small
slowdown) against A/A2.128 gains0.006283%/0.000081%, effectively unchanged.
Both high-bitrate-first gates FAIL. Do not adopt this opcode change or
claim MUL16S has inherently lower latency on LX106. The best accepted recipe
remains three-table MDCT pairs (about87.7% CPU192), not a new MUL16S baseline.

| Input | Maximum call A us | Maximum call B us | Maximum call A2 us |
|---|---:|---:|---:|
| mono12 |8392|8969|8031|
| mono24 |19701|14263|43460|
| stereo64 |23357|17167|16880|
| stereo128 |27014|20164|19443|
| stereo192 |29646|23846|22527|

CPU192 maxima88.932208 /87.749833 /87.742250%. Candidate maximum23.846ms
does not establish continuous playback. A2/mono24 maximum43.460ms retained.

Free DRAM minima1044 /8032 /8172 B; stack free1660 B in all groups. Codec
scratch and static RAM/frame unchanged. Post-run DRAM min/median/max:
A17740/26564/26652, B26124/26476/26652, A2 26300/26476/26652 B.

A/run7 had an HTTP observation timeout and transient minimum1044 B. Its
completed decode/PCM result is retained, not restarted or excluded. No proven
cause is attributed to the codec, Wi-Fi or heap allocator from this evidence.
B/run4/mono12 task_us exceeds wall_us by33us; preserve this timing-window
excess without correcting the CPU median. No hidden outlier filtering.

28 final related Node tests PASS/0skip, including independent30-run
recomputation, outlier retention, exact source/opcode checks and restore QA.
Fresh11-case host semantic parent exact through320/510/mixed/PLC/reset/OOM;
this is not host execution of Xtensa ASM and not a bitrate support limit.

Ordinary live512-idle3s restored OTA, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b,
slot0x10000, C backend, benchmark OFF. RootHTTP200 in205.01ms (single fetch,
not full browser rendering), WebSocket current167/stopped and unchanged
playlist verified. Heap27448/min24748 B, web stack2324 B, RSSI-61dBm.
No UART commands/reset or host Wi-Fi change. Goal70%/live I2S still unmet.

Archived: comparison.json, controls/before, runs, controls/after,
ota-before/candidate/after, host-parent.json, initial-snapshot.json,
restore-ota/snapshot/root.json and regression-final.log beside candidate app.

Next independent hypothesis: four cached table pairs in post-rotation;
register/in-place/bounds conditions saved in
[the opportunity list](ESP8266_OPUS_ASM_OPTIMIZATION_OPPORTUNITIES.md).
This is not implemented yet. Do not repeat MUL16S without a new hypothesis.
