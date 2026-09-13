# Experimental Opus ASM library — 2026-09-13

- Full GCC 8.4 / O3 / LX106 call0 / fixed-point snapshot: 110 units, 229 functions.
- Standalone `libopus-gcc-asm.a`; optimized `libopus-optimized-asm.a` replaces
  only ec_dec_update. Original upstream license is in COPYING.
- ASM round-trip checks instructions, relocations and section contents.
- Candidate: ec_dec_update 171 -> 107 code bytes, local stack16 -> 0;
  no additional persistent/scratch buffers, allocated task stacks unchanged.
- correctness.json: 100000 unit states, complete PCM model comparisons and PLC.
- build-comparison.json: full linked images, equal RAM/IRAM sections.
- CPU speed and real LX106 PCM are NOT yet device-qualified. No OTA performed.
- Archives require the existing native opus_memory allocator hooks and target
  libgcc/libc; they are not directly flashable firmware images.
