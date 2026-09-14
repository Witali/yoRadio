# Opus ASM: shared-parity MDCT t0/t1/bitrev pairs

2026-09-14. ESP8266 LX106, CPU160/QIO40. Independent experiment after
[standalone bitrev](ESP8266_OPUS_ASM_MDCT_BITREV_PAIR.md), which was NOT accepted.
Control is accepted MDCT-half/tell-inline, not that rejected bitrev candidate.

- [x] Reschedule pre-rotation yr arithmetic to free a14/a15, no spills.
- [x] Cache t0/t1/bitrev words in a14/a15/a0, one shared parity branch.
- [x] Validate actual linked table alignment, bounds, mode and loop ABI.
- [x] Symbolic modular32 proof for450 pairs/all four transforms;16 numeric
  full transforms including PCM32 extrema, deterministic random, strides1/2
  and deliberately aliased input/output. No arithmetic rounding relaxed.
- [x] Preserve every other ELF byte, function/table address, RAM and stack.
- [x] Complete10 control /10 candidate /10 repeated control physical runs.
- [x] Save selection/maxima/RAM, restore ordinary radio and verify HTTP/WS.

## Exact transformation

In clt_mdct_backward_c, replace only [0x40247268,0x40247329):193 bytes.
Live instructions use160 bytes, followed by33 unreachable padding bytes.
All other ELF bytes, including original96-byte frame and FFT CALL0, unchanged.

For each pair of iterations: load aligned32-bit t0/t1/bitrev on the low half,
retain words in registers, take high halves on the following iteration.
One BBSI tests all three pointers' phase. The invariant -2*N4 stack value and
t0 address are needed only on the low half. Six table loads become three,
two stack reads of that invariant become one. Other PCM/stack reads and
all writes retain their sequence and values. No new array/stack slot.

yr uses a7 accumulator/a11 scratch, then yi uses the original a4/a5/a8/a2.
Reassociation is confined to modular32 ADD; each MULL, SRAI15 and SLLI1
term retains its own rounding/overflow semantics. Low unsigned16 products
are NOT changed to MUL16S. SAR unchanged. This is not reduced-precision PCM.

Original a0 is saved at sp+92; no loop call can destroy cached words.
At exit original instructions restore a15=yp from a9 and pass original
FFT arguments. FFT kills a0; a14 is overwritten before the following use.
Original epilogue restores a0/a12..a15. All tables immutable flash/L32I,
no unsafe16-bit flash/IRAM access introduced.

Actual standard MDCT N4=480/240/120/60, all even, all t0/t1/bitrev bases
word aligned. Proof checks linked mode48000_960_120 and its four FFT states.
No bitrate cap or packet-duration restriction is added. Not a general
arbitrary CUSTOM_MODES API: other builds keep the original C fallback.
Post-rotation/TDAC table accesses are unchanged in this experiment.

Per pair in the two-iteration proof:135 reachable instructions become106;
an intermediate high iteration has one extra back J in both variants.
Instruction counts are NOT cycle counts or predicted whole-decoder gain.

## Reproduction and evidence

Generator: tools/esp8266_opus_asm/mdct_three_pair.cjs, commented source
mdct_three_pair.s. Reporter: report_mdct_three_pair.cjs.
Tests: tests/esp8266-opus-mdct-three-pair.test.js (mutation guards included).

firmware/development/esp8266-opus-mdct-three-pair-{control,candidate}-v1/app.bin
are903216 B. Candidate SHA256:
9de8b4f8ea18ff9ec51eb71f699de12f68968e8309919fdb0f9f5e9955f7572a.
Control SHA256:
f74fb6f9b2dfd2bd4fd51ac63b772503dbe93b2917c2b012f5e4c15d223c3d97.
preflight.json, patches.s/elf, parent.elf.gz and sdkconfig saved beside image.

Fresh host tell-inline semantic parent11 scenarios exact (through320/510,
mixed/PLC/reset/OOM). Host does NOT execute new Xtensa ASM. New instructions
are checked by interpretation of actual linked disassembly plus physical
PCM hashes.12 related Node tests PASS/0skip before candidate deployment.

Raw runs use RAM-preloaded reproducible packets, no network audio or
PDM/output/function/stage profiling. CPU includes charged interrupts and
unchanged benchmark bookkeeping. Goal70% and live I2S qualification not yet
achieved. Default/ordinary firmware and C backend are unchanged.

## Physical results: accepted experimental raw candidate

All30 attempts completed with exact PCM hashes and no decoder/observation
errors. No runs were dropped/replaced. Same five12-packet20ms RAM fixtures,
10 rounds per run,120 decoded packets/115200 mono48k output samples per case.

| Input | A median CPU % | B median CPU % | A2 median CPU % |
|---|---:|---:|---:|
| mono12 |23.086625|23.088333|23.084646|
| mono24 |54.910125|54.518042|54.919208|
| stereo64 |65.273667|64.872167|65.308604|
| stereo128 |77.325896|76.915479|77.305708|
| stereo192 |88.054104|87.687042|88.067042|

192 relative time gain0.41686% against A and0.43149% against A2;
128 gains0.53076%/0.50479%. Both exceed mono12 losses0.00740%/0.01597%.
Both saved high-bitrate-first gates PASS. Retain as a new experimental
baseline, not as a production/default change. Reaching70% still requires
another20.17% time reduction from this result, followed by live I2S/WebUI QA.

| Input | Maximum call A us | Maximum call B us | Maximum call A2 us |
|---|---:|---:|---:|
| mono12 |8500|9107|7299|
| mono24 |14738|15972|14368|
| stereo64 |19419|17398|22533|
| stereo128 |21015|19288|19667|
| stereo192 |22674|21932|22211|

CPU192 maxima88.091875 /87.747417 /88.149500%. Candidate maximum call
21.932ms still exceeds a20ms audio frame: average improvement does NOT prove
continuous playback. No guarantee of better maxima on every future stream.

Free DRAM minima8176 /8168 /8384 B, stack free1660 B in all groups.
Static RAM,96-byte MDCT frame and measured codec scratch unchanged. Whole-app
sampled heap differs slightly between runs; this is not a memory-leak audit.
Post-run DRAM min/median/max: A26124/26476/26652, B26192/26476/26652,
A2 25984/26336/26688 B. Timing-window excesses retained: A/run6/mono12
task_us exceeds wall_us by104us; B/run5/mono12 by3us. No exclusions or
adjusted CPU medians. All maxima and original timing fields remain archived.

23 final related Node tests PASS,0skip, including independent recalculation
of all30 results and restore checks. Host semantic parent11 cases exact;
new Xtensa ASM correctness scope is the proof, numeric transforms and five
physical fixtures, not a claim that host executes target instructions.

Ordinary live512-idle3s restored OTA, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b,
slot0x10000, C backend/benchmark OFF. HTTP root200 in106.01ms (single fetch,
not browser rendering). WebSocket current167/stopped and unchanged playlist
verified. Heap27448 B/min24748 B, web stack2324 B, RSSI-60dBm. No UART/reset.

Evidence: comparison.json, controls/before, runs, controls/after,
ota-before/candidate/after, host-parent.json, initial-snapshot.json,
restore-ota/snapshot/root.json and regression-final.log beside candidate app.

## Next independent experiment

Test MULL -> MUL16S for proven signed16 x signed16 products, without
changing addresses/widths/arithmetic or combining with another optimization.
Preliminary conservative signed-width dataflow identifies16 candidate sites:
pre-rotation402472a8/b6/c6/cc; post-rotation402473d7/dd/e3/f7 and
4024745a/60/66/6c; TDAC402474ef,40247502/08/0e (full addresses in current ELF).
Require a persistent fail-closed range/CFG verifier, opcode proof and ten
A/B/A physical measurements before acceptance. Do NOT substitute unsigned
low16 products (range0..65535). Instruction latency/gain is not established.
