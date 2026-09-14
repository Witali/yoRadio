# Opus ASM: MDCT signed-half selection, frozen layout

2026-09-14, ESP8266 / LX106 160 MHz, QIO40. Independent candidate after
[unsuccessful duplicate-load replacement](ESP8266_OPUS_ASM_FROZEN_RELOADS.md).

- [x] Build five exact17-byte instruction replacements over the best tell-inline
  control. Three pre-rotation coefficient/bitrev reads, two TDAC window reads.
- [x] Keep all other ELF bytes, function/table addresses, RAM,96-byte MDCT stack,
  original aligned L32I accesses and register allocation unchanged.
- [x] Prove all32 input bits, both pointer parities, all registers and SAR.
- [x] Ten physical A/B/A runs per group, all30 attempts/peaks/memory retained.
- [x] Archive results, apply high-bitrate criterion, restore normal radio by OTA.

Old sequence: mask=2; sign-extend low half; test address; optionally overwrite
with signed high half and jump to next instruction. New: mask=2; BBSI to high
half; otherwise low extension and jump past high path. The high path executes
3 instead of6 instructions, low5 instead of4. Alternating adjacent halfwords
average4 versus5; this is NOT a CPU-cycle or full decoder speed measurement.

No paired word-load optimization yet, no transform-size assumption, no new
buffer, no PCM approximation and no bitrate cap. No table bounds change.
Both17-byte slots use the original locations. Everything except the five
slots and image checksum/digest is byte-identical to the control app.

Generator: tools/esp8266_opus_asm/mdct_half.cjs. The source snapshot and C
fallback are untouched. Diagnostic candidate only, not default. Comments
in patches.s describe ABI and changes. A linker script fixes five standalone
sections at their original addresses; final app is repacked with SDK elf2image.

Artifacts: firmware/development/esp8266-opus-mdct-half-{control,candidate}-v1.
App903216 B, candidate SHA256
f74fb6f9b2dfd2bd4fd51ac63b772503dbe93b2917c2b012f5e4c15d223c3d97.
Control SHA2560129559856a9b339ec8428d903fc3e9bd3a4489bc127f1ed7a310d127d310811.

Goal remains raw decoder CPU192 <=70%, then >=20 seconds continuous I2S PDM
with working WebUI. No such result is claimed by static verification.

## Physical result: very small experimental gain, not production qualification

All30 runs completed, decoder errors0, all PCM hashes exact. No observation
timeouts. Each fixture:12 RAM-preloaded20ms packets,10 rounds/run; five fixtures
12/24/64/128/192 kbps. No network audio, PDM or stage/function profiling.
Task CPU retains benchmark bookkeeping and charged interrupts as in the control.

| Input | A CPU median % | B CPU median % | A2 CPU median % |
|---|---:|---:|---:|
| mono12 |23.08652|23.08913|23.08248|
| mono24 |54.95871|54.90596|54.97467|
| stereo64 |65.34015|65.25946|65.32848|
| stereo128 |77.37792|77.31794|77.36440|
| stereo192 |88.11908|88.06342|88.10215|

CPU192 improves by0.05567/0.03873 percentage points against A/A2:
0.06317%/0.04396% relative time, approximately11.13/7.75 us per20ms packet.
CPU128 improves by0.07751%/0.06005% relative time. Worst low-bitrate slowdown
is mono12:0.01128%/0.02879%. Both comparisons pass the saved high-bitrate-first
criterion. Retain as an **experimental post-link ASM recipe**, not board default.
These tiny gains are specific to this corpus/configuration; not a universal
speed guarantee and not a material resolution of audio gaps.

| Input | Max call A us | Max call B us | Max call A2 us |
|---|---:|---:|---:|
| mono12 |7999|8313|8337|
| mono24 |15443|14287|14852|
| stereo64 |16916|17801|16541|
| stereo128 |19608|20039|19963|
| stereo192 |22306|23009|22208|

Worst CPU192:88.24717 /88.14008 /88.17363%. Maximum single call is NOT improved;
candidate23.009ms exceeds a20ms packet. No continuous-output guarantee follows
from average CPU below100%. Free DRAM minima6116 /6836 /8032 B; stack free1660 B
in every group. ELF static RAM/stack and measured codec scratch unchanged.
Allocator fluctuations do not establish a whole-application leak diagnosis.

18 related Node regression tests pass,0 skipped. Includes actual ASM symbolic
bit-origin proof, linked branch/width checks, image validation, all30 rederived
results and ordinary restore. Fresh host parent check11 scenarios has exact PCM
through320/510, mixed modes/PLC/reset/OOM. That host check executes the C semantic
parent, NOT Xtensa MDCT ASM. The five ASM replacements are independently proven
for all32-bit loaded values, pointer parities and live registers; actual board
PCM checks execute the changed code on the five speed fixtures.

Files: comparison.json, controls/before, runs, controls/after, host-parent.json,
preflight.json, patches.s/elf, parent.elf.gz and regression-final.log under the
candidate artifact. No failed/slow attempts removed or replaced.

Normal live512-idle3s app restored OTA, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
HTTP200 root104.45ms (single request, NOT browser rendering measurement), WebSocket
getindex/current167/stopped status and unchanged playlist verified. Free heap27624 B,
min24748 B, web stack2324 B, RSSI-60dBm. The board is stopped as before the test.

**70% goal remains unmet.** Best measured experimental CPU192 is88.06342%; still
about20.5% more decoder-time reduction is needed. No live I2S qualification of
this candidate. Next independent opportunity: paired MDCT table reads without
new RAM or extra stack spills; preserve the in-place post-rotation ordering.
