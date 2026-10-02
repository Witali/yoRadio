# QMF storage with independent real/imaginary exponents

**Current policy (2026-10-02): production permits +/-3 PCM LSB; development permits +/-5.**
The older acceptance statements below describe the limits at measurement time.
Measured errors and archived evidence are unchanged. See [current precision policy](ESP32C3_AAC_PRECISION_POLICY.md).

## Result and scope

The [18+18 follow-up](ESP32C3_AAC_STORAGE18_20261002.md) adds a fifth variant
with a shared four-bit exponent and four metadata bytes per word. It fits the
same payload as independent 16-bit component exponents and gives lower RMS
error on the retained recordings. The consolidated table below includes it.

The requested representation is implemented as a **QEMU experiment**, behind
`CONFIG_YORADIO_QEMU_AAC_QMF_STORAGE_TEST`. Each complex pair has a 32-bit word
containing signed 16-bit real and imaginary mantissas. A separate 32-bit word
contains eight four-bit exponents for four pairs:

```text
mantissa word i: [ Im low 16 bits | Re low 16 bits ]
metadata word:  [ Im3 Re3 | Im2 Re2 | Im1 Re1 | Im0 Re0 ]
                  each component occupies one four-bit nibble
reconstructed component = signed_mantissa * 2^(stored_exponent + 1)
```

The shift range is 1..16, preserving the full signed-32 input range. Quantization
uses nearest rounding, ties away from zero, with saturation for a positive carry
at the largest shift. Zero stays zero. DSP arithmetic and its native scaling
remain unchanged. Each component chooses its own smallest fitting shift.

The full decoder produced a maximum difference of **3 signed-16 PCM LSB** on
the exercised synthetic and recorded QMF cases. All tested variants passed the
temporary 5-LSB criterion; none passed the final 2-LSB criterion on all active
QMF inputs. This is corpus evidence, not an error bound for every AAC stream.
No sample-rate or channel restrictions were added.

The experiment packs each newly written analysis row into real mantissa and
metadata arrays, unpacks it for the original downstream decoder, and compares
its final PCM against a separate original decoder. Quantized rows propagate
through the retained low-band history, high-frequency generation, PS and
synthesis as applicable. It does **not** replace the allocation or the native
array readers. Actual heap saving in this experiment is **0 bytes**. High-band
history, hybrid history and PS delay quantization are not combined into this
QMF trial.

## Storage accounting

Low-band storage has 40 rows of 32 complex values per channel. This table uses
independently word-aligned rows, including metadata padding. It excludes working
buffers, guards and other SBR/PS state.

| Representation | Bytes per row | Two-channel payload | Payload reduction |
| --- | ---: | ---: | ---: |
| Native int32 Re + int32 Im | 256 | 20,480 | 0 |
| 16+16, shared four-bit exponent | 144 | 11,520 | 8,960 (43.75%) |
| **16+16, independent four-bit exponents** | **160** | **12,800** | **7,680 (37.5%)** |
| 17+17, shared exponent, five six-bit metadata entries/word | 156 | 12,480 | 8,000 (39.06%) |
| 17+17, shared exponent, four byte metadata entries/word | 160 | 12,800 | 7,680 (37.5%) |
| 18+18, shared exponent, four byte metadata entries/word | 160 | 12,800 | 7,680 (37.5%) |

The 17-bit alternatives keep the low 16 bits in the mantissa word and place each
component's extra high/sign bit with the four-bit shift. No mantissa crosses a
word boundary. Their shift range is 0..15. The five-entry layout could use 12,288
bytes if metadata spans row boundaries; that is a different indexing choice.

In HE-AAC v2, the right channel's apparent low-QMF area also holds PS state and
delay buffers. A single active low-QMF matrix would save **3,840 payload bytes**
with independent exponents. The stereo 7,680-byte estimate cannot be claimed as
additional PS-mode heap saving or added to PS overlay savings.

## Consolidated signal and storage comparison

The reference representation is signed **32-bit Re + 32-bit Im**. Compression
factor means original payload divided by packed payload; reduction means the
percentage of original bytes removed. Metadata and its word padding are included.
QMF sizes describe two independently row-aligned low-band matrices; PS sizes
describe the 617 complex delay pairs. The native baselines are 20,480 and 4,936
bytes respectively, with zero PCM difference from themselves.

Signal errors are measured **after complete decoding**, against the original
decoder's signed-16 PCM. One LSB is one integer unit in that output. RMS is
`sqrt(sum(square_error) / sum(sample_count))`, pooled across channels and active
recordings, using run 1 only. The three repeats have matching error counts.
QMF covers ABBA64 and Groove Salad 16/32/64 (9,859,072 scalar samples); PS covers
ABBA64 (2,646,016 scalar samples). Synthetic fixtures and inactive paths are
excluded from this RMS aggregation. Compare variants within each area: QMF and
PS use different active corpora and were tested separately.
The 18-bit follow-up reran all earlier variants and verified their PCM error
statistics and input hashes against the first batch before extending this table.

| Area | Storage change | Bytes before -> after | Compression / reduction | Max error, LSB | RMS error, LSB | Samples above 2 LSB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| QMF | 16+16, shared exponent | 20,480 -> 11,520 | 1.78x / 43.75% | 3 | 0.343647 | 1,424 (0.014444%) |
| QMF | 16+16, independent Re/Im exponents | 20,480 -> 12,800 | 1.60x / 37.50% | 3 | 0.327956 | 1,156 (0.011725%) |
| QMF | 17+17, five metadata entries/word | 20,480 -> 12,480 | 1.64x / 39.06% | 3 | 0.266385 | 496 (0.005031%) |
| QMF | 17+17, four metadata entries/word | 20,480 -> 12,800 | 1.60x / 37.50% | 3 | 0.266385 | 496 (0.005031%) |
| QMF | 18+18, four metadata entries/word | 20,480 -> 12,800 | 1.60x / 37.50% | 3 | 0.209491 | 176 (0.001785%) |
| PS delays | 16+16, shared exponent | 4,936 -> 2,780 | 1.78x / 43.68% | 3 | 0.275221 | 178 (0.006727%) |
| PS delays | 16+16, independent Re/Im exponents | 4,936 -> 3,088 | 1.60x / 37.44% | 3 | 0.246376 | 103 (0.003893%) |
| PS delays | 17+17, five metadata entries/word | 4,936 -> 2,964 | 1.67x / 39.95% | 3 | 0.205390 | 54 (0.002041%) |
| PS delays | 17+17, four metadata entries/word | 4,936 -> 3,088 | 1.60x / 37.44% | 3 | 0.205390 | 54 (0.002041%) |
| PS delays | 18+18, four metadata entries/word | 4,936 -> 3,088 | 1.60x / 37.44% | 3 | 0.164850 | 24 (0.000907%) |

Independent component exponents reduce aggregate RMS error relative to shared
16-bit exponents while using more metadata. The 18+18 variant gives the lowest
RMS error in this comparison. For 17+17, changing from five to four metadata entries per
word changes storage/indexing, with identical measured PCM statistics. All
variants stay within the temporary 5-LSB limit on this corpus, but still exceed
the final 2-LSB limit on some samples. These measurements do not establish a
perceptual audibility threshold or a worst-case bound for untested recordings.

**Actual heap reduction remains zero in these experiments.** The table compares
array payload representations. The QMF probe restores native rows for existing
readers, and PS retains the original owner allocation. Low-QMF/PS overlay savings
must not be added together. See the lifetime audit below before changing the
allocation.

## Readers and lifetime audit before resizing

The pinned archive and the checked RV32 structures are recorded in
[the symbolic audit](audits/esp32c3-aac-core-symbolic-20261001/README.md).
The following accesses prevent changing an array size without changing its
consumers:

| Function/path | Use of low-band QMF storage | Required migration |
| --- | --- | --- |
| `sbr_dec` -> `calc_sbr_anafilterbank`, `_LC` | Writes 32 new rows after the retained prefix | Pack each new row; preserve real-only processing |
| `sbr_dec` -> `sbr_generate_high_freq` -> coefficient/correlation helpers | Reads multiple time rows through native real/imaginary pointers | Supply decoded bands or change all consumers; a single row buffer is insufficient |
| `sbr_dec`, normal synthesis | Reads low bands and combines them with generated high bands | Unpack rows without changing fixed-point shifts |
| `sbr_dec`, PS preparation | Reads low bands into a separate PS QMF workspace, including lookahead | Preserve lookahead and native saturation/scaling |
| `sbr_dec`, frame tail | Moves retained rows from the end back to the prefix | Move both mantissas and metadata with correct overlap semantics |
| `PVMP4AudioDecoderResetBuffer` | Clears retained regions through native field addresses | Clear matching compact history on every applicable reset path |
| `ps_allocate_decoder` and PS consumers | Alias the right-channel QMF region for energy arrays, delay data and pointer tables | Keep PS overlay independent of the low-QMF layout; verify switches |
| SBR owner allocation and decoder close | Own the enclosing channel objects; QMF has no separate native allocation | Change owner size, alignment and cleanup together; do not free a QMF field separately |

Relevant readable functions: [sbr_dec](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/sbr_dec.c),
[reset](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/PVMP4AudioDecoderResetBuffer.c),
[PS allocator](audits/esp32c3-aac-core-symbolic-20261001/pseudocode/ps_allocate_decoder.c).
These are typed decompilations, not original source. The audit identifies migration
sites; it does not certify a smaller owner allocation.

## Verification and interpretation

This section records the initial four-format batch. The separate
[18-bit report](ESP32C3_AAC_STORAGE18_20261002.md) records the later five-format
matrix and current instruction comparisons; instruction counts from different
builds must not be compared as if only the selected format had changed.

- Independent 64-bit arithmetic oracle: 1,000,000 random pairs, 74,398 additional
  boundary pairs and a Cartesian set of signed-range edge values, all four
  formats. GCC undefined-behavior sanitizer enabled.
- Metadata neighbour, incomplete final word and guard tests; RV32 repeats the
  oracle on 10,000 random pairs before audio decoding.
- QMF: 129 paired comparisons, including three repeats for each tested variant.
  Six synthetic AAC-LC/HE-AAC/HE-AAC v2 files and five retained ADTS recordings.
- PS: 153 paired comparisons using the same storage formats on **actual feedback
  writes**. This is a separate experiment, not simultaneous QMF+PS compression.
- Format/output-shape assertions, original binary bypass, PS native-source
  control, error counts and per-channel histograms/moments for recordings.
- All observed quantizer saturation counts are zero. Histograms and source/config
  hashes are retained with the [raw results](../tests/results/esp32c3-aac-storage-20261002/).

Timing means **QEMU guest instructions**, including experimental wrappers,
packing/unpacking and counters. Medians use runs 2/3; PCM checks include all
runs. It is not physical CPU load, cache latency or a calibrated percentage of
available ESP32-C3 CPU time. Runtime format selection adds overhead compared
with a specialized production implementation.

On the ABBA recording, separate QMF component exponents reduce RMS error from
0.359202 to **0.320218 LSB**, and samples exceeding 2 LSB from 464 to **286**.
Maximum error remains 3 LSB. Guest instruction overhead changes from +8.441% to
**+11.474%**. On real-only low-band paths the independent imaginary exponent
cannot improve accuracy; it still costs metadata and instructions.

The alternative 17+17 layouts measured lower RMS error at lower instruction cost
than independent 16-bit exponents on this corpus, while retaining the same
3-LSB worst case. Keep both options for further qualification; do not infer an
universal ordering from these recordings.

## Reproduction

From the repository worktree, using PowerShell 7 and the existing ESP-IDF setup:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-qmf-storage `
  -Sdkconfig build-qemu-aac-qmf-storage/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.qemu.defaults','sdkconfig.qemu-aac-qmf-storage.defaults')

python tools/codec_benchmark/run_aac_qmf_storage.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu /path/to/qemu-system-riscv32 --bios /path/to/qemu/share --wsl `
  --output .build/qmf-storage-synthetic

# Add --input path/to/recording.aac for a retained raw ADTS recording.
# Exit 2 reports a completed experiment that failed the PCM tolerance.
python tests/run-aac-storage.py
python tests/test-aac-storage.py
python tests/test-aac-pc16-write.py
```

Use the project's patched ESP32-C3 QEMU with the audio/OLED support required by
the existing harness. The recorded commands retain the exact executable and
BIOS paths used here. Production firmware and the connected board were not
changed by this experiment.

For the PS comparison, use build/config names `build-qemu-aac-ps-storage`, add
`sdkconfig.qemu-aac-packed-history.defaults` before
`sdkconfig.qemu-aac-ps-storage.defaults`, and run `run_aac_ps_storage.py`.

## Next implementation gate

Replace the audited low-QMF readers/writers with compact-storage accessors,
measure the necessary decoded workspace, and then resize the owner. Test
bit-exact lossless traversal first, followed by quantized decoding, resets,
mono/stereo/profile transitions, malformed data, full-radio heap/CPU and OTA.
The current representation passes the development corpus criterion, but still
needs both the allocation change and speed work. The final 2-LSB criterion also
remains open. Other memory areas retain their own entries in the
[experiment checklist](ESP32C3_AAC_MEMORY_EXPERIMENTS_20261002.md).

## Initial four-format active cases

The table below combines both experiments. RMS and counts use one complete run
(repeated counts agree); instruction percentages use the median of runs 2/3.
Synthetic fixtures did not allocate histogram buffers, so RMS is shown as `N/A`.
AAC-LC controls and non-PS recordings in the PS trial have zero PCM difference
and are retained in the raw matrix, but do not exercise the corresponding
compression path. `shared17/5` and `shared17/4` have identical PCM statistics.

| Area | Input | Format | Max LSB | RMS LSB | Samples >2 LSB | Instructions vs binary |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| QMF | he44100_stereo | shared16 | 3 | N/A | 254 | +16.300% |
| QMF | he44100_stereo | split16 | 3 | N/A | 254 | +18.638% |
| QMF | he44100_stereo | shared17/5 | 3 | N/A | 4 | +17.224% |
| QMF | he44100_stereo | shared17/4 | 3 | N/A | 4 | +16.737% |
| QMF | he48000_stereo | shared16 | 3 | N/A | 200 | +16.194% |
| QMF | he48000_stereo | split16 | 3 | N/A | 200 | +18.503% |
| QMF | he48000_stereo | shared17/5 | 3 | N/A | 5 | +17.106% |
| QMF | he48000_stereo | shared17/4 | 3 | N/A | 5 | +16.625% |
| QMF | hev2_44100_stereo | shared16 | 3 | N/A | 7 | +7.180% |
| QMF | hev2_44100_stereo | split16 | 3 | N/A | 7 | +8.592% |
| QMF | hev2_44100_stereo | shared17/5 | 3 | N/A | 1 | +7.763% |
| QMF | hev2_44100_stereo | shared17/4 | 3 | N/A | 1 | +7.400% |
| QMF | abba64 | shared16 | 3 | 0.359202 | 464 | +8.441% |
| QMF | abba64 | split16 | 3 | 0.320218 | 286 | +11.474% |
| QMF | abba64 | shared17/5 | 3 | 0.262609 | 121 | +9.120% |
| QMF | abba64 | shared17/4 | 3 | 0.262609 | 121 | +8.783% |
| QMF | groovesalad16 | shared16 | 3 | 0.294778 | 172 | +13.459% |
| QMF | groovesalad16 | split16 | 3 | 0.263236 | 82 | +17.529% |
| QMF | groovesalad16 | shared17/5 | 3 | 0.218240 | 54 | +14.651% |
| QMF | groovesalad16 | shared17/4 | 3 | 0.218240 | 54 | +14.060% |
| QMF | groovesalad32 | shared16 | 3 | 0.349741 | 376 | +19.627% |
| QMF | groovesalad32 | split16 | 3 | 0.349741 | 376 | +21.826% |
| QMF | groovesalad32 | shared17/5 | 3 | 0.282241 | 152 | +20.526% |
| QMF | groovesalad32 | shared17/4 | 3 | 0.282241 | 152 | +20.043% |
| QMF | groovesalad64 | shared16 | 3 | 0.354381 | 412 | +20.898% |
| QMF | groovesalad64 | split16 | 3 | 0.354381 | 412 | +22.706% |
| QMF | groovesalad64 | shared17/5 | 3 | 0.284954 | 169 | +21.360% |
| QMF | groovesalad64 | shared17/4 | 3 | 0.284954 | 169 | +20.912% |
| PS | hev2_44100_stereo | shared16 | 2 | N/A | 0 | +37.666% |
| PS | hev2_44100_stereo | split16 | 2 | N/A | 0 | +46.484% |
| PS | hev2_44100_stereo | shared17/5 | 2 | N/A | 0 | +41.421% |
| PS | hev2_44100_stereo | shared17/4 | 2 | N/A | 0 | +39.513% |
| PS | abba64 | shared16 | 3 | 0.275221 | 178 | +48.438% |
| PS | abba64 | split16 | 3 | 0.246376 | 103 | +67.880% |
| PS | abba64 | shared17/5 | 3 | 0.205390 | 54 | +52.940% |
| PS | abba64 | shared17/4 | 3 | 0.205390 | 54 | +51.060% |
