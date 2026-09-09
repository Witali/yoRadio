# libopus decoder for ESP8266 native

Imported from ESP8266Audio commit `10d929ac01436dfe8856e0a06fd9ec35a848c6e2`,
`src/libopus` (Xiph libopus 1.5.2, fixed-point decoder subset).
Source: https://github.com/earlephilhower/ESP8266Audio/tree/10d929ac01436dfe8856e0a06fd9ec35a848c6e2/src/libopus

Licenses and attribution: `upstream/COPYING`, `upstream/AUTHORS`,
`upstream/LICENSE_PLEASE_READ.txt` and individual source notices.
No Arduino wrapper, encoder API, libogg or libopusfile dependency is used.

YoRadio adaptation (compile-time `YORADIO_OPUS_BOUNDED`):

- Separate 32-bit CELT history from byte-addressed state, so the former can
  live in the existing shared codec IRAM arena. LPC/energy tails stay in DRAM.
- Replace variable-length task-stack allocations with bounded, reusable
  scratch arenas. Allocation failure unwinds to a checked decoder entry;
  no unchecked pointer, task-stack expansion or per-packet malloc.
- Use word-sized copy/clear/move for typed 32-bit buffers, avoiding byte
  accesses to ESP8266 IRAM. All arithmetic remains upstream fixed-point.
- Original layout and C99 VLA path remain available for host A/B regression.
- Automatic IRAM scratch is restricted to CELT translation units; SILK uses
  an explicit allowlist for sLTP_Q15/res_Q14 only. Its libc byte-copy arrays
  remain in DRAM. SILK/CELT stage lifetimes reuse the same scratch storage.
- Skip unused 48-kHz deemphasis scratch, scope prefilter scratch, and remove
  decoder-unreachable encoder RDO stack storage in bounded builds.
- Force a full-width volatile read of SILK sLTP_Q15 during gain rescaling:
  Xtensa GCC 8.4 otherwise emits l16si for part of an int32 SMULWW operand.

The adapter is single-decoder/single-audio-task, like the existing MP3/AAC
arena. It must be opened only after the preceding codec has been released.
See the project Opus integration documentation for limits and test results.
