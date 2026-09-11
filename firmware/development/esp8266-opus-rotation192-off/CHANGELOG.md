# CELT LX106 rotation: matched raw control

2026-09-11, source05eff07, app902928B. Diagnostic only, not a release.
Matched candidate: ../esp8266-opus-rotation192-on, differing only in
OpusRotationLx106. CPU160/QIO40, FIR/ICDF/word helpers ON, DivOnce and
CeltDecodeOnly OFF. Input1024B/scratch6144B, standard GPIO3 PDM32/512x2
configuration; the raw benchmark itself neither plays PCM nor reads audio
from the network. Wi-Fi/WebUI remain enabled.

Five own12/24/64/128/192-kbit fixtures,12 packets per round,10 measured
rounds plus warmup. Decoder reset per round; expected PCM and samples
checked each round. No runtime bitrate cap. Task CPU includes charged ISR
and timing bookkeeping, not just isolated instruction cycles.

Build and paired manifest checks passed. Both targets have static
IRAM vectors128B/text22900B/BSS4044B, DRAM data1652B/BSS18784B. The DMA
ISR is387B and its section hash is identical. Rotation ON changes flash
text637042→636658B; rodata remains241116B. This is not a heap/stack bound.

Host rotation checks passed for512 vectors/78880 samples against the actual
ASM instruction model, with C ASan/UBSan and preserved call0 registers.
This is not physical execution or a speed result. Physical10+10 raw runs,
followed by flash→PDM and real-radio continuity, are still required.

After application-only OTA and confirmed slot change:

```powershell
tools/esp8266_opus_profile/run_raw_series.ps1 -Directory firmware/development/esp8266-opus-rotation192-off -Fixtures .build/esp8266-opus-board-through192 -Attempts 10
```

Physical series completed: ten terminal runs, exact PCM, no observation errors.
Median raw CPU:23.480/55.377/63.886/76.289/88.555%. These are decoder-only
measurements, not continuous output. The matched universal ASM candidate was
slower for CELT; see its comparison.json. Earlier pending statements above
describe the build-time state, before these saved runs.

Every attempt remains runN.json/log, including failures. Unknown state or
invalid PCM stops the series; do not silently restart or replace results.
See [the rotation contract](../../../docs/ESP8266_OPUS_ROTATION_ASM.md).
