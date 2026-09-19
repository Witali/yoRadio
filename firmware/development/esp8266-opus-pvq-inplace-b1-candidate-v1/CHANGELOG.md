# Experimental PVQ in-place B=1 ASM — 2026-09-19

Not a production release. App-only OTA image, CPU160/runtime QIO40, raw
Opus RAM-packet benchmark, no audio output or function/stage profiling.

- Parent: accepted `esp8266-opus-ebands-final-candidate-v2`.
- Direct int16 pulses in X for B=1; removes temporary iy/arena calls.
- Original paths for other B/K, bitrates unrestricted, old C fallback intact.
- Fixed section sizes, same app size 903216 B, static RAM and stack unchanged.
- App SHA256: `8f696562ce88c6f013ab57c4770bcf877d3d4ed15b06c725eaa56a3f3331b3c4`.
- Local PCM/ISA proofs passed; all150 board PCM hashes exact in30 A/B/A runs.
- REJECTED: CPU192 A/B/A2=77.878188/78.883083/77.870771%; no peak RAM gain.
- Ordinary I2S PDM radio restored by OTA. Full measurements and final decision:
  [experiment report](../../../docs/ESP8266_OPUS_PVQ_INPLACE_ASM.md).

Do not use this benchmark image as ordinary radio firmware. Restore the
ordinary firmware after measurement; no UART commands/reset on GPIO3.
