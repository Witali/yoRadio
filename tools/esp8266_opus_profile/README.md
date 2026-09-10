# Fixed-point Opus host regression

See the [whole-decoder optimization audit and checklist](../../docs/ESP8266_OPUS_DECODER_SPEED_OPTIMIZATION_PLAN.md).
`audit_target.cjs` inventories target instruction sites and linked symbols;
it is a static inspection tool, not a CPU profiler. Its saved report is
`target-audit-results.json`. Physical flash-to-DMA results and limitations are
in [the benchmark report](../../docs/ESP8266_OPUS_FLASH_OUTPUT_BENCHMARK.md).

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

`build_host.cjs --fast-int64 0` selects the generic 32-bit arithmetic used by
Xtensa, even on an x86-64 host; `--fast-int64 1` selects native 64-bit arithmetic.
Each explicit selection has a separate `-int64-0`/`-int64-1` build cache.
Without the option the upstream architecture default is unchanged. These Opus
arithmetic branches are not always bit-exact with one another, so board golden
PCM must use `--fast-int64 0`. This changes arithmetic selection, not the host ABI.
A pristine source override must have the same opt-in `#ifndef OPUS_FAST_INT64`
guard in `celt/arch.h`; preserve the original tree and document that sole change.

Reproduce the target-matched reference and the saved generic32 report:

```powershell
node tools/esp8266_opus_profile/prepare_generic32_reference.cjs --source .build/upstream-radio-review-2026-09-09/esp8266audio/src/libopus
node tools/esp8266_opus_profile/run_regressions.cjs --fast-int64 0 --compare-fast-int64 1 --upstream .build/esp8266-opus-pristine-generic32 --output tools/esp8266_opus_profile/generic32-results.json
node --test tests/esp8266-opus-arithmetic.test.js
```

Preparation never changes the original tree. Its default diagnostic destination
is `.build/esp8266-opus-pristine-generic32`; `--output` can select another new
directory. Only the architecture-detection guard is added (line endings in that
edited block become LF). Every source/copy file SHA-256 and sorted-tree digest
is recorded in `opus-generic32-provenance.json`. Repeating preparation verifies
the complete inventory and contents; unexpected changes are rejected, not
overwritten. The source must be an independently obtained pinned upstream tree,
not the adapted vendored component.

The runner accepts `--fast-int64 0/1` and isolates PCM/report outputs under
`.build/esp8266-opus-regression-int64-0` or `-int64-1`. Optional
`--compare-fast-int64 1` also decodes the other upstream arithmetic branch and
records full-corpus and first-12-packet quality, without requiring those two
upstream branches to match each other. Baseline/bounded/pristine equivalence
within the selected branch remains strict, including mixed modes and PLC.
`generic32-results.json` preserves this report; the earlier `results.json`
records the host's original architecture default. For the first 12 hybrid
packets, generic32's FNV-1a32 is `0xbfb8d5fa` (matching the initial board run),
versus native64 `0xcae9facc`: 1,024/11,520 samples differ by at most 1, SNR
84.24 dB. Switching only `vq.c` to generic32 reproduced that difference: normal
`alg_unquant -> exp_rotation -> celt_div -> MULT32_32_Q31` uses the split-product
approximation. This is upstream arithmetic variation, not adaptation error.

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

## CELT phase-buffer reuse

`YORADIO_OPUS_BOUNDED` can lend the current idle PCM output frame to the
second-channel folding buffer (`norm2`). This does not change packet channels,
sample rate, frame size or decoding arithmetic. It is allowed only for mono API
output, stereo-coded CELT, no SILK accumulation, and no downsampling. The callee
also checks the exact folding length. The first folding buffer and X/Y remain
separate. Folding finishes before synthesis/deemphasis writes PCM; earlier
frames of a multi-frame packet are outside the borrowed current-frame range.
For the fixed 48-kHz mode, `N=120*M` and the largest lent region is `78*M`
16-bit samples (1,248 bytes at 20 ms), within the current output frame.

Pitch-based PLC now allocates `fir_tmp` only inside the FIR/copy block. Its scoped
allocator mark preserves `_exc` and the outer channel-loop state, and releases
the copy before IIR. Neither `_celt_autocorr` nor IIR accesses `fir_tmp`. Both
changes leave the ordinary, non-bounded allocation path unchanged.

```powershell
node tools/esp8266_opus_profile/run_phase_regressions.cjs
node --test tests/esp8266-opus-phase-memory.test.js
```

The runner requires the independent reference preparation described above. It
reuses the incremental generic32 objects, then links a host-only wrapper around
`quant_all_bands` to count actual borrowed transient/dual-stereo paths and around
the allocator to permit peak-call tracing. Production objects contain no trace
hooks. Set `OPUS_PHASE_TEST=1` to rerun it from the Node test as well.

Saved `pcm-scratch-results.json` covers the original five fixtures, ten new
deterministic short/multiframe CELT fixtures, mixed modes/PLC, six-loss PLC bursts,
and 8/12/16/24-kHz no-borrow guard cases. Every sample matches independent
pristine generic32 PCM, including a second pass after reset. The focused probe
uses a real 6,144-byte logical scratch limit with a canary immediately after it,
and checks the PCM boundaries and untouched tail after short packets. The
original runner separately retains its forced-OOM/reinitialization checks.

| Host DRAM scratch peak | Before phase reuse | After both changes |
| --- | ---: | ---: |
| Normal 20-ms stereo-coded CELT, mono output | 6,736 | 5,488 |
| Mixed modes/channels plus PLC | 7,216 | 5,968 |

Norm borrowing alone reduced the mixed peak to 6,400; its remaining high-water
allocation was `celt_iir`'s 1,104-sample 16-bit temporary while the obsolete FIR
copy was still live. The word-arena peak remains 15,600 bytes. A 6,144-byte DRAM
arena leaves 176 bytes above this tested corpus peak; this is not a universal
upper-bound proof for every valid Opus stream. Production defaults are a
separate decision. No board throughput or whole-device heap claim is made here.

For a reproducible allocator trace, run the bounded `phase_probe` from its WSL
environment with `OPUS_TRACE_ALLOC=1`; it prints each new peak, request size and
caller address. The probe is linked without PIE, so `addr2line -f -e phase_probe`
can resolve those addresses. `OPUS_PHASE_CAPACITY` selects a diagnostic limit,
`OPUS_PHASE_RATE` selects the test API rate, and `OPUS_PHASE_PLC_BURST` selects
one through eight losses after every eighth packet when `--plc` is supplied.

## ICDF flash-word A/B (default OFF)

### Flash packets with physical output (diagnostic)

`-OpusBenchmarkOutput` requires `-OpusBenchmark -Diagnostic -EnableOpus` and
standard physical I2S PDM32 (not decode-only). It keeps the raw benchmark mode
unchanged when omitted. Each of the five own 12-packet fixtures runs one warmup
and 100 measured rounds: 24 seconds of decoded PCM. Decoder state is reset at
each 240-ms round boundary; the output/DMA is NOT stopped between rounds.
These deliberate PCM segment boundaries are not an analog quality assessment.

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-flash-output -Diagnostic -EnableOpus -OpusBenchmark -OpusBenchmarkOutput -OpusWordAsm -OpusIcdfFlashWord -NoSpiffsCache -Pdm32Iram -Pdm32Batch
node tools/esp8266_opus_profile/run_board.cjs --interval-ms 30000 --output .build/opus-flash-output.json
```

Build does not flash. Deploy explicitly by native OTA before issuing the POST.
Physical mode hashes the decoded PCM BEFORE gain/normalization, then passes it
through the real output API in <=512-sample callbacks, exactly as the native
Opus adapter does. No extra PCM array, audio TCP socket or demux is used. Wi-Fi,
WebUI and OTA remain available. Stop/new station/OTA cancels at a packet or
callback boundary; cleanup silences output and releases the existing four DRAM
blocks and shared word arena on every failure path.

`physical_output=true` identifies this mode. `wall_us` remains decode wall time,
but `task_us` is zero (it must not be mistaken for decoder-only CPU). Separate
`pipeline_task_us` counts full-path task CPU including charged ISR/measurement,
flash copies, checksum and output; `pipeline_wall_us` includes elapsed waits.
`output_wall_us` includes normalization/PDM AND DMA waits, not just conversion.
DMA counters bracket the timed phase after warmup. The strict host gate requires
>=20 seconds, real DMA progress, no missed deadlines, matching decoded/submitted
PCM and elapsed duration. A completed run with gaps exits unsuccessfully and
saves all results; it never qualifies real HTTP-radio playback by itself.
`fifo_empty_seen` also checks the I2S hardware's latched TX-empty flag, cleared
only after warmup and then read without clearing throughout the scored window.
It must stay zero. This detects FIFO starvation even if software had a ready
DMA descriptor. No ISR modification is needed; other profiles that clear this
flag in the ISR are prohibited in this benchmark.
Errors -9008 (output failure) and -9010 (oversized PCM result) supplement existing
allocation/cancel/decoder/golden-PCM errors. Raw benchmark keeps its old timing.

For live read/decode/output/wait attribution and exact 180-second own HTTP
fixtures, see [the live-stage report](../../docs/ESP8266_OPUS_LIVE_STAGE_PROFILE.md).
`run_stage_wall.cjs` retains timeouts and strict continuity failures. Its wall
times are not CPU measurements. A full flash-source decode/PDM/DMA control is
still pending; the existing raw packet benchmark excludes audio output.

The separate CMake option `-DYORADIO_OPUS_ICDF_FLASH_WORD=ON` enables a bounded
decoder experiment in `ec_dec_icdf`. It is independent of
`YORADIO_OPUS_WORD_ASM`. The table address is classified once before either
decoding loop. Constant CDFs in the ESP8266 mapped flash window
`[0x40200000, 0x40300000)` use an aligned word load and byte extraction; ordinary
DRAM CDFs, packet-byte reads and `ec_dec_icdf16` retain their original accesses.
No table is copied to DRAM in production and no persistent RAM is added.

The production builder exposes this as `-OpusIcdfFlashWord`, requiring
`-EnableOpus`. It is independent of `-OpusWordAsm` and `-Pdm32Iram`.
Every builder invocation explicitly passes the CMake option ON or OFF, so
omitting the switch clears a previous ON selection. The artifact manifest
records the boolean `opus_icdf_flash_word` field. For a controlled raw A/B,
use fresh variant names and otherwise identical switches/fixtures; for example:

```powershell
./tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-icdf-on -Diagnostic -EnableOpus -OpusBenchmark -OpusWordAsm -OpusIcdfFlashWord
```

The matching OFF build omits only `-OpusIcdfFlashWord` and uses a different
variant name. The builder does not deploy either image; physical timing and
PCM hashes must be compared separately before claiming a speed improvement.

This relies on the existing internal API contract: valid monotonically
non-increasing CDFs ending in zero. Each accessed byte selects only its own
aligned word; there is no next-word prefetch. Both mapped-region boundaries
are word-aligned, so a valid CDF ending at the final flash byte does not cause
a read beyond the region. This is not an API accepting untrusted CDF pointers.

```powershell
node tools/esp8266_opus_profile/run_icdf_regressions.cjs
node --test tests/esp8266-opus-icdf-word.test.js
node tools/esp8266_opus_profile/check_xtensa_icdf.cjs
```

The host tests execute the real word/extract branch, not the normal host byte
fallback. A Linux/WSL `MAP_FIXED_NOREPLACE` mapping occupies the actual flash
address range, with `PROT_NONE` guard pages outside. A test-only linker wrapper
copies only the executable's readonly CDF tables into this mock region,
preserving bytes through the first zero. Stack/heap CDFs are passed unchanged.
Actual path/load hooks count execution and check each word against the active
table's enclosing words. The mapping is read-only while decoding. Failure to
reserve it is explicit; the test never silently reports byte-fallback coverage.
The wrapper, hooks, mappings and their memory costs do not exist in firmware.

Unit tests compare every entropy context field and bit count against the legacy
implementation for 137,728 symbols. They exercise byte offsets 0 through 3,
CDFs ending at the flash boundary, a final two-byte flash table, exact two-byte
heap/guard-page DRAM tables, and addresses immediately outside both flash
boundaries. The same test passes AddressSanitizer and UndefinedBehaviorSanitizer.
The full 22-scenario corpus requires pristine generic32 PCM equality, actual
word-branch coverage, untouched output guards, repeat/reset equality, and
unchanged scratch peaks. Evidence is saved in `icdf-word-results.json`.

The isolated GCC 8.4 target-object check verifies one address-dispatch branch
outside both loops, `l32i` plus shifts in the flash loop, and the two retained
`l8ui` sites for DRAM CDF and packet data. It also checks unchanged machine code
for `ec_dec_init`, `ec_dec_icdf16` and `ec_dec_bits`. With word assembly enabled
the flash loop has no `memw`; otherwise the existing volatile-word fence is
retained. The `ec_dec_icdf` stack frame is 32 bytes versus 16 bytes before this
experiment (+16 bytes); static RAM remains unchanged. No physical speedup is
claimed until a separate board A/B holds the firmware and packet corpus fixed.

## SILK FIR word pairs

`-OpusFirFlashWord` in the firmware builder enables the default-off exact
four-word/eight-coefficient FIR experiment. It requires `-EnableOpus`.
The host runner accepts `--fir-word --fast-int64 0`; its candidate binary
uses a separate cache directory. FIR ASan/UBSan, target alignment/stack and
saved PCM checks: `node --test tests/esp8266-opus-fir-word.test.js`.

Ten raw-only board runs per profile are archived with their application
binaries, manifests and OTA records. Reproduce the strict comparison:

```powershell
node tools/esp8266_opus_profile/compare_raw.cjs --reference firmware/development/esp8266-opus-fir-off-raw --candidate firmware/development/esp8266-opus-fir-on-raw --output .build/opus-fir-comparison.json
```

It verifies hashes/configurations and keeps slow runs and observation errors.
An incomplete run or changed PCM is a failure, not a discarded sample.
SILK/Hybrid speed improved; physical-output and live continuity remain unproven.
See [results and limitations](../../docs/ESP8266_OPUS_FIR_WORD_BENCHMARK.md).
