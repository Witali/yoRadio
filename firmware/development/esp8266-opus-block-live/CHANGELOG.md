# Packed-frame Opus live diagnostic, 2026-09-10

Source `ff49a46`, 885376-byte app, CPU160/QIO40, FIR/ICDF/word helpers,
GPIO3 PDM32, two 512-word DMA buffers. Application-only OTA succeeded;
Wi-Fi, playlist and SPIFFS were not replaced. This is NOT a qualified
continuous-radio build and must not be promoted as a production fix.

DLF24's real packets contain three 20-ms Hybrid frames. They now decode
through the existing 960-sample PCM buffer, with no static RAM growth.
Host regression compared 1728 decoded blocks (1658880 samples) with an
independent full-packet reference: exact. See
[bounded output design](../../../../docs/ESP8266_OPUS_PACKET_BLOCK_OUTPUT.md).

Physical results, all failures retained:

- Run 1: ~27 s window, only 82248 new PCM frames (1.7135 s), 3419 added
  DMA misses. TCP timeout errno116 followed by reconnection.
- Run 2: 28.918 s window, 646216 new PCM frames (13.4628 s), 3355 added
  DMA misses, minimum sampled free heap6252 bytes. Misses also occurred
  during intervals with continuing input, not only after network timeout.
- Minimum observed free audio stack1464 bytes of5120. Not a worst-case proof.
- A later cold decoder initialization hit the post-init reserve guard:
  stage10, free DRAM3840 < reserve4096, detail3900; heap after cleanup27240.
  This does not prove a leak. The reserve was NOT lowered.

Run1 stage values are wall times, including preemption, not pure CPU.
DMA misses count silence fallback descriptors, not their exact duration.
`run1.json`, `run2.json` and `ota.json` preserve raw observations.

Compared with the previous FIR-live image: app +528 bytes;
`.iram0.text`22848, `.iram0.bss`4040, `.dram0.data`1652 and
`.dram0.bss`18504 unchanged. Some call-chain stack frames grew with the
callback wrapper; do not infer unchanged stack from unchanged static RAM.

Follow-up inspection: committed partial DMA descriptors use their exact
byte length; they do not pad the remainder with silence. Silence is emitted
when the next buffer is unavailable. Need stage/deadline profiling and
transport recovery investigation before claiming gap-free Opus playback.
