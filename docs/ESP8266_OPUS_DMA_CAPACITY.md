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
- [ ] Matched builds and static memory comparison.
- [ ] Physical matched10 attempts each, retain failed starts and observations.
- [ ] At least20s continuous real Opus station, no new DMA underruns and
  PCM elapsed duration matching wall time. Do not discard network failures.
- [ ] Promote only if continuity and RAM safety improve; otherwise keep default.

Build example: existing diagnostic live Opus flags plus `-DmaBufferWords 768`.
The default loan option512 means no artificial cap, as before; shorter loan
options64/128/256 retain their separate meaning and are not part of this A/B.
