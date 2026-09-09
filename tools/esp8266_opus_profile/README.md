# Fixed-point Opus host regression

This harness decodes the committed synthetic corpus to 48 kHz signed 16-bit
little-endian **mono** PCM, including stereo-to-mono decoding. It compares the
vendored decoder with `YORADIO_OPUS_BOUNDED` undefined and enabled. The optional
pristine source comparison also detects changes to the ordinary macro-off build.

Run from the repository root with Node.js and GCC. Windows uses `wsl.exe --exec`
and the GCC installed in WSL; no serial port or ESP8266 is accessed.

```powershell
node tools/esp8266_opus_profile/run_regressions.cjs
node tools/esp8266_opus_profile/run_regressions.cjs --no-build
node tools/esp8266_opus_profile/build_host.cjs --bounded tests/fixtures/opus_native/stereo-510.opuspkt
```

The first run compiles separate baseline and bounded objects with four workers.
Later runs use GCC dependency files plus source/header timestamps and a
compiler/flags signature, recompiling changed objects and relinking only when
needed. `--no-build` explicitly trusts the existing executables; use it only when
sources have not changed. Builds and decoded PCM go under `.build/`.

For an independent pristine copy of the pinned upstream sources:

```powershell
node tools/esp8266_opus_profile/run_regressions.cjs --upstream .build/upstream-radio-review-2026-09-09/esp8266audio/src/libopus --output tools/esp8266_opus_profile/results.json
```

`--upstream` accepts the path containing `src`, `celt`, `silk`, and `include`.
It compiles that tree without the bounded macro into its own cache. The pinned
source for the checked-in report is ESP8266Audio commit `10d929ac`; its full
provenance is recorded by the decoder component. The default generated report is
`.build/esp8266-opus-regression/results.json`; `results.json` beside this README
is the saved complete validation evidence, including PCM SHA-256 hashes.

The runner requires exact PCM, records mismatch count, maximum absolute error
and SNR (`"Infinity"` for no error), and checks every fixture's SHA-256, decoded
sample count, and packet TOC modes. Every fixture also exercises a warmed decoder
reset against fresh PCM, arena boundary guards, forced `OPUS_ALLOC_FAIL`, and
successful reinitialization after OOM. The wrapper may partially update decoder
state before OOM; callers must reset/reinitialize it before reusing it. The probe
rebinds the arenas and calls `opus_decoder_init` before recovery decoding.

The bounded probe uses 7,680 bytes of byte-addressed scratch and a 16,384-byte
word arena, matching the experimental profile limits. Word-arena high-water marks include
persistent CELT history and SILK excitation. Host state sizes depend on host pointer/alignment rules.
These measurements exclude packet and PCM buffers, native bridge allocations,
call-stack usage, and SDK/Wi-Fi memory. They establish PCM equivalence and arena
usage for this corpus, not physical ESP8266 speed or deadline compliance.

After building the ESP8266 Opus component, run
`node tools/esp8266_opus_profile/check_xtensa_iram.cjs` to inspect the actual
Xtensa object code. It checks that pitch interpolation never narrows reads of
its IRAM correlation array and that band denormalization/PLC history zero fills
call the word-safe helper instead of compiler-generated ROM `memset`. The same
checks run in the Node tests when target objects and the SDK disassembler exist.
They reject stale target objects and accept explicit `--object`/`--objdump`
paths. These guards cover the identified regressions, not every IRAM access.

Run the checked-in evidence/corpus tests with `node --test
tests/esp8266-opus-memory.test.js`. To additionally execute GCC and the actual
decoders in that test:

```powershell
$env:OPUS_HOST_TEST = '1'
node --test tests/esp8266-opus-memory.test.js
```

`OPUS_HOST_NO_BUILD=1` reuses existing binaries; `OPUS_HOST_UPSTREAM` optionally
adds a pristine tree. Packet duration admission (2.5/10/20 ms, rejection above
20 ms) belongs to the native adapter tests, not this raw libopus probe.
