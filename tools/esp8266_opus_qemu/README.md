# Offline ESP8266 Opus qualification

This runner executes the accepted linked LX106 decoder in QEMU `sim/lx106`.
It verifies ELF and input hashes, exact PCM, arena guards, bounded scratch OOM
and recovery. It never opens a serial port, uses OTA or changes the board.

From the repository root:

```powershell
node tools/esp8266_opus_qemu/run.cjs --fixture stereo-192
node tools/esp8266_opus_qemu/run.cjs --extended
node tools/esp8266_opus_qemu/suite.cjs --output .build/opus-qemu-qualification
node --test tests/esp8266-opus-qemu.test.js
```

The suite selects only the accepted `esp8266-opus-ebands-final-candidate-v2`
artifact already included in `main`. It checks the extended mono/stereo,
12–510 kbit/s, mixed-mode and packet-duration corpus, profiles seven inputs,
replays the 192 kbit/s trace and requires an intentionally damaged canary to
fail. A suite output directory must be new and inside this checkout. Its
inventory hashes cover saved inputs, reports, compressed output and traces.
Experimental N3/N4 firmware and A/B recipes remain on the research branch.

Requirements: Node.js, QEMU with `sim/lx106`, Xtensa LX106 GCC 8.4 and fetched
Git LFS artifacts. The default tool locations match this project's Windows
installation. `run.cjs` accepts `--qemu` and `--toolchain` overrides. Extended
checks also require FFmpeg/libopus and GCC with ASan/UBSan (through WSL on
Windows), as used by the existing host decoder tools.

QEMU checks instruction semantics, not ESP8266 clock cycles, flash/cache
latency, Wi-Fi, I2S continuity or full firmware RAM headroom. ROM calls use
explicit functional substitutes; the IRAM word-only access rule still needs
the existing static checks. The extra PCM oracle uses vendored generic32 C
under sanitizers; it is not an independent pristine decoder. No new radio
firmware is built by these commands.
