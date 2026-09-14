# Opus ASM: four cached post-rotation table pairs

2026-09-14, LX106 CPU 160 MHz / QIO40. Control is accepted
[pre-rotation three-table pairs](ESP8266_OPUS_ASM_MDCT_THREE_PAIR.md).
The rejected MUL16S experiment is NOT included; all multiplications stay MULL.

- [x] Rewrite only post-rotation [0x402473a0,0x402474b4), 276 bytes.
- [x] Keep four immutable words in a0/a11/a12/a14 across adjacent iterations.
- [x] Reassociate yr sums to release a14, without another array or spill.
- [x] Prove exact PCM32/table-word arithmetic and in-place event sequence.
- [x] Check all four standard transforms, central pair and exit liveness.
- [x] Complete 10 control / 10 candidate / 10 repeated control target runs.
- [x] Save speed/RAM/maxima decision and restore ordinary radio via OTA.

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

## Physical result: accepted as an experimental ASM baseline

All30 A/B/A attempts completed with exact target PCM hashes, state3/error0.
The five RAM fixtures use12/24 kbit/s mono and64/128/192 kbit/s stereo input,
48kHz and20ms packets, decoded to mono PCM16. Each run decodes120 packets
per fixture. They contain reproducible tones plus seeded noise, not a long
real-radio recording. Network audio, audio output and function/stage profiling
are disabled; task timing still includes charged interrupts/bookkeeping.

| Input | A CPU median % | B CPU median % | A2 CPU median % | Max call A/B/A2, us |
| --- | ---: | ---: | ---: | --- |
| mono12 | 23.094688 | 23.088167 | 23.082854 | 8295 /9143 /7308 |
| mono24 | 54.519146 | 54.320000 | 54.511229 | 19634 /14993 /16925 |
| stereo64 | 64.876917 | 64.632062 | 64.878167 | 23734 /17211 /18311 |
| stereo128 | 76.897875 | 76.682625 | 76.908667 | 29323 /19727 /18794 |
| stereo192 | 87.661438 | 87.481438 | 87.674250 | 30844 /21829 /22193 |

192 relative time gains are0.20534% and0.21992%;128 also improves in both
comparisons. The worst low-bitrate relative loss is0.023015% (mono12 vs A2),
less than either high-bitrate gain. Both saved selection gates PASS.
This is a small measured improvement, not evidence of a general instruction
latency or a cache-miss explanation. New experimental raw best87.481438%.
The70% target remains false; the maximum192 call21.829ms still exceeds a
20ms packet duration. Continuous I2S playback has NOT been qualified.

Static sections, frame96 B, scratch sizes and all non-patch ELF bytes are
unchanged. Minimum free DRAM A/B/A2:1224 /8216 /8168 B; minimum lifetime
task stack free1660 B for all three series. Median free DRAM after completion:
26384 /26476 /26476 B. These heap minima vary with network/other activity;
do not interpret them as changed decoder allocations.

No attempt was excluded. A/run6 has an HTTP observation timeout and the1224 B
minimum, but later terminal state3/error0 and every PCM hash are valid. Its
192 CPU100.936833% and30.844ms maximum remain in the report. The cause of this
transient is not established. A2/mono12 runs2/6/10 show task-window excesses
over measured wall time of2077/1617/588us, also retained without correction.
They are measurement-accounting anomalies, not negative waiting time.

All28 final related regressions PASS,0 skipped. These re-derive image/proof
hashes, all30 archived runs and selection results, and restoration checks.
The11-case host semantic-parent check includes320/510 kbit/s and exact PCM;
it does not execute the new target instructions. Standard transform coverage
for those instructions is provided by the linked symbolic/numeric proof.
This is not a claim that the entire repository test suite passes.

Archived in firmware/development/esp8266-opus-mdct-post-pair-candidate-v1:
comparison.json, controls/before, runs, controls/after, OTA evidence,
host-parent.json and regression-final.log. Reproduce the report with
`node tools/esp8266_opus_asm/report_mdct_post_pair.cjs`.

Ordinary C-backend radio restored via OTA to0x10000, app SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
HTTP root200 in99.5531ms (response transfer, not browser rendering), WebSocket
getindex/current167/stopped, station and playlist unchanged. RSSI-59dBm,
free heap27452 B/min24748 B, WebUI stack free2324 B. No UART/reset or default
profile change. The board is left stopped as before the experiment.
