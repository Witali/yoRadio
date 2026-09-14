# Opus ASM: three loads instead of four in FFT radix-5

2026-09-14, CPU 160 MHz / QIO40. Parent: accepted
[MDCT post-rotation pairs](ESP8266_OPUS_ASM_MDCT_POST_PAIR.md).

- [x] Locate the exact GCC ASM/linked instruction group.
- [x] Preserve the eight-byte range with three loads and no executed padding.
- [x] Prove exact registers and ordered reads for arbitrary memory values.
- [x] Verify no interior or indirect branch, no new RAM/frame or changed ABI.
- [x] Complete 10 A /10 B /10 A2 physical raw runs and evaluate both speed gates.
- [x] Save every attempt, maxima/RAM, decision, and restore ordinary radio OTA.

## Change

In the saved GCC kiss_fft.c.s, label .L54 implements `scratch[0] = *Fout0`
inside the radix-5 loop. It reads the same task-private sp+32 pointer twice:

```asm
# Original: 2+2+2+2 bytes.
l32i.n a2, a1, 32
l32i.n a3, a1, 32
l32i.n a2, a2, 0
l32i.n a3, a3, 4

# Candidate: 3+2+3 bytes.
l32i   a3, a1, 32
l32i.n a2, a3, 0
l32i   a3, a3, 4
```

Only [0x40254126,0x4025412e) changes. There is no NOP, new branch, literal,
array or spill. Other ELF bytes and instruction/table addresses stay fixed.
After the group, a2/a3 have the same complex r/i values; all other registers,
SAR and memory are unchanged. The two data loads stay in the same order.
The removed operation is a duplicate private-stack read, not MMIO or shared
input. The symbolic proof covers arbitrary word values and possible data
aliasing. No bitrate/mode or numerical-precision restriction is added.

This differs from the rejected frozen-reloads experiment: that retained four
instructions by replacing one L32I with MOV. Here the whole group has three
instructions. Narrow/wide encoding preserves layout, but the shorter sequence
alone does not prove lower cycle count, especially with load dependencies.
The existing C_MUL_TABLE already reads twiddle r/i as one packed word; that
earlier optimization is unchanged and is not credited as a new improvement.

## Evidence and reproduction

`node tools/esp8266_opus_asm/fft_load3.cjs` generates both images and verifies
actual linked opcodes, unchanged memory/addresses and image checksums.
Commented code: fft_load3.s. Report: report_fft_load3.cjs. Tests:
tests/esp8266-opus-fft-load3.test.js, including negative mutation guards.
10 pre-deployment related tests PASS; no source C or saved GCC ASM changes.

Artifacts: firmware/development/esp8266-opus-fft-load3-{control,candidate}-v1.
Both app.bin images are 903216 B. Candidate SHA256:
081444a69f1f32fb407bbe39f06ae9175980e6fbefbbab124e1628f78bb682e0.
Control SHA256:
5e5525a242f5145db2aa5888ea76bd8f4515e3f7910333ec5f7d12cedaced7d4.
No production/default change. The candidate is rejected by the physical
performance gate below.70% CPU192 and continuous I2S PDM/WebUI remain unproven.

## Physical result: no reproducible speedup, candidate rejected

All30 A/B/A attempts completed, state3/error0, all target PCM hashes exact.
Five reproducible noise+tone RAM fixtures:12/24 kbit/s mono,64/128/192 stereo,
48kHz,20ms packets, decoded to mono PCM16.120 measured packets per fixture
per run. No network audio, PCM output or function/stage profiling. Task CPU
includes charged ISR/bookkeeping; this is not a live playback qualification.

| Input | A CPU median % | B CPU median % | A2 CPU median % | Max call A/B/A2, us |
| --- | ---: | ---: | ---: | --- |
| mono12 | 23.099208 | 23.090604 | 23.097938 | 7727 /7922 /8580 |
| mono24 | 54.330521 | 54.323146 | 54.321208 | 15014 /15273 /14191 |
| stereo64 | 64.680542 | 64.682417 | 64.648146 | 17194 /17312 /16981 |
| stereo128 | 76.695167 | 76.706917 | 76.721813 | 19786 /19440 /19189 |
| stereo192 | 87.470146 | 87.479646 | 87.475354 | 23989 /23391 /21813 |

192 relative time changes are0.01086% and0.00491% slower.128 is slightly
slower against A, slightly faster against A2; both full selection gates FAIL.
The tiny differences do not establish an architectural latency. Do not retain
this more complicated overlay as an accepted optimization merely because it
has fewer instructions. The accepted MDCT post-pair parent remains the best
experimental variant; ordinary C/default is unchanged.

The original pointer load has an independent instruction before dereference;
the candidate dereferences immediately. This is a possible load-use explanation,
not measured stall cycles. A distinct19-byte scheduling hypothesis is saved in
the [opportunity list](ESP8266_OPUS_ASM_OPTIMIZATION_OPPORTUNITIES.md), along
with a more frequent PVQ row-address candidate. Neither is implemented here.

No RAM, scratch or stack allocation changed; FFT frame remains288 B and every
other ELF byte is identical. Free DRAM minima A/B/A2:8176 /8352 /8024 B;
minimum task stack free1660 B in all series. Post-run free DRAM medians:
26476 /26580 /26388 B. These differences are runtime heap observations, not
changed decoder allocations. All30 runs and their maxima remain archived.
No HTTP observation errors occurred. Mono12 task-window excesses are retained:
A/run1=1314us, A/run7=507us, A2/run3=157us. No clamping, filtering or re-runs.

33 final related regressions PASS/0skip, including independent CPU-median
calculation, archive hashes, both rejection gates and restoration. Fresh11-case
host semantic-parent check is exact, including320/510, mixed PLC/reset/OOM;
it does not execute the target ASM. Symbolic linked-opcode proof covers the
changed loads for arbitrary valid data. Not a full-repository test-suite claim.

All evidence is in firmware/development/esp8266-opus-fft-load3-candidate-v1:
comparison.json, controls/before, runs, controls/after, host-parent.json,
regression-final.log and OTA/snapshot/HTTP reports.

Ordinary radio restored OTA to0x10000, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
HTTP root200 in104.2838ms (transfer only, not browser render), WebSocket
getindex/current167/stopped, unchanged station/playlist. RSSI-60dBm,
free heap27448 B/min24748 B, web stack free2324 B. No UART or reset commands.
Goal70% remains unmet; this experiment does not justify continuous I2S claims.
