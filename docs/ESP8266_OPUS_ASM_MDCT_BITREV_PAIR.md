# Opus ASM: paired MDCT bitrev word reads

2026-09-14, LX106 CPU160/QIO40. Control is the accepted experimental
[MDCT half selector](ESP8266_OPUS_ASM_MDCT_HALF.md), not the older tell-inline alone.

- [x] Replace one24-byte pre-rotation block, preserving all other ELF bytes.
- [x] Keep a loaded32-bit bitrev word in a0 for two adjacent int16 entries.
- [x] Validate actual four immutable flash tables, alignment, bounds and mode.
- [x] Prove signed extraction for arbitrary word bits, scratch liveness and ABI.
- [x] Ten physical runs per A/B/A group, exact PCM, all maxima/free RAM retained.
- [x] Archive decision (not accepted) and restore ordinary radio over OTA.

The unchanged96-byte prologue saves return address a0 at sp+92. No instruction
in the pre-rotation loop uses a0; the following FFT CALL0 overwrites it before
observing it, and function return restores the original address from sp+92.
This allows one register of temporary storage without another array/stack slot.
Removed temporary values a2/a5/a7 are overwritten before their next read.
All other live registers and SAR are unchanged. No memory writes are introduced.

First/low iteration: BBSI not taken, aligned L32I a0,a12,0; sign-extend low half.
Next/high iteration: reuse signed high half of a0, no second load. a12 advances
by2 in the unchanged loop. Per pair: two loads become one,14 instructions become8
inside this block. This is NOT a CPU-speed prediction. Four padding bytes are
unreachable; both paths explicitly branch to the original continuation address.

Actual standard Opus mode has bitrev counts480/240/120/60. All are word-aligned
immutable flash arrays; the public decoder creates the pinned48000/960 mode.
Generator rejects a different parent/table layout. No codec bitrate limit or
packet-duration restriction is added;320/510 kbps and PLC share the same tables.
This specialized diagnostic is not a general arbitrary custom-CELT-mode API.
Other architectures and custom configurations retain the original C fallback.
The last iteration performs no new read beyond the original table; post-rotation
in-place ordering and TDAC/window accesses are not modified in this experiment.

Generator: tools/esp8266_opus_asm/mdct_bitrev_pair.cjs. App903216 B,
candidate SHA2563095072ae7bed52ce2fb83b815122487e20403f5adbacd14116d91e363bf0274.
Saved under firmware/development/esp8266-opus-mdct-bitrev-pair-{control,candidate}-v1.
Default/C fallback/source snapshot unchanged. Goal70% remains unproven.

## Physical results: standalone candidate not accepted

All30 attempts completed, all PCM hashes exact, no decoder or observation errors.
Raw benchmark: five fixtures,12 RAM-preloaded20ms packets each,10 rounds per run;
no network audio, normalization/PDM or stage/function profiler. CPU accounting
retains the same task bookkeeping/charged interrupts as the control.

| Input | A median CPU % | B median CPU % | A2 median CPU % |
|---|---:|---:|---:|
| mono12 |23.08456|23.08917|23.08448|
| mono24 |54.91571|54.88748|54.89888|
| stereo64 |65.27042|65.23885|65.26217|
| stereo128 |77.33221|77.29390|77.30623|
| stereo192 |88.05546|88.02013|88.07158|

192 improves by0.04013%/0.05843% relative time against A/A2.128 improves
0.04954%/0.01595%. But mono12 slows0.01994%/0.02031%: the second control's
128 gain is smaller than the low-rate loss. Initial selection passes, repeated
selection fails. Do not change the saved relative high-bitrate-first criterion
to accept this tiny result. The standalone recipe remains OFF/rejected;
the accepted best remains MDCT-half/tell-inline, previously88.06342% CPU192.
No broad causal claim about these small timing differences or cache misses.

| Input | Max call A us | Max call B us | Max call A2 us |
|---|---:|---:|---:|
| mono12 |7828|7797|8401|
| mono24 |15002|15592|14332|
| stereo64 |17590|19209|17310|
| stereo128 |20022|20287|19547|
| stereo192 |22129|22621|22165|

CPU192 maxima88.16167 /88.10571 /88.09033%; no single-call improvement.
Free DRAM minima8004 /8172 /8168 B; stack free1660 B in every group.
Static RAM,96-byte MDCT frame and measured codec scratch unchanged.
All numbered runs and maxima retained; no exclusions or replacement attempts.

24 related Node regressions PASS,0 skipped. Fresh host parent11 scenarios
exact through320/510/mixed/PLC/reset/OOM. Host runs C semantic parent, NOT the
new Xtensa code. Actual assembly is covered by bit-origin/signed-word proof,
linked table/mode/liveness/ABI checks and five physical PCM fixtures across30 runs.
Standard120ms compound packets reuse these MDCT tables; arbitrary custom CELT
mode layouts are outside this pinned diagnostic, not silently restricted at runtime.

Evidence beside app: preflight.json, patches.s/elf, parent.elf.gz,
comparison.json, controls/before, runs, controls/after, host-parent.json,
regression-final.log and OTA/restore snapshots.

Normal live512-idle3s app restored OTA, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
Root HTTP 200 in100.29ms (one request, not browser rendering), WebSocket current167,
stopped state and identical playlist verified. Heap27628 B/min24748 B, web
stack2324 B, RSSI-64dBm. Goal70% and live I2S qualification remain incomplete.

Next distinct experiment is saved in the main opportunity list: reschedule
pre-rotation arithmetic to free a14/a15, cache t0/t1/bitrev together, share
parity/address work. This is not merely re-running the rejected24-byte recipe.
