# ESP32-C3 codec optimization review

Date: 2026-10-23. Source reviewed: main `51cd114f9`.
Scope: native ESP32-C3 OLED firmware; ESP8266 work is a source of algorithmic
ideas, not transferable instruction timings or assembly.

This is a source/evidence review and an experiment plan. No new firmware was
built, benchmarked or flashed. Proposed savings below are unmeasured unless
explicitly attributed to a retained experiment.

## Baseline to preserve

The [October 15 acceptance](ESP32C3_PRODUCTION_ACCEPTANCE_20261015.md) identifies
the qualified binary, SDK revision and 145 passing campaign/post-install checks.
It does not automatically qualify a rebuild of today's main.
Use `build-production.ps1 -TestedRadioProfile` when reproducing that configuration;
generic `sdkconfig.defaults` alone does not enable every accepted option.

The accepted configuration includes QIO 80 MHz, fractional nominal 48-kHz output,
output task priority above decoding, full-rate compact AAC/SBR/PS with PC19 high
history, a 17,058-byte TLS RX reserve, bounded input slots and tail coalescing.
Shared decoder arena, direct DMA PCM and bytewise Rice are still experiments,
not recommendations to enable globally.

Preserve supported rates, channels, AAC profiles, transitions, EOF and recovery.
Storage/control optimizations should retain exact current PCM. Further lossy AAC
storage changes must remain within 3 signed-16 PCM LSB against the full-precision
reference on the qualification corpus. Separate per-array passes are insufficient:
the combined implementation must pass. FLAC reconstruction remains lossless before
the existing output conversion.

## Priorities by codec

| Codec | Evidence and existing work | Next useful experiment | Expected kind of benefit / uncertainty |
| --- | --- | --- | --- |
| HE-AAC / HE-AAC v2 | Compact owner, low-QMF call-local workspace, asymmetric ownership, smoothing storage and PC19 are implemented | Batch high-history metadata loads/stores without changing rounding; profile packing separately from QMF and PS DSP | CPU reduction while retaining current RAM savings; no measured new percentage |
| FLAC | Custom decoder already skips trailing zero LPC coefficients, uses sparse rolling prediction when profitable, and groups four taps; Rice/LPC dominate the retained host profile | Test the existing no-auto-unroll LPC variant alone on C3; then investigate a bounded word-oriented Rice reader | CPU/cache footprint; keep bytewise Rice disabled after its physical regression |
| Opus | Vendor backend; old isolated fixture had the largest decoder CPU share among the five basic codecs | Profile entropy/PVQ, transforms and SILK separately; transfer only reachable, exact algorithmic simplifications from ESP8266 work | Potential CPU benefit; current internal stage ranking and source equivalence are unverified |
| Vorbis | Allocation failure cleanup and output retry/EOF repairs are implemented | Attribute codebook/residue/MDCT cost and live memory first; then reuse only non-overlapping scratch lifetimes | CPU and peak RAM; preserve overlap history, pending packets and final samples |
| AAC-LC | Uses the shared AAC path, including late SBR discovery | Measure core transforms and PCM publication; reuse scratch only after a reader/lifetime audit | Lower priority than HE; an LC start must retain the ability to become HE/PS |
| MP3 | Espressif backend won the retained three-backend comparison | Optimize common PCM handling first; consider backend work only after a new matched profile | Lower priority; switching backend is not an established improvement |

### HE-AAC: accelerate the compact representation first

In `main/aac_high_history.c`, `aac_high_history_memmove()` traverses history pairs
and invokes `unpack()` or `pack()` per pair. PC19 metadata includes a context side
array with 16 pairs per word. Test grouped loads and stores at the actual packing
boundaries, avoiding repeated read/modify/write of a shared metadata word.
Inspect optimized assembly first: the compiler may already remove some loads.

Keep identical saturation, ties-away-from-zero rounding, real-only preservation
of imaginary history, and channel/context ownership. Handle partial groups and
reset explicitly. Compare all PCM against the existing PC19 implementation first,
then against the full-precision reference, including late, missing and resumed SBR.
Do not introduce a second persistent unpacked cache without measuring reuse: this
path already expands history into working arrays for the native DSP call.

The [PC19 experiment](ESP32C3_AAC_PC19_20261004.md) measured owner-plus-adapter
allocation of 32,960 B versus 51,232 B for its already partially compact reference:
18,272 B saved in that comparison. This excludes the AAC core, stack, input and PCM;
it is not a new saving or a total-radio RAM figure. Its retained recordings reached
2 LSB peak error. Earlier PC18 reached 5 LSB in missing-SBR tests and must not
replace PC19 merely to save 144 allocated bytes.

The low-QMF wrapper still copies persistent history into and out of its scoped
matrix. Removing these copies would require changing native consumers or their
address layout. This is a later lifetime/ABI experiment, not a safe memcpy deletion.
See [workspace ownership](ESP32C3_AAC_LOW_QMF_WORKSPACE_20261003.md).

### FLAC: distinguish promising code size from proven speed

The [host hot-loop profile](ESP32C3_FLAC_HOTLOOPS_20261008.md) attributes 82-86%
of exclusive decoder CPU to residual decoding plus prediction on its recorded
LPC12/LPC32 corpus. Those percentages describe x86, not C3.
`FLAC_LPC_NO_AUTO_UNROLL=1` reduced the RV32 relocatable object by 706 B in that
experiment; four explicit taps remain. Benchmark this independently before
combining it with a new reader. Object size does not equal linked application size.

The [physical bytewise Rice comparison](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md)
was slower by 2.68-10.10% in elapsed decode time/audio second across three FLAC
cases, despite a 176-byte smaller application. Both heavy HTTPS images had
watchdog faults. Keep that rejected result visible. ROM CLZ is not by itself
proven responsible; call boundaries, spills and cache layout also changed.

For a new word reservoir, test refill boundaries, short inputs, long unary runs,
Rice escape partitions, truncation and overflow before timing. Any narrow LPC
accumulator path needs a proved bound using sample width and coefficient magnitude,
with the existing wide path as fallback. Mid/side decoding can need additional
width. Never discard LPC32 or high-depth support to improve a benchmark.
The adapter's input compaction (`memmove`) is another measurable candidate;
a read offset may reduce copying, but must preserve contiguous decoder input and
the audited frame window.

### Opus and Vorbis: establish the current internal profile

The [isolated codec benchmark](ESP32C3_CODEC_BENCHMARK.md) reports about 42% CPU
for its Opus fixture and 36-37% for Vorbis, without Wi-Fi or WebUI. These old
figures justify investigation, not a claim about current total radio load.
Current registration uses `esp_opus_dec_register` and `esp_vorbis_dec_register`;
changing application `-O3` flags does not rebuild the precompiled vendor DSP.

For Opus, compare the linked implementation with the source behind each proposed
ESP8266 optimization before porting. Reusing a previously computed PVQ lookup is
an example to inspect; its reachability/frequency must be measured on C3 streams.
Do not copy Xtensa register code to RV32 or assume a generic decoder complexity
knob from encoder APIs. Preserve CELT, SILK, hybrid, supported frame durations,
reset and packet-loss behavior.

For Vorbis, start from the [repair plan](ESP32C3_VORBIS_REPAIR_PLAN.md) and
[output retry evidence](ESP32C3_VORBIS_OUTPUT_20261005.md). Codebooks depend on
stream setup; they cannot simply become one fixed flash table. Scratch reuse
requires a complete reader/writer map for floor, residue, MDCT and overlap.
The old output retry bug synthesized a packet twice; the EOF repair recovered
five omitted packets. Preserve those tests while changing any PCM ownership.

For MP3, the retained backend comparison measured Espressif/Helix/minimp3 at
27.9%/30.2%/407.9% decoder CPU on one C3 fixture. These are historical measurements,
not a universal ranking across all configurations. They do not support replacing
the current Espressif backend for speed.

## Common pipeline opportunities

1. **Measure PCM copying, then test a queue-owned output lease.**
   `audio_service.c:send_pcm()` copies the decoder workspace into the PCM ring.
   Current ordinary packets hold at most 3,584 payload bytes in an 8-KiB
   no-split ring. At 48 kHz stereo signed-16, one full PCM copy moves 192,000
   payload bytes/s (reads plus writes cause more memory traffic). This is a
   calculation, not measured CPU cost. A large codec output frame may not fit
   one packet. Try direct decoding into a queue-owned block only for a proven
   capacity/lifetime path; retain a fallback for larger output and retry/EOF.
   Account for blocks reserved by a decoder but not yet published. Do not make
   the decoder hold a live DMA descriptor during an unbounded decode call.
2. **Keep buffering codec-aware and bounded.** The accepted raw-tail coalescing
   already packs short network reads into useful slot capacity. Budget encoded
   bytes and PCM frames separately; a slot count is not a duration guarantee.
   Increasing the shared arena can strand free RAM outside the network allocator,
   as documented in the [arena investigation](ESP32C3_ARENA_FLAC_DMA_20261013.md).
   Preserve TLS/Wi-Fi headroom by ownership, not an arbitrary global heap floor.
3. **Inspect cache and IRAM after profiling.** Move only a measured hot routine
   if its CPU improvement justifies lost data RAM. Review final linked calls,
   constants and cache-disabled safety. A smaller loop can outperform additional
   unrolling. Do not apply the old QEMU correction factor to a different codec,
   library, memory placement or network workload.

## Experiment order and acceptance

All items below are pending; this review does not enable them.

1. Freeze a matched current control: SDK/archive hashes, options, compiler, ELF,
   input hashes, clocks and buffer policy. Record stage CPU, wall waits, memory
   owners and stack margins on the same inputs.
2. Test grouped AAC PC19 metadata operations, with bit-identical current output
   and the combined 3-LSB full-reference gate. Reuse the late-SBR, recording,
   pointer-audit and fault suites in `tools/codec_benchmark/`.
3. Test LPC no-auto-unroll independently. Use `compare_flac_hotloops.py`,
   `run_flac_rice.py`, `run_flac_depths.py` and `run_flac_bounds.py` as appropriate;
   exercise ordinary predictors and non-repeating LPC32, not only the sparse path.
4. Profile Opus/Vorbis internals, then choose one reachable exact optimization
   per codec. Reuse `run_vorbis_output.py` for retry/chunk/EOF regression coverage.
5. Measure PCM copy cost; prototype queue leases only if the benefit is material.
   Reuse `run_output_dma_host.py` for relevant output-equivalence coverage, but
   add ownership tests specific to the new queue contract.
6. Qualify each surviving candidate on physical C3 with alternating control and
   candidate runs, identical fixtures, and up to 10-minute heavy playback cases.
   Verify HTTP/HTTPS, transitions, Stop/Play, EOF, allocation failures, WebUI and
   OTA. Preserve unsuccessful and incomplete trials.

Report cycles/audio second, decoder task CPU, elapsed decode time, input wait,
PCM-space wait, output-submit wait, p95/p99/max call durations and active-playback
DMA deltas separately. Completion-queue drops are not directly audible sample
loss counts and must exclude idle/EOF. Check actual PCM/sample count as well.
Track live allocation peaks, largest block, reserved arena slack and stack usage;
heap savings that merely consume additional stack are not net RAM savings.

A candidate needs unchanged supported functionality and no new playback,
allocation, watchdog or recovery failures. High CPU or a small free block alone
is diagnostic, not an automatic rejection when the required workloads work.
Do not claim a universal precision bound from a finite corpus.

## Primary references checked

- [Espressif C3 speed guide, IDF 6.1](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-guides/performance/speed.html): measure hot functions, distinguish cycle and wall-time measurements, and account for cache/layout effects.
- [FLAC RFC 9639](https://www.rfc-editor.org/rfc/rfc9639.html): prediction, residual coding, and decoding precision requirements, including Appendix A.3.
- [Opus 1.5 decoder CTLs](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoderctls.html): decoder controls; do not infer a supported decoder optimization setting from an encoder API or a different library version.

Project-specific hardware counter details and prior cache evidence are in
[ESP32-C3 optimization reference](ESP32C3_OPTIMIZATION_REFERENCE.md).
