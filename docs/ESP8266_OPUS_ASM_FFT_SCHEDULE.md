# Opus ASM: schedule an independent load before FFT dereference

2026-09-14, LX106 CPU 160 MHz / QIO40. This is an independent experiment
on the accepted [MDCT post-pair](ESP8266_OPUS_ASM_MDCT_POST_PAIR.md) parent,
not a continuation on the rejected FFT load3 binary.

- [x] Implement the exact 19-byte scheduling hypothesis from the plan.
- [x] Prove registers and memory effects, including possible pointer aliasing.
- [x] Run 648 numeric overlap/edge cases and negative mutation guards.
- [x] Preserve remaining ELF bytes, addresses, stack and RAM.
- [x] Complete 10 A /10 B /10 A2 target runs and evaluate both speed gates.
- [x] Archive all attempts/maxima/RAM and restore ordinary radio via OTA.

## Mechanism

Only [0x40254126,0x40254139) in opus_fft_impl's radix-5 loop changes.
The accepted parent has two private sp+32 pointer loads, two PCM loads,
two stores, a private sp+100 pointer load and a packed twiddle load.
The candidate removes the duplicate pointer read and moves sp+100 between
the remaining pointer load and its dereference:

```asm
l32i   a3, a1, 32
l32i   a4, a1, 100
l32i.n a2, a3, 0
l32i   a3, a3, 4
s32i   a2, a1, 156
s32i   a3, a1, 164
l32i.n a6, a4, 0
```

Seven instead of eight instructions, with widths 3+3+2+3+3+3+2 =19 bytes.
No NOP, new branch/literal/array/spill. The independent sp+100 load separates
pointer load and use; this is not a claim about guaranteed LX106 cycle counts.
The FFT frame remains288 B; all other instructions/tables and sections stay
byte-identical. C fallback and immutable GCC ASM snapshots are not edited.

## Exactness, not an assumed non-aliasing shortcut

Only sp+32 and sp+100 are stable private words; neither is written in the
fragment. Writes remain to sp+156 and sp+164 in the original order. Both PCM
reads precede both stores. The twiddle data read still follows both stores.
The symbolic interpreter represents a data read that could overlap a store
with an explicit conditional expression. Thus equality does not rely on
assuming that a data pointer never aliases a stack output. Final a2/a3/a4/a6,
all other registers, memory and SAR match; no ABI changes or calls are added.

648 numeric cases cover nine aligned PCM and nine twiddle addresses with
eight edge/seeding values, including pointer metadata and written words.
This supplements the arbitrary-word symbolic proof. Moving twiddle read
before stores, reversing stores, changing pointer offsets or adding an
interior branch fails the appropriate regression. Numeric alias filtering
is supplemental; symbolic memory events are the exact ordering proof.

12 pre-deployment related regressions PASS/0skip. Target speed/PCM must still
be verified by physical runs; host testing alone cannot validate Xtensa speed.

## Reproduction and artifacts

`node tools/esp8266_opus_asm/fft_schedule.cjs` builds and verifies both images.
Commented instructions: fft_schedule.s. Reporter: report_fft_schedule.cjs.
Tests: tests/esp8266-opus-fft-schedule.test.js.

Artifacts are firmware/development/esp8266-opus-fft-schedule-{control,candidate}-v1.
Both app.bin files are903216 B. Candidate SHA256:
3cdf60498cce7d57238d2b2d78c2c43d4b7b4ba0ee42b3b400c18c359b5206ea.
Control SHA256:
5e5525a242f5145db2aa5888ea76bd8f4515e3f7910333ec5f7d12cedaced7d4.
Control was uploaded from the identical accepted parent artifact before the
candidate was built; the reporter verifies that exact hash and actual slot.

No default/production change.70% CPU192 and continuous I2S PDM/WebUI remain
unproven. The physical candidate was not accepted (results below).

## Physical result: scheduling candidate rejected

All30 A/B/A attempts completed with exact target PCM, state3/error0.
The same five RAM fixtures use12/24 kbit/s mono and64/128/192 stereo input,
48kHz,20ms packets, mono PCM16 output;120 measured packets per fixture/run.
No network audio, PDM or stage/function profiler. Task CPU still includes
charged interrupts and bookkeeping; no speculative overhead is subtracted.

| Input | A CPU median % | B CPU median % | A2 CPU median % | Max call A/B/A2, us |
| --- | ---: | ---: | ---: | --- |
| mono12 | 23.095000 | 23.080542 | 23.087063 | 7907 /7811 /8529 |
| mono24 | 54.335729 | 54.319354 | 54.334000 | 16039 /15882 /15684 |
| stereo64 | 64.650875 | 64.663312 | 64.676875 | 19964 /17088 /17194 |
| stereo128 | 76.736917 | 76.751354 | 76.726458 | 24458 /23012 /19885 |
| stereo192 | 87.480438 | 87.538375 | 87.473479 | 21735 /24599 /22096 |

192 is0.06623% and0.07419% slower in relative time;128 is also slower
against both controls. Both selection gates FAIL: the candidate is rejected.
This neither proves nor disproves a hardware load-use stall; the experiment
does not measure stall counters. Do not accept it solely for fewer instructions.
The prior MDCT post-pair remains the accepted experimental raw baseline.

No static RAM/frame/scratch growth. Free DRAM minima A/B/A2:
3296 /7484 /8168 B; task stack free minimum1660 B in all series. Post-run
free DRAM medians26476 /26564 /26476 B. A/run3 minimum3296 B is retained;
its cause is not established. Initial RSSI was-75dBm, but packets were in RAM,
and this does not establish a Wi-Fi explanation for decoder timing differences.
No HTTP observation errors. Mono12 accounting excesses are retained:
A/run5=2603us, B/run6=1236us, B/run8=2898us. No filtering/clamping/re-runs.

39 final related regressions PASS/0skip, including all30 hashes/attempts,
independent CPU medians, rejection gates and restoration. Fresh11-case host
semantic-parent checks, including320/510/PLC/reset/OOM, have exact PCM.
Host results are not target execution/timing; the linked symbolic/numeric proof
and physical hashes validate this target patch. Not a full-repository QA claim.

Evidence: firmware/development/esp8266-opus-fft-schedule-candidate-v1,
comparison.json, controls/before, runs, controls/after, host-parent.json,
regression-final.log, OTA/snapshots/HTTP reports.

Ordinary C-backend radio restored by OTA to0x10000, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
HTTP200 root transfer103.0571ms (not browser-render time), WebSocket
getindex/current167/stopped, station and playlist unchanged. RSSI-60dBm,
free heap27452 B/min24748 B, web stack free2324 B. No UART/reset commands.
Goal70% and continuous I2S PDM/WebUI remain unfulfilled.
