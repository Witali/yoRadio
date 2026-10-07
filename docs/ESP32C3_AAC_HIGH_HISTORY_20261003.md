# Persistent high-QMF history: smaller allocation

This experiment integrates packed high-band QMF history with the existing
five-entry smoothing pointer tables and relocated PS control. The native
decoder allocates a **smaller SBR owner**. Unlike the earlier roundtrip probe,
the original retained int32 history arrays no longer exist in the candidate.

## Memory

| Decoder layout | Requested owner | Measured allocator block | Block saving vs original |
| --- | ---: | ---: | ---: |
| Original | 55,128 B | 55,296 B | 0 |
| Lossless compact tables + relocated PS | 49,708 B | 51,200 B | 4,096 B |
| Above + high history, shared 18-bit mantissas | 47,980 B | 49,152 B | **6,144 B** |
| Above + high history, shared 16-bit mantissas | 47,692 B | 49,152 B | **6,144 B** |

High history holds six rows of 48 complex pairs per channel. Its stereo payload
falls from 4,608 B to 2,880 B (18-bit) or 2,592 B (16-bit): savings of 1,728 B
(37.5%) or 2,016 B (43.75%). Both requests land in the same allocator bin here.
The additional **measured block saving is 2,048 B** over the lossless owner.
The unguarded allocation probe and guarded live decoder allocations agree.

These numbers describe the SBR owner allocation, not net whole-radio RAM.
The QEMU adapter has 144 B of shared test state; the new copy/quantization
instrumentation adds 44 B. Native working arrays provide the unpacked rows;
there is no extra unpack allocation or full-size history shadow. Production
integration is now available in the [production adapter experiment](ESP32C3_AAC_HIGH_ADAPTER_20261003.md),
with per-decoder ownership and passing QEMU isolation/reset/failure tests.
Physical heap/CPU qualification is tracked separately there.

## Representation and access audit

- Each complex pair has a 32-bit word holding the low 16 bits of Re and Im.
  PC18 adds one metadata byte (two high bits per component plus a shared shift),
  four pairs per metadata word. PC16 uses one exponent nibble, eight pairs per
  metadata word. Arithmetic scales and QMF working rows stay unchanged.
- `sbr_dec` has **six** retained-history transfers: entry Re/Im loads and Re/Im
  stores on the PS and non-PS paths. Loading Re reconstructs the pair of rows;
  storing Re packs both working components. The paired Im transfer validates
  its arguments and order. Other memmoves retain their original behavior.
- The real-only SBR path is also exercised. It stores the new real component
  with the previously represented imaginary component; it never reads unused
  imaginary scratch. Both representations can introduce quantization into the
  real-only path, so it is included in the PCM gate rather than assumed exact.
- `init_sbr_dec` builds all five smoothing pointers at their new locations.
  `sbr_open` zeroes the smaller channels. `sbr_read_data` and `sbr_applied`
  use the new channel stride and high/synthesis pointers. `ps_allocate_decoder`
  uses the shifted right-channel workspace. The frame prefix used by envelope,
  noise and bitstream readers is unchanged; their working-array arguments are
  still native int32 pointers.
- `calc_sbr_envelope` and high-frequency/synthesis functions consume pointers
  supplied by those callers; their arithmetic is unchanged. The repaired
  `PVMP4AudioDecoderResetBuffer` clears the packed histories through typed
  helpers and preserves the right imaginary component in real-only reset.
  Close/free still owns one allocation, with no auxiliary history to leak.
- The PS overlay retains its channel-relative layout. Compile-time assertions
  ensure relocated PS ends before synthesis in both smaller layouts. PS/SBR
  are overlapping right-channel uses, never additive memory savings.

The archive is SHA-256 pinned. All **87 address/stride instruction patches**
derive their values from RV32 compiler `offsetof`/`sizeof` descriptors. Applying
the original descriptors reconstructs every original instruction exactly.
The six history call sites and all 21 forwarded memmove call sites are checked
against ELF relocations before redirecting the copied `sbr_dec` object. The
SDK archive is unchanged. Machine instruction locations belong only to this
audited binary boundary; runtime code uses named fields.

## Qualification

Each representation runs 81 paired comparisons: six synthetic AAC-LC/HE-AAC/
HE-AACv2 formats and five saved radio captures, with three repetitions and
unchanged native decoder controls. External captures also retain per-channel
histograms, RMS error and input hashes. Format rates/channels, consumed bytes,
frame sizes, guards and saturation counts are checked.

Each run additionally checks a 21-segment format-change lifecycle, both SBR
allocation-failure paths, 24 smoothing FIR cases, and repaired reset for all
six synthetic formats (three decoding cycles with two resets). Reset and
lifecycle PCM maxima participate in the same **3 signed-16 PCM-unit** gate.
The contained original reset-overrun reproduction is retained separately.

The injected-allocation A/B checks retain the vendor's fallback behavior to
compare cleanup against the reference. They do not qualify production failure
handling: the production adapter must still return a memory error and no
core-only PCM when SBR allocation fails. Its existing fail-closed checks must
be rerun when this candidate is integrated.

The 18-bit format reaches at most **2 LSB** across the retained corpus and
these lifecycle/reset checks. Its active HE-AAC guest-instruction overhead is
approximately **2.6–5.6%**, including guards, statistics, verification unpacking
and scoped copy dispatch. This is not a real-board CPU percentage.

PC16 also passes, at **3 LSB** maximum with approximately **2.5–5.0%** active
HE-AAC instruction overhead. Since both formats occupy the same allocator bin,
PC18 is selected for the next production-adapter experiment for its extra
precision margin. The [comparison table](../tests/results/esp32c3-aac-high-history-20261003/TABLES.md)
includes per-recording peak/RMS errors, reset/lifecycle peaks and instruction costs.

A fresh regression build with high-history compression disabled passes all 36
original lossless synthetic comparisons, lifecycle and reset checks at **0 PCM
error**. The shared test changes therefore preserve that existing profile.

See the [saved results](../tests/results/esp32c3-aac-high-history-20261003/)
for both formats, including individual error distributions and allocator
measurements. Neither candidate is promoted to a production default. Remaining
gates include malformed/truncated input,
long-running radio networking, physical CPU/cache behavior and OTA. This change
does not claim to resolve the previously recorded HE-AAC network allocations.
The implicit SBR change with an unchanged ADTS header remains a separate issue.

## Reproduction

Use the project's existing ESP-IDF/QEMU setup. Create a separate build directory
and sdkconfig for each representation to avoid retaining the other format's
Kconfig selection:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-high-history18 `
  -Sdkconfig build-qemu-aac-high-history18/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.qemu.defaults',`
    'sdkconfig.qemu-aac-packed-history.defaults','sdkconfig.qemu-aac-smoothing.defaults',`
    'sdkconfig.qemu-aac-compact-owner.defaults','sdkconfig.qemu-aac-high-history.defaults')
python tools/codec_benchmark/run_aac_high_history.py --help
python tests/test-aac-high-history.py
```

For PC16 use a fresh `build-qemu-aac-high-history16` directory and replace the
last defaults file with `sdkconfig.qemu-aac-high-history-pc16.defaults`.
The runner accepts `--build`, `--qemu`, `--bios`, `--wsl`, `--output` and optional
`--input`/`--source-url`; saved provenance records the actual commands and
firmware/configuration hashes. Real recordings remain local.
