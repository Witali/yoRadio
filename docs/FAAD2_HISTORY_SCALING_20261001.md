# FAAD2 versus the C3 AAC backend: history scaling

## Result

Downloaded and built pinned FAAD2 in **fixed-point, full complex SBR/PS, `-O2`**
mode, matching the supplied configuration recommendation. A separate floating
build is used only as a scaling reference. Ran **60 paired host comparisons** on
the same synthetic and real AAC bytes used by the C3 experiments.

With nearest 14+14+4 packing, the tested FAAD2 fixed history scope reaches
**2 LSB on the real recordings and 3 LSB on synthetic HE-AAC v2**. This passes
the user's temporary **±5 LSB development** criterion on this corpus; the
synthetic case still exceeds the final **±2 LSB** requirement. This is a promising
source-backend candidate, not a qualified firmware replacement or an actual RAM
saving. Its exact history scope differs from the Espressif experiment.

**There is no demonstrated single scaling constant to transplant into the
Espressif binary.** A power-of-two rescale changes the shared exponent along
with the data; away from the exponent floor/saturation it does not improve the
14-bit mantissa's effective precision. Changing scaling *inside* the DSP requires
matching coefficients, shifts, energy estimates and output normalization.

## Source and configuration provenance

- [FAAD2 upstream](https://github.com/knik0/faad2/tree/e8e76f0a44db45aed773a3f62fe35a63c867a738),
  commit `e8e76f0a44db45aed773a3f62fe35a63c867a738`.
- Downloaded archive SHA-256:
  `36f5aa8cbfcc442cdaced7f29dbe66276c62a1432d3c639405c07bcdf47614ab`.
- Local source:
  `.build/faad2-comparison/faad2-e8e76f0a44db45aed773a3f62fe35a63c867a738/`.
  The source archive and build products are ignored; a pinned download/build
  runner, source hashes, exact commands, raw results and tests are tracked.
- Supplied `faad2_esp32c3_build_configuration.md` SHA-256:
  `f3e066807390931ec14c80119c9937e4cc57d8e467e91306ae1c271c7f82ec92`.
  This describes a recommended build. It does not establish the exact binary,
  quantizer integration or input used for the earlier 100.626 dB study.

Fixed build defines `FIXED_POINT`, `APPLY_DRC` and the upstream platform feature
macros. `SBR_DEC`/`PS_DEC` are enabled by upstream `common.h` and checked at compile
time. `SBR_LOW_POWER`, `DISABLE_SBR`, `LC_ONLY_DECODER`, `DRM_SUPPORT` and
`BIG_IQ_TABLE` are not defined. No LTP/LD feature was removed. The float control
omits only `FIXED_POINT`. Both use GCC `-O2 -ffloat-store -fno-strict-aliasing`.

FAAD2's default configuration object selects MAIN even when fixed-point support
disables that profile. The probe explicitly sets the **fallback** object type to
LC before `NeAACDecSetConfiguration`; each ADTS header supplies the actual stream
configuration. This avoids an initialization failure without forcing a core-only
decode. PS activity, channel/rate metadata and output shape are checked at runtime.

No upstream implementation is incorporated into the shipped firmware. The host
probe includes downloaded FAAD2 headers and links downloaded FAAD2 sources.
Any future backend replacement must retain licensing and verify the existing
format contract; FAAD2 fixed mode itself disables MAIN and SSR.

## What the scales actually mean

| Location | FAAD2 implementation | Consequence |
| --- | --- | --- |
| [`fixed.h`](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/fixed.h) | `REAL_BITS=14`, `COEF_BITS=28`, `FRAC_BITS=31` | Signal samples, some coefficients and fractional coefficients use different binary points. “14” is a fractional-bit count, **not** a 14-bit storage mantissa. |
| [`sbr_qmf.c`](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/sbr_qmf.c) | Fixed analysis input shifts right by 4; floating output applies ×2 that fixed output omits | Fixed QMF represents the floating QMF signal with an additional factor of 1/32 relative to Q14. |
| [`ps_dec.c`](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/ps_dec.c) | Fixed PS energy code explicitly accounts for a signal scale of 2^-5 and energy scale of 2^-10 | Changing QMF normalization also changes downstream energy calculations. |
| [`output.c`](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/output.c) | Fixed output rounds/clips and shifts by `REAL_BITS`; float output uses PCM-like units, or divides by 32768 for float PCM | Internal QMF numbers and final full-scale PCM numbers cannot be compared without normalization. |

For signal QMF/history, the expected numeric ratio is therefore
`fixed_integer / float_native ≈ 2^14 / 32 = 512`. Measurements on ABBA give
**512.0011 for SBR and 512.0014 for PS-delay RMS**, consistent with the source.
This is an aggregate cross-decoder check, not samplewise identity: fixed and
float arithmetic have different rounding, and synthetic transients differ more.

The Espressif binary uses a different pipeline. Its retained
[`calc_sbr_anafilterbank` pseudocode](audits/esp32c3-aac-decompile-20260930/pseudocode/calc_sbr_anafilterbank.c)
reads **int16 core PCM**, shifts it by 16 before high-word multiplies, then calls
`analysis_sub_band`. FAAD2 feeds its internal `real_t` core output into QMF.
SBR/PS layouts and synthesis are also different. This evidence establishes
different conventions, but does **not** establish a universal Q-format for every
Espressif history field or justify replacing one constant with `REAL_BITS=14`.

## Paired measurements

Each candidate is compared to an unmodified decoder of the **same backend and
arithmetic mode**. No amplitude matching, resampling or output rescaling is
applied to the compared int16 PCM. Synthetic input is repeated twice without
reset, matching the C3 experiment; recordings run once. FAAD2 startup/output
latency differs from Espressif, so their scalar PCM counts are not identical.

The FAAD history scope here is:

- Retained `Xsbr` rows `0 .. tHFGen-1`, after `sbr_save_matrix` has moved the
  history and cleared working rows. Both allocated channel arrays are inspected.
- Four PS signal-delay arrays: `delay_Qmf`, `delay_SubQmf`, `delay_Qmf_ser` and
  `delay_SubQmf_ser`, only when PS is active. Generic unused entries include zeros.
- **Excluded:** complex mixing/phase coefficients, energy/control fields and
  the hybrid history behind the private opaque pointer. The C3 probe includes
  hybrid history and has a different low/high QMF layout. The original supplied
  study's exact modified buffers/code are unavailable.

The following are maximum absolute int16 differences for **SBR plus PS delays**:

| Input | FAAD fixed | FAAD float, conversion scale 512 | C3 Espressif nearest, SBR plus all tested PS history |
| --- | ---: | ---: | ---: |
| Synthetic HE-AAC v2, two passes | 3 LSB | 4 LSB | 7 LSB |
| ABBA 64 kbps, PS active | 2 LSB | 2 LSB | 3 LSB |
| Groove Salad 16 kbps | 2 LSB | 2 LSB | 3 LSB |
| Groove Salad 64 kbps HE-AAC | 2 LSB | 2 LSB | 0 LSB, complex packing inactive in this real-only path |
| Groove Salad 128 kbps AAC-LC | 0 | 0 | 0, no SBR |

For ABBA, fixed FAAD SBR-only reaches 2 LSB, PS-delay-only 1 LSB, combined 2 LSB
with **0.2597 LSB RMS**. No int32 conversion overflow or packing saturation occurs
in the fixed or scale-512 floating trials. These narrower/different scopes and
different baselines prevent attributing the improvement solely to scale.

FAAD decodes Groove Salad 16 kbps as **32 kHz mono with no active PS**. The
Espressif result duplicates mono into two output channels, also without entering
its PS path. FFprobe's HE-AAC v2/stereo label alone was therefore insufficient to
establish PS coverage for that capture. ABBA and the synthetic fixture exercise
PS in both experiments. This is saved as a metadata-test follow-up.

### Why simply enlarging the scale is not a solution

The float reference is converted to int32 at scale 512 before applying the same
portable packed quantizer, then converted back. A second diagnostic trial uses
scale 16384 (32 times larger). It can preserve smaller coefficients near the
minimum `shift=3`, but larger values no longer fit int32.

On ABBA combined history the larger scale produced **17,439 out-of-range pairs**
and one pack saturation. On the two-pass synthetic fixture it produced **622
out-of-range pairs**. The probe explicitly leaves unrepresentable pairs unchanged
and marks these runs `representable=false`; their apparently better one-LSB
maxima are **invalid as a complete compact-storage result**. They are retained to
prevent promoting a partial/overflow-bypassed comparison into a quality claim.

An independent test executes the actual quantizer on **98,304 interior
power-of-two rescaling cases**. Mantissas and restored values are identical after
undoing the scale when the minimum exponent and saturation do not intervene.
It also verifies the minimum-step exception: at the native scale `(1,-1)` rounds
to `(0,0)`; multiplying by eight before packing preserves that pair, at the cost
of less remaining upper range. There is no free improvement across the complete
int32 domain from a global scale change.

## Reproduce and retained evidence

With Windows ESP-IDF Python and WSL GCC already installed:

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& $python tools/codec_benchmark/run_faad_history_comparison.py
& $python tests/test-faad-history-comparison.py
```

The runner also works with native GCC on Linux. `--output` selects the source,
build and result directory; `--recordings` selects the directory containing the
saved ADTS files. It downloads only the pinned source archive, checks its hash
and verifies an existing extraction against it. It does not download recordings
or touch a board. Input hashes, compiler/commands, source hashes, counters and raw
JSON output are retained in
[`tests/results/faad2-history-comparison-20261001`](../tests/results/faad2-history-comparison-20261001/).

## Next implementation gates

1. Isolate C3 low-QMF, high-QMF and individual PS-history contributions before
   changing its arithmetic; preserve the complete format contract.
2. Consider a source-based FAAD2 adapter as a separate backend experiment. Measure
   real RV32 peak heap, stacks, code size and decode speed; host results do not
   establish that a generic FAAD2 allocation fits the radio.
3. Implement actual packed history ownership and bounded native scratch only
   after choosing the backend/layout. Current roundtrip probes release no RAM.
4. Add the requested default-on development storage option only with a working
   implementation satisfying the temporary ±5 LSB gate. Keep the final ±2 LSB
   and decode-speed requirements visible; no release or default production
   backend change is qualified by this comparison.
