# Diagnostic Opus live-join/cache-off — 2026-09-09

Application 907904 bytes; SHA-256 and source9d4310d in manifest.
CPU160/QIO40; I2S PDM32 GPIO3, 2x512 words; input1024/scratch6144.
Private word ASM ON. The separately developed ICDF word experiment was
present in the checkout but explicitly OFF in this build's CMakeCache.
Raw Opus benchmark ON; SPIFFS read/write caches OFF; logs OFF.
This is an experimental diagnostic build, not a production qualification.

Target build and IRAM/flash instruction guards passed. OTA switched app1
to app0 successfully, without serial access or filesystem replacement.
The real Intense 56-kbit/s source now reaches actual PCM and `playing=true`;
an observed snapshot reported heap6672, minimum5276, and no playback error.
It subsequently disconnected/reconnected: 662044 cumulative PCM frames
(about13.8seconds of PCM, not proof of a continuous interval), followed by
a failed6144-byte scratch allocation despite9636 total free DRAM. Total
free space does not guarantee a sufficiently large contiguous allocation.

The following local40-second synthetic64-kbit/s trial also failed: its
observed25-second window had no PCM progress, and the final diagnostic
showed reserve-gate failure (3852 free DRAM, required4096). These failures
are preserved in local-continuity-results.json and local-state-results.json.
Do not infer audible continuity from successful raw decoding or playing=true.

SPIFFS cache A/B, stopped radio:10 HTTP requests each for root, settings and
playlist in both modes. All30 cache-off responses were200 and byte-identical
to cache-on responses. Mean times ON/OFF: root106.5/108.0ms,
settings105.1/107.0ms, playlist73.8/71.6ms; worst cache-off114.1ms.
These are complete individual HTTP transfers, not full browser rendering,
uploads, or simultaneous playback validation. See paired web-cache reports.

Next: remove raw-benchmark RAM overhead from stream-only diagnosis, inspect
transport stalls/reconnect allocation fragmentation, and rerun continuous
PCM/DMA checks. The4096-byte reserve and5-KiB audio/web stacks remain intact.
