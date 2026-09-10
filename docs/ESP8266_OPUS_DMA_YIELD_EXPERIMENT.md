# Opus DMA-aware yield experiment: no demonstrated continuity improvement

2026-09-10. Candidate source `bd95aca`, archived under
`firmware/development/esp8266-opus-dma-yield/`. The candidate was tested, then
removed from the active firmware code: it did not demonstrate a useful gain.
The ordinary one-tick post-frame yield is restored. No production default changed.

The candidate omitted the extra Opus frame delay only after that packet had
already spent at least one tick in a successful DMA notification wait. Immediate
or stale notifications, timeout, no-wait packets and MP3/AAC kept the old delay.
Actual DMA acquire host tests covered these cases and tick/counter rollover.
ISR machine code was identical (387 bytes, 151 instructions), IRAM unchanged;
application +256 bytes, persistent counters 12 bytes (DRAM BSS +16 with alignment).

## Physical results

Same own SILK12 signal, CPU160/QIO40, PDM32 batch/IRAM and Opus WordASM ON,
ICDF OFF, two 512-word DMA buffers; sparse health requests about 27 seconds apart.

| Interval | Board ms | PCM ms | New underruns | Result |
|---|---:|---:|---:|---|
| OFF, initial 1 | 27487 | 20388.5 | 2971 | RX timeout/reconnect; not isolated CPU comparison |
| OFF, initial 2 | 29975 | 22242 | 3294 | RX timeout/reconnect; not isolated CPU comparison |
| OFF, after stream restart 1 | 27175 | 20633.5 | 859 | RX timeout/reconnect |
| OFF, after stream restart 2 | 26976 | 27060 | 22 | Full duration, but short gaps |
| ON, steady 1 | 26962 | 27040 | 24 | Full duration, but short gaps |
| ON, steady 2 | 26968 | 27060 | 19 | Full duration, but short gaps |
| ON, own stereo CELT64 | 26970 | 17533.5 | 2169 | RX timeout; incomplete duration |

ON skipped 1337 delays in each steady SILK interval while retaining 15/16
delays. This removes about 49.6 ms/s of requested sleep, **not** 4.96% of CPU
computation. The similar 19–24 underruns do not show a reliable improvement.
No change to decoded PCM or PDM algorithm. 18 local tests passed, including
10 actual-output variants checking 6480 blocks/1841169 words/5670 failure cases
each; PDM paths use ASan/UBSan and a mock DMA sink, not hardware scheduling.

Free heap sampled during ON SILK: 6808–9136 bytes; audio stack watermark 1720,
CELT 1640 bytes. These values do not prove sufficient worst-case heap headroom.
First observed post-OTA health carried reset_reason=7 (`ESP_RST_WDT`), not a
normal software reset. There was no additional uptime/generation reset during
the measured intervals. The precise reset moment during OTA/startup is unknown;
do not attribute it to decoding or this scheduling change without evidence.

Raw reports, including failures, accompany the artifact. No serial operations,
Wi-Fi configuration or playlist upload. Continuous Opus playback remains open.
Next: attribute DMA misses to receive, decode/demux, PCM output and waits using
bounded diagnostic counters; keep these wall-time measurements distinct from
the already saved raw decoder CPU benchmark.
