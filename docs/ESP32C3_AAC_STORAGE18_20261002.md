# AAC storage with 18 bit mantissas

Follow-up: [eight other AAC storage areas](ESP32C3_AAC_OTHER_ARRAYS_20261002.md),
with isolated PCM effects, payload sizes and the rejected IMDCT result.

## Result

The fifth experimental format stores **18-bit Re, 18-bit Im and one shared
four-bit exponent**. It improves measured PCM accuracy while occupying the same
space as 16+16 with independent component exponents or the byte-aligned 17+17
format. Native DSP scaling, output rates and channels remain unchanged.

The maximum PCM difference is still **3 LSB** on the exercised recordings,
within the updated production limit of 3 LSB and the development limit of 5 LSB.
See [current precision policy](ESP32C3_AAC_PRECISION_POLICY.md). The old 2-LSB
verdicts remain in archived measurements; full production qualification still
requires memory and speed work. No saturation occurred in the audio corpus.

## Representation

```text
mantissa word: [ Im bits 15..0 | Re bits 15..0 ]
metadata byte: [ Im bits 17..16 | Re bits 17..16 | shared shift bits 3..0 ]
                 2 bits          2 bits           4 bits
metadata word: [ pair 3 byte | pair 2 byte | pair 1 byte | pair 0 byte ]
decoded component = signed_18_bit_mantissa * 2^shift
```

The shift is selected from 0..14, enough for every signed-32 input; code 15 is
reserved and rejected by the decoder assertion. Rounding is nearest, ties away
from zero, with saturation for a positive rounding carry at shift 14. Sign
extension uses bounded arithmetic, with no signed left-shift or unaligned
cross-word mantissa access. Each pair occupies 40 bits including metadata before
array-end word padding.

The previous byte-aligned 17+17 representation left two metadata bits unused.
The new representation uses these to retain one more bit of each component;
metadata bit positions change accordingly. `PC_STORAGE_SHARED18_FOUR` is variant
5 in the QMF/PS test harness, not a new production default.

## Signal and storage comparison

QMF RMS combines four active captures, 9,859,072 scalar signed-16 PCM samples.
PS RMS uses the ABBA64 capture, 2,646,016 scalar samples. Each uses one run and
includes both channels where present; repeated runs agree. RMS is computed from
the total squared error divided by total sample count, not an average of file
RMS values. The original data is signed 32+32 per complex pair.

| Area | Format | Packed bytes | Reduction from original | RMS error, LSB | Max error, LSB | Samples above 2 LSB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| QMF, two low-band matrices (20,480 B native) | 16+16, separate exponents | 12,800 | 37.50% | 0.327956 | 3 | 1,156 |
| QMF | 17+17, four metadata entries/word | 12,800 | 37.50% | 0.266385 | 3 | 496 |
| QMF | **18+18, shared exponent** | **12,800** | **37.50%** | **0.209491** | **3** | **176** |
| PS delays (4,936 B native) | 16+16, separate exponents | 3,088 | 37.44% | 0.246376 | 3 | 103 |
| PS delays | 17+17, four metadata entries/word | 3,088 | 37.44% | 0.205390 | 3 | 54 |
| PS delays | **18+18, shared exponent** | **3,088** | **37.44%** | **0.164850** | **3** | **24** |

These are separate QMF and PS experiments. QMF packs/unpacks newly generated
analysis rows before the unchanged downstream DSP; PS replaces actual delay
feedback writes. The enclosing allocations are unchanged, so **actual heap
saving is zero**. PS aliases the right-channel low-QMF region, and these payload
estimates cannot be added. Full allocation integration remains a separate task.

## Work comparison in the same build

The table reports median guest instruction overhead relative to the original
binary decoder in runs 2/3. Runtime format selection, instrumentation and
pack/unpack wrappers are included. These are QEMU instructions, not ESP32-C3
CPU cycles or physical load. Adding a format can change compiler inlining/code
layout, so use this new five-format build for comparisons rather than mixing its
timings with the earlier four-format build.

| Area | Input | 17+17, four entries | 18+18, four entries |
| --- | --- | ---: | ---: |
| QMF | Synthetic HE 44.1 kHz | +20.320% | +20.343% |
| QMF | Synthetic HE 48 kHz | +20.182% | +20.169% |
| QMF | Synthetic HE v2 44.1 kHz | +8.748% | +8.825% |
| QMF | ABBA64 | +10.205% | +10.295% |
| QMF | Groove Salad 16 | +16.378% | +16.558% |
| QMF | Groove Salad 32 | +24.199% | +24.094% |
| QMF | Groove Salad 64 | +25.168% | +24.770% |
| PS | Synthetic HE v2 44.1 kHz | +41.516% | +41.894% |
| PS | ABBA64 | +53.207% | +53.115% |

Thus 18+18 has similar measured instruction demand to byte-aligned 17+17, with
lower RMS error on this corpus. It still costs more work than the native binary
decoder. A specialized implementation and physical measurements remain needed.

## Verification and reproduction

- Independent signed-64 arithmetic oracle: 1,000,000 random pairs and 167,322
  boundary pairs across five formats, plus signed-range edge combinations.
- Exact reconstruction of all 262,144 signed-18 mantissas with complementary
  real/imaginary values and shift zero; a fixed known mantissa/metadata word.
- Metadata neighbour/tail guards and host undefined-behavior sanitizer.
- The target repeats the oracle on 10,000 random pairs before decoding.
- 153 QMF and 177 PS paired comparisons: six synthetic files and five retained
  recordings, full output-shape checks, binary/native-source controls,
  per-channel histograms for recordings and zero observed saturation.
- All four earlier formats retain their previous PCM error counts, moments and
  histograms. Input/fixture hashes also match. Parser tests reject missing
  fifth-variant rows, misleading format counts and incomplete/corrupt evidence.

Use the build commands in the [QMF storage report](ESP32C3_AAC_QMF_STORAGE_20261002.md#reproduction).
The same QMF/PS profiles now exercise five formats. Validation commands:

```powershell
python tests/run-aac-storage.py
python tests/test-aac-storage18.py
python tests/test-aac-storage.py
python tests/test-aac-pc16-write.py
```

The latter two tests preserve compatibility with the initial four-format and
PC16 evidence. Raw logs, results, source/configuration snapshots and SHA-256
provenance are saved in
[`tests/results/esp32c3-aac-storage18-20261002`](../tests/results/esp32c3-aac-storage18-20261002/).
The [consolidated table](ESP32C3_AAC_QMF_STORAGE_20261002.md#consolidated-signal-and-storage-comparison)
now includes all five representations.
