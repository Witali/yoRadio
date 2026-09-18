# Full Opus ASM radio: reconnect lifetime / DRAM reserve

2026-09-18, source156f5c0a, CPU160/QIO40. Normal native player with WebUI,
I2S PDM32 GPIO3 and diagnostics, not a raw decoder benchmark. All18 accepted
eBands-final ASM stages; no pending SRC or rejected quant experiment.

- Preserve Opus allocation across the second bounded non-memory open
  attempt; still free on Stop/final failure/codec replacement/memory pressure.
- Check actual byte-addressable DRAM for Opus's4096-B safety reserve.
- Input2048B, scratch6144B, PCM2x960, DMA2x128 words, prior clock/network
  settings and LEDoff unchanged. Zero static-RAM increase.
- Application890352 B (+80), SHA256
  `dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`.
- OTA200/OK, running slot0x110000 ->0x10000 confirmed. No SPIFFS/partition
  writes, UART access or default-profile change.
- 19/19 memory tests, ten sanitizer reconnect repetitions and5/5 server
  tests passed. Target recovered from all10 injected HTTP503 failures;
  init failure stage remained0.
- NOT reliable-audio qualified: later regular local playback stalled with
  CONNECTION ERROR, DMA underruns and one15-s WebUI status timeout. Post-Stop
  DRAM26288..26464B stayed stable over60s but below pre-test; further trace
  needed. All failures retained. Board left stopped on this image.

[Full evidence](../../../../docs/ESP8266_OPUS_MEMORY_RECONNECT_2026-09-18.md).
