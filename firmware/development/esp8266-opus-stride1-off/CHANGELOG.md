# Opus stride1 v2: matched C control

2026-09-11, source3aeac48, app902928B. Diagnostic raw benchmark, not a release.
CPU160/QIO40; word/ICDF/FIR helpers, PDM32 IRAM batching and SDK RX diagnosis
enabled. Rotation ASM, DivOnce, CeltDecodeOnly and PCM publication OFF.
Input1024B/scratch6144B. GPIO3 PDM32 DMA512x2 profile, but raw measurement
does not output PCM and does not receive audio from the network. Wi-Fi/WebUI
remain enabled; task CPU includes charged ISR/instrumentation.

Five own12/24/64/128/192-kbit fixtures,12 packets per round,10 measured rounds
plus warmup. Decoder resets per round; not one continuous playback history.
Header SHA256 cd3d55d30806bd143810cb6ec56e34db69956c7ccb011f46f85ae2aac5d65d7a.
Use ten numbered attempts; retain all failures/outliers. No bitrate cap.

Matched candidate ../esp8266-opus-stride1-on differs only by rotation flag.
Static IRAM vectors128/text22900/BSS4044, DRAM data1652/BSS18784, rodata241116.
DMA ISR387B, same hash914cdfe2fb0863ba26c726ebbd1465133695f4043614969be3f849c85a6cba00.
C exp_rotation1/exp_rotation/alg_unquant object instruction sections match
the previous rotation192-off control byte for byte. Physical10 runs complete:
exact PCM, no observation errors, all failures/outliers retained. CPU medians
23.479/55.368/63.842/76.249/88.524 percent; dynamic DRAM minimum7612B,
stack headroom1660B. One timing-window excess retained in comparison.json.
Matched ASM candidate slowed CELT8.42/9.23/8.65%; default stays C.

```powershell
tools/esp8266_opus_profile/run_raw_series.ps1 -Directory firmware/development/esp8266-opus-stride1-off -Fixtures .build/esp8266-opus-board-through192 -Attempts 10
```
