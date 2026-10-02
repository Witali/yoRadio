# AAC array-by-array compact storage experiments

## Result

Eight isolated probes completed **330 paired PCM comparisons** against the
pinned Espressif ESP32-C3 AAC decoder. Five retained radio captures passed the
temporary maximum error of 5 signed-16 PCM LSB in every probe. **IMDCT overlap
compression failed on synthetic HE-AAC signals**, with errors up to 2838 LSB.
It must not be enabled based on the radio captures alone.

Complex high-band QMF history reached at most 2 LSB in this corpus. Checked
int16 storage for smoothing exponents was bit-exact; observed values were
-50 through +16. Neither observation proves a bound for every valid AAC stream.
Other hybrid/PS probes reached 3 LSB and still fail the final 2-LSB requirement.

These are **numerical storage roundtrips**, with unchanged native allocations
and DSP. Actual heap saved is **0 bytes**. Production defaults and firmware are
unchanged. Smaller owners and complete reader/writer adaptations are still needed.

## Representation and comparison

The decoder stores fixed-point integers, not IEEE floating-point complex values.
Complex arrays pair their native int32 real and imaginary components. Other
probes pair **adjacent real scalars**; coefficients and energies are not complex
samples. Unpacking restores the native scale. Smoothing exponents use exact
int16 storage instead of quantization.

The [18+18 format](ESP32C3_AAC_STORAGE18_20261002.md) stores the low 16-bit halves
in one aligned word and four metadata bytes in another word. Each metadata byte
contains two high bits per component and a shared four-bit shift. Shifts 0..14
are valid; code 15 is reserved. Rounding is nearest, ties away from zero.
All eight probes reported **zero quantizer saturation**.

Sizes include row padding to whole metadata words. Stereo means two native
channels; PS-only arrays describe one PS instance. These are candidate payloads,
excluding pointers, owner alignment, caches and workspace. PS overlays the right
SBR channel: savings must not be summed blindly.

| Isolated area | Native → compact bytes | Payload saved | Maximum PCM error, all inputs | RMS, real captures only | QEMU instruction overhead range |
| --- | ---: | ---: | ---: | ---: | ---: |
| Complex high-QMF history, stereo | 4608 → 2880 | 1728 / 37.5% | 2 LSB | 0.017990 LSB | +0.151..3.733% |
| Hybrid retained history, 3 × 12 complex pairs | 288 → 180 | 108 / 37.5% | 3 LSB | 0.123533 LSB | +0.270..0.318% |
| IMDCT overlap, stereo, adjacent real values | 8192 → 5120 | 3072 / 37.5% | **2838 LSB — reject** | 0.267491 LSB | +4.021..56.696% |
| Gain/noise smoothing mantissas, stereo | 5120 → 3200 | 1920 / 37.5% | 0 LSB¹ | 0 | +2.308..6.337% |
| Gain/noise smoothing exponents, stereo, int16 | 5120 → 2560 | 2560 / 50% | 0 LSB¹ | 0 | +0.367..1.038% |
| Previous PS mixing coefficients, 4 × 22 real values | 352 → 224 | 128 / 36.4% | 3 LSB | 0.178183 LSB | +0.380..0.405% |
| Left hybrid analysis output, 10 complex pairs | 80 → 52 | 28 / 35% | 3 LSB | 0.166505 LSB | +2.342..2.853% |
| PS peak/energy/difference histories, 3 × 20 real values | 240 → 156 | 84 / 35% | 3 LSB | 0.090302 LSB | +7.138..7.549% |

¹ Smoothing rows were restored immediately after a frame-boundary roundtrip.
Mantissas really changed, but PCM did not. This **does not qualify within-frame
writes or the enabled five-tap FIR**: rows may be overwritten or not consumed by
the next envelope. A compact accessor implementation must separately exercise
smoothing on/off, all five taps, row rotation, resets and coupling. The int16
test checked every visited exponent before narrowing; out-of-range values would
be counted and retained unchanged. There were no exceptions. A format-wide
exponent bound remains necessary before allocating int16 arrays.

Timing is the median of QEMU guest-instruction ratios for runs 2 and 3, then the
range across exercised inputs. It includes packing, immediate unpacking, guards,
counters and wrapper overhead. It is **not physical CPU utilization or the speed
of an optimized compact decoder**; no board calibration factor is applied.

RMS pools run-1 scalar PCM samples only from real inputs where the area was
visited. Synthetic failures and inactive-codec controls are excluded from RMS:

- Complex high history: ABBA64 and Groove Salad 16, 4,567,040 samples.
- Hybrid and PS areas: ABBA64, 2,646,016 samples each.
- Smoothing: ABBA64 and Groove Salad 16/32/64, 9,859,072 samples.
- IMDCT: all five captures, 12,505,088 samples.

The high-history probe skips real-only low-complexity SBR. An inactive path does
not demonstrate exact compression of its storage.

## Consumer, lifetime and alias audit

The runner checks archive SHA-256
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909` before execution.
Live probes use named fields in
[`aac_sbr_abi.h`](../idf/esp32c3-oled-native/main/aac_sbr_abi.h), compile-time ABI
offset/size assertions, bounded PS pointers and guarded packed words.

| Area | Initializers and native consumers checked | Boundary and limits |
| --- | --- | --- |
| High QMF history | `sbr_open`, `init_sbr_dec`, `sbr_reset_dec`, `sbr_dec`; working high bands also pass through `sbr_generate_high_freq`, `calc_sbr_envelope` and synthesis | After `sbr_dec` saves six 48-pair rows; the next frame reloads them. Working high-band writes are excluded. |
| Hybrid history | `ps_allocate_decoder`, `ps_hybrid_filter_bank_allocation`, `sbr_dec`, `ps_hybrid_analysis`, `two_ch_filtering`, `eight_ch_filtering` | Three 12-pair rows after `sbr_dec` copies scratch back. Within-frame scratch is excluded. |
| IMDCT overlap | `PVMP4AudioDecodeFrame`, both `trans4m_freq_2_time_fxp_1/2`, `long_term_prediction`, decoder init/reset | After each transform producer, 1024 real values. Both entry points and all four window sequences exercised. The inactive right channel is **not swept**: PS reuses it as QMF workspace. LTP-specific corpus coverage is not claimed. |
| Smoothing rows | `init_sbr_dec` constructs five row pointers; `calc_sbr_envelope`, `envelope_application`, `envelope_application_LC` populate/read them; `sbr_reset_dec` and startup rebuild state | All five physical rows at frame end; gain/noise mantissas and exponents separately. No tap, pointer or row is removed. |
| Previous mixing coefficients | `ps_allocate_decoder`, `ps_init_stereo_mixing`; interpolation reaches `ps_stereo_processing` via `mix` and `delta_mix` | Four 22-scalar `previous_mix` rows at frame end. Current `mix` and `delta_mix` excluded. |
| Hybrid analysis output | Hybrid allocator, `ps_hybrid_analysis`, `two_ch_filtering`, `eight_ch_filtering`; power detection, decorrelation, stereo processing and hybrid synthesis | Ten left Re/Im outputs after each analysis call, before power/decorrelation/mixing. Right outputs and later in-place writes excluded. |
| PS energy states | `ps_allocate_decoder`, `ps_pwr_transient_detection`, called before decorrelation | Three 20-scalar arrays after every transient detector call, feeding its next invocation. Current-call attenuation has already been calculated. |

Initialization, reset and free remain native; no pointer is redirected and no
allocation is resized. PS probes validate the embedded object and its pointers
into the right-channel overlay. Observed zero values never authorize removing
storage. Function analyses are retained under
[`docs/audits/esp32c3-aac-core-symbolic-20261001/pseudocode/`](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/).
Ghidra pseudocode is analysis evidence, not original source.

### Other arrays and exclusions

- **Synthesis and LTP histories are already int16.** This format needs about
  20 bits per real value and would grow their payload. Use a separately qualified
  format or lifetime/ring redesign.
- **Current PS mixing/delta matrices** need separate envelope/slot-update probes.
  Their error cannot be inferred from previous mixing coefficients.
- **Working QMF, spectral/transform and envelope scratch** share storage with
  other phases and PS. The 12,288-byte shared scratch is used to its end.
  Compact retained arrays do not authorize shrinking scratch. Real spectral
  values and exponent/control overlays cannot be traversed as complex samples.
- **IID/ICC indices, harmonics and flags** are control data. Narrowing must be
  exact and preserve every reader's signedness and sentinels; lossy block-floating
  storage is inappropriate.
- **Pointers and smoothing pointer tables** must remain pointers. The prior
  lossless five-entry table compaction is a separate layout change.

## Corpus, controls and rejected result

Six synthetic fixtures cover AAC-LC 22.05 kHz mono and 44.1/48 kHz stereo,
HE-AAC 44.1/48 kHz stereo and HE-AAC v2 44.1 kHz stereo. Five original ADTS
captures are the same bytes as earlier QMF/PS experiments: ABBA64 and Groove
Salad 16/32/64/128. Input hashes, FFprobe profiles, lengths and decoder/config/ELF
hashes are retained. No retranscoding or new downloads were used; raw radio audio
is not committed.

Every input runs eight isolated probes, exact traversal (9), binary bypass (0)
and three repeats. Synthetic files decode twice per repeat. LC runs the whole
matrix, so its overlap coverage cannot disappear behind an SBR-only check.
Independent reference/candidate decoders receive identical chunks and compare
final PCM layout, frame/sample counts and errors. Real recordings retain
per-channel histograms and 64-bit error moments.

| Rejected IMDCT case | Maximum PCM error |
| --- | ---: |
| Synthetic HE-AAC 44.1 kHz | 2838 LSB |
| Synthetic HE-AAC 48 kHz | 2364 LSB |
| Synthetic HE-AAC v2 44.1 kHz | 1350 LSB |

Real IMDCT tests reached at most 5 LSB; synthetic LC reached 1 LSB. All four
window sequences ran in every synthetic fixture. Exact traversal stayed
bit-exact. The large downstream HE error is measured; its internal amplification
mechanism has not been isolated. Smaller real-recording RMS does not qualify it.

## Reproduction and evidence

Build with `idf/esp32c3-oled-native/build.ps1`, dependency root
`C:/Work/yoRadio/.idf`, build/config directory `build-qemu-aac-area-storage`, and
defaults in order: `sdkconfig.defaults`, `sdkconfig.qemu.defaults`,
`sdkconfig.qemu-aac-packed-history.defaults`, `sdkconfig.qemu-aac-area-storage.defaults`.
Use the IDF Python environment and the project's patched icount QEMU:

```powershell
python tools/codec_benchmark/run_aac_area_storage.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu /mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl --timeout 1200 `
  --output .build/aac-area-storage/synthetic

# Add --input path/to/original.aac and a separate --output for each recording.
python tests/test-aac-area-storage.py
```

Exit 2 means measured PCM precision failure, not a crashed experiment. The
synthetic run is expected to return 2; do not discard that result.

[`tests/results/esp32c3-aac-area-storage-20261002/`](../tests/results/esp32c3-aac-area-storage-20261002/)
contains all logs/results, build log/config, source snapshots with hashes and
`summary.json`. Tests reparse the matrix, verify provenance, preserve the negative
IMDCT result and reject missing/duplicate rows, wrong verdicts, cross-area writes
and contradictory histograms.

Priorities: prove the exponent range and adapt every accessor for exact int16
storage, then integrate compact high-QMF history. Hybrid/PS still need the final
precision limit and speed qualification. IMDCT's theoretical 3072-byte saving is
rejected and cannot be counted as available RAM.
