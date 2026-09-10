# Selected CELT stage profile, 2026-09-10

Source17b1f2f, app912960 bytes, CPU160/QIO40. Diagnostic raw decoder
benchmark, `OpusProfileStage=8`, FIR/ICDF/word optimizations, no audio
network/normalization/PDM during the measurement. Wi-Fi and WebUI stay on.
Five own tone/noise fixtures,120 packets/2.4 seconds PCM per case, each run
includes ten measured rounds and a warmup. History resets every round.

All ten attempts completed with correct PCM. No result was discarded.
Polling interval30 seconds reduces observer interference; it does not turn
this into a Wi-Fi-off benchmark or guarantee a safe RAM reserve.

| Input | Task CPU median | Bands/PVQ share of decode wall time | Maximum single bands scope |
|---|---:|---:|---:|
| SILK12 | 23.44% | 0% (not used) | 0 |
| Hybrid24 | 58.45% | 12.79% | 4.015ms |
| CELT64 | 75.97% | 51.47% | 15.872ms |
| CELT128 | 96.38% | 61.63% | 23.454ms |
| CELT510 | 172.91% | 78.34% | 49.832ms |

Stage wall time includes interrupts/preemption, not exclusive CPU. Task
time includes instrumentation and charged ISR. This is not a speedup A/B
against the earlier stage0 series: clock/serialization/source and observer
interval changed. In that separate stage0 series the medians were24.47%,
58.62%,71.51%,94.07%,169.57%. All its ten attempts are also preserved under
`esp8266-opus-stage-prior-control`.

Run6 reached only1052 bytes free DRAM (1932 on CELT510); it is retained and
the4096-byte RAM-safety gate is **failed**. Other runs sampled8032 bytes or
more. Minimum lifetime free audio stack1564/5120. No claim of leak freedom
or production safety. Frequent polling in the rejected earlier series
also caused transient pressure; heap later recovered without a USB reset.

Target cost versus stage0: +128B `.dram0.bss`, +464B flash text, +176B flash
rodata; IRAM/data unchanged. The selected CELT entry remains464B stack,
clock helper32B. Stage0 instructions in the three touched translation units
match pre-instrumentation exactly. No extra PCM or packet buffers.

128 empty SDK clock pairs per run: minimum1us; maxima across runs5..2920us
(median13us), including preemption. Nothing is subtracted from timings.

The CCOUNT and printf attempts are separately archived as rejected. Their
stage durations must not be mixed into this series. See
[method and caveats](../../../../docs/ESP8266_OPUS_STAGE_PROFILE.md).

Next: decoder-only specialization of CELT bands and exact division/rotation
work there; independently profile SILK core and CELT synthesis for Hybrid.
This benchmark does NOT establish continuous physical radio playback.

## Live restoration and failed follow-up

Restored `esp8266-opus-block-live`, sourceff49a46, via app-only OTA to0x10000.
No benchmark/profile counters in that live image, no SPIFFS/Wi-Fi/playlist
upload. DLF24 started late: first25s test crossed the startup format change
and is not a steady-state interval. It did produce1057496 PCM frames by
the second snapshot, but the continuity gate failed.

A later25s window had no new input or PCM, timeout errno116, then
DECODER INIT ERROR. The preserved snapshot identifies stage8 (scratch
allocation failure): free10220B, request6144B, reserve4096B. Correction after
source audit: the reserve check is stage10, not stage8; the earlier claim
that this was a reserve-guard rejection was incorrect. Total CAP8 free size
does not establish the largest contiguous free block, so fragmentation or
transient system allocations remain possible, not proved. Even a successful
6144B allocation would leave less than4096B CAP8 before allocator overhead.
The current stage10 guard uses combined heap, which must be audited separately
from the stricter DRAM reserve. No reserve was lowered. After cleanup current
DRAM26992B; this does not prove a leak. RSSI at final status−48dBm.

Playback explicitly stopped after the failed test. Final live firmware
responds over HTTP and remains installed; continuous Opus audio is still
unresolved. Both windows, init failure, OTA and stop responses are retained.

Recompute from all files, verifying the application hash:

```powershell
node tools/esp8266_opus_profile/summarize_stage.cjs firmware/development/esp8266-opus-stage-sdk-bands firmware/development/esp8266-opus-stage-sdk-bands/summary.json
```
