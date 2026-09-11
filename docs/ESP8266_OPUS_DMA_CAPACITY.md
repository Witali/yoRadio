# Opus: diagnostic DMA capacity experiment

2026-09-11. Default remains two512-word buffers. Diagnostic-only
`-DmaBufferWords 768` keeps ping-pong ownership and adds2048B static DRAM;
no third buffer, decoder workspace change, PCM/PDM approximation or IRQ masking.
CMake rejects this outside diagnostic Opus standard I2S PDM32. A768-word
descriptor holds3072B, below the12-bit4095B hardware length limit.

At48kHz, total capacity rises21.33→32ms (one buffer10.67→16ms).
This is capacity, not a guarantee both buffers are full before every decode.
The retained short-neutral retry, partial publication and decode callbacks
mean actual queued audio can be shorter. No expected speedup of the codec.

## Evidence motivating the experiment

Live C profile esp8266-opus-publish-off, HTTP radio.plaza.one/opus:
one28s health interval yielded26.44s PCM,1252 new DMA misses, heap7192B.
Decode-exclusive wall time76.98%, output16.37%, read3.62%, post-decode
wait2.63%, input-wait0.027%. Maximum decode call since boot29.816ms.
These are wall timings including preemption, not pure CPU or an analog test.
[Unfiltered report](../firmware/development/esp8266-opus-publish-off/live-plaza-recheck-1.json).

This interval supports testing output headroom; it does not prove a global
network or decoder cause, nor that larger DMA buffers can fix average overload.
Keep the decoder reserve gate, verify lowest live DRAM, WebUI and switching.

## Qualification

- [x] Parameterize two DMA capacities; preserve production512 and constraints.
- [x] Host PCM/PDM sequence, ownership/EOF/stop/cancel and configuration tests:
  14/14 passed, no skips; six output/capacity variants, six sample rates,
  mono/stereo and normalization on/off. Host is not physical timing evidence.
- [x] Matched builds and static memory comparison.
- [x] Physical matched10 attempts each, retain failed starts and observations.
- [ ] At least20s continuous real Opus station, no new DMA underruns and
  PCM elapsed duration matching wall time. Do not discard network failures.
- [ ] Promote only if continuity and RAM safety improve; otherwise keep default.

Build example: existing diagnostic live Opus flags plus `-DmaBufferWords 768`.
The default loan option512 means no artificial cap, as before; shorter loan
options64/128/256 retain their separate meaning and are not part of this A/B.

## Board results: NOT qualified

Each series uses `run_live_series.cjs`,10 requested starts,5s startup allowance,
then a25s requested sparse health/profile window (normally27..28s actual).
Source is HTTP `radio.plaza.one/opus`, advertised64kbps. No PC adapter changes,
UART commands or serial resets. OTA is recorded with each artifact.

| Variant | DMA words/buffer | Idle deadline | Qualified / attempts | Playing in startup status | Missing profile windows |
| --- | ---: | ---: | ---: | ---: | ---: |
| dma512-live | 512 | 1000ms | 0/10 | 5 of9 obtained statuses | 7 |
| dma768-live | 768 | 1000ms | 0/10 | 0 of5 obtained statuses | 3 |
| dma768-idle3s | 768 | 3000ms | 0/10 | no startup statuses obtained | 4 |

All failures/timeouts remain in `firmware/development/esp8266-opus-<variant>/`.
Unavailable statuses are not treated as proof that playback never started.
Likewise, neutral-output EOF/underrun counters while stopped are not useful
measurements of playing continuity. Such windows explicitly fail qualification.

The first512 run DID sustain decoding across28.219s, but only26.960s PCM
progressed (95.54%), with1046 new DMA misses. Sampled free heap was6392B;
startup min-heap was5712B. Later starts included Decoder Init Error, response
timeouts and a boot-lifetime min-heap3124B. The lifetime minimum must not be
presented as a per-window measurement or as proof of a leak.

The768 increase costs2048B static DRAM. All other RAM sections are equal:
DRAM data1652B, BSS18520 ->20568B; IRAM vectors128B/text22848B/BSS4040B.
Apps885520 ->885536B; ISR387B in both, but hashes differ (constants/addresses).
Its10-attempt series failed; observed startup min-heap reached3080B. No reason
to promote768 to production: the larger payload capacity did not qualify and
reduced the already tight RAM margin.

An independent30s PC connection recorded7 inter-arrival gaps>=1s out of94,
max1067.185ms (`dma768-live/plaza-pc-arrivals.json`). This motivated the3s
control, not a claim that the ESP saw the same arrivals. That control ALSO
failed10/10. In its first trace only16968 PCM frames had progressed before
receive timeout116; the later interval made no progress. Increasing the idle
deadline alone is therefore not a demonstrated fix.

Next: [PCM queue and explicit ownership](ESP8266_OPUS_PCM_QUEUE.md), together
with investigating receive/reconnect memory pressure. Keep512 as the default;
do not reduce the reserve guard to turn failed decoder starts into successes.
