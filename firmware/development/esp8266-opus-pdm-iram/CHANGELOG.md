# Opus + PDM32 in IRAM — 2026-09-09

Experimental diagnostic application, 881056 bytes, built from the same
stream-only profile as `esp8266-opus-stream-only`, with PDM32 IRAM ON.
CPU160/QIO40; Opus word ASM ON, ICDF OFF; SPIFFS cache OFF; logs OFF;
runtime/raw benchmark OFF; input1024/scratch6144; 2x512 DMA words, GPIO3.
See manifest for source revision, hashes and effective settings.

Whole ELF confirms PDM32 in IRAM and only signed modulo `__moddi3` moved to
flash. Packer remains456 bytes /164 instructions /no calls. Executable IRAM
span shrank504 bytes (alignment differs from the isolated508-byte result).
No codec arena reduction; shared16384-byte requirement is unchanged.
493216 words/states per placement match under UBSan; placement/caller guards
and five focused tests passed. OTA app1→app0 passed.

No continuous-playback qualification: all three25-second tests FAILED.
Local stereo64 produced357768 PCM frames before a transport stall and later
stage8 scratch allocation failure. Real Intense56 also stopped. A separate
local SILK12 control reproduced the same long stoppage despite much lower
pure decoder CPU demand, so CPU overload alone does not explain it.
Local server logged the entire63275-byte SILK file handed to its OS; this
does not prove every byte arrived at the board. Repeated health timeouts
remain in the reports; none were excluded from acceptance.

The early local64 interval has a useful DMA accounting check:
1016ms,44160 PCM frames,163 EOF and71 underrun retries. The retry descriptor
is64 words (1.3312ms), not512; 163−71=92 audio submissions, exactly
46*(512+448) frames. PCM plus71*64 neutral words accounts for1.013s of
physical output, consistent with the observation interval. About9% is
actual short silence, not a dropped second buffer or71 whole-buffer gaps.
This is not a controlled CPU benchmark of PDM placement by itself.

The option remains OFF by default. Next: bounded TCP connect, small
diagnostic phase snapshots for the long stall, ICDF raw A/B and a separate
PDM32 span-fill experiment. These later changes are not in this binary.
