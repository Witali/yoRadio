# Opus ASM: inner product unroll4

2026-09-14. Candidate `bands-inner4-asm`, parent `bands-tell-inline-asm`.
Status: **rejected** after 30 physical A/B/A runs. Kept only as a reproducible
opt-in diagnostic experiment; not enabled in ordinary firmware.

## Physical result

ESP8266 LX106 160 MHz, QIO40, O3. Median of 10 runs in every column.
A/A2 = best tell-inline control; B = inner4 on the same parent/profile.

| Coded stream, kbit/s | A CPU % | B CPU % | A2 CPU % | B time change vs A |
|---|---:|---:|---:|---:|
| mono12 | 23.085 | 23.128 | 23.096 | +0.188% |
| mono24 | 54.969 | 55.004 | 54.978 | +0.064% |
| stereo64 | 65.318 | 67.061 | 65.326 | +2.669% |
| stereo128 | 77.372 | 81.415 | 77.378 | +5.225% |
| stereo192 | 88.103 | 94.984 | 88.120 | +7.811% |

The 192-kbit/s candidate spends about **1.38 ms more per 20 ms audio** on
average than either control. No high-bitrate speed gain; reject regardless
of the smaller low-rate differences. The 70% CPU goal remains unmet.
The measurements are raw task CPU, not the whole player's load or idle time.
All packets were preloaded into RAM. Wi-Fi remains on; task CPU excludes
other tasks but includes charged ISR and benchmark bookkeeping. Function and
stage profilers, network audio reads, normalizer and physical PDM are off.

All 30 attempts completed with exact PCM hashes and no decoder/observation
errors. No outliers were removed. Maximum wall call at 192 kbit/s:
22592 / 23548 / 23971 us (A/B/A2), including preemption. Different measurement
windows occasionally make task time exceed wall time; all three such records
are retained, not clamped or filtered.

Minimum sampled free DRAM across the five cases: 8168 / 8336 / 6652 bytes.
Minimum free DRAM after benchmark cleanup: 26016 / 26300 / 26300 bytes.
Audio-task lifetime stack headroom: >=1660 bytes in every series.
The maximum scratch use is unchanged: byte scratch 5488 B and word scratch
15600 **bytes**, not words (host mixed/PLC suite byte peak 5968 B).
Transient heap minima are observations, not a guarantee for arbitrary streams.

## Scope and exactness

Only the inlined `celt_inner_prod(X,X,N)` energy loop in
`renormalise_vector` changes. No global compiler unrolling or pitch/PLC
changes. For N >= 8, process complete groups of four, then the original
scalar loop for the remaining 0..3 elements. N <= 0 keeps the original
guard. N 1..7 retains the scalar loop, with one additional threshold branch.

The bulk loop executes 14 instructions for four elements instead of 20.
There are four entry instructions and one tail check. These are instruction
counts, **not an LX106 cycle prediction or an end-to-end speed measurement**.
Paired signed 16-bit loads preserve access widths; nothing reads past N.
Every multiply and accumulation has exactly the original order and low
32 bits, including wraparound. No reassociation, saturation or approximation.

`a4` and `a7` are extra dead caller-saved temporaries. The original live
registers, input memory and SAR are unchanged at the join. Stack remains
32 bytes; no new buffer/table/heap/static RAM. The object function grows
181 -> 233 bytes; linker/image sizes still require separate verification.

## Checklist

- [x] Separate ASM overlay on the best tell-inline parent; C default unchanged.
- [x] Comments describing entry/join registers, tail and fixed-point semantics.
- [x] Actual-instruction tests: 6162 cases, lengths 1..1024/1536/2047/2048,
      extreme int16 inputs, wraparound, 2-byte alignment and read bounds.
- [x] Host ASan/UBSan exact PCM through 192, 320 (2.5/5/10/20 ms) and
      510 kbit/s; PLC/reset/OOM and arena/scratch guards.
- [x] Linked disassembly, same build settings and static RAM/stack.
      Function +52 bytes; app 903216 -> 903280 bytes (+64 including alignment).
      IRAM text 22900, IRAM BSS 4044, vectors 128, DRAM data 1652 and BSS
      18752 bytes remain identical. Flash text +52, flash rodata +4 bytes.
- [x] At least 10 physical A / 10 B / 10 A; retain all failures/outliers.
- [x] Record CPU, maxima and free RAM; rejected against both controls.
- [x] Restore ordinary I2S PDM radio via OTA; verify HTTP/WS/playlist/status.

Speed tests use RAM-resident packets with network audio, PDM and detailed
profiling off. They do not qualify continuous live playback. A successful
candidate needs >=20 seconds of I2S PDM plus WebUI before production adoption.
192 kbit/s is a measurement target, not a decoder bitrate limit.

56 Node tests passed, including the new three inner4 tests. Host PCM error
is zero (SNR relative to baseline: infinity); the host mirror is not used to
claim LX106 timing. Firmware/artifacts: [inner4-v1](../firmware/development/esp8266-opus-bands-inner4-v1/README.md).
Implementation commit: `b6217542`; no default/C fallback changes.

Reproduction:

```text
node tools/esp8266_opus_asm/inner4.cjs <xtensa-lx106-elf-gcc.exe>
node --test tests/esp8266-opus-inner4-asm.test.js
node tools/esp8266_opus_asm/check_bands.cjs inner4
node tools/esp8266_opus_asm/profile_inner4.cjs
```

## Dynamic coverage (host only)

A separate counter build executes one original fixed-point decode per file.
Counters are not linked into either board image. Its PCM also matches exactly.
The five speed fixtures contain 12 packets / 11520 mono output samples:
**0.24 seconds each**, repeated ten times in a physical raw run (2.4 seconds).

| Fixture | Calls / one 0.24-s pass | Calls using bulk path |
|---|---:|---:|
| mono12 | 0 | 0 |
| mono24 | 47 | 47 |
| stereo64 | 62 | 62 |
| stereo128 | 44 | 44 |
| stereo192 | 31 | 31 |

The 192-kbit/s pass visits N=8/16/32/48/64/96/144/176; the exact scalar
loop count is 7560 instructions, candidate 5447, including its entry/tail
checks. Saving 2113 instructions per 0.24 seconds cannot be converted into
an end-to-end CPU percentage without measuring target cycles/cache effects.
This is a relatively infrequent inner product, not the dominant bands/PVQ
operation: about 2.6 calls per 20-ms frame. Future vector-loop candidates
must establish dynamic frequency before choosing the implementation site.

Host coverage also includes 320 and 510 kbit/s. The 320-kbit/s 10-ms file
exercises both bulk and short paths; 2.5/5-ms files do not call this function.
Zero calls in these files is not proof of unreachability for other inputs.

## Linked layout caveat

Only the `renormalise_vector` instruction graph changes. However, its +52
bytes move unchanged `quant_partition` (0x4024dafc -> 0x4024db30),
`quant_band` (0x4024e44c -> 0x4024e480) and `quant_all_bands`
(0x402507d8 -> 0x4025080c). Address/cache effects therefore remain a possible
source of whole-decoder timing changes; this is not a cache-miss measurement.

## Restore

Returned `esp8266-opus-live512-idle3s-20260913` (885552 bytes,
SHA256 `661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b`)
via application-only OTA, slot 0x110000. Ordinary C backend, I2S PDM32,
GPIO3, two 512-word DMA buffers; no raw benchmark. Initial stopped state
retained, no UART reset, SPIFFS upload or Wi-Fi configuration changes.

Native status/audio HTTP, six WebSocket getindex messages and playlist HTTP200
verified. Root HTML HTTP200 in 130 ms (one HTTP request, not a full-browser
load test). RSSI -61 dBm, free heap 27624 B, minimum heap 24748 B,
WebUI stack headroom 2324 B; no reported connection error. A new continuous
20-second playback qualification was not performed for the rejected candidate.
