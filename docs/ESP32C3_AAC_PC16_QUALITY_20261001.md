# ESP32-C3: PC16 history decoding quality

## Result

The 16+16 mantissa format with eight separate four-bit exponents per word and
`shift=exponent+1` passes the **temporary ±5 signed-16 PCM LSB** gate on the tested
corpus. It **does not pass the final ±2 LSB** gate: the maximum remains 3 LSB.
The synthetic HE-AAC v2 maximum improves from 7 LSB with 14+14+4 storage to 3 LSB.

This is a QEMU experiment with the actual pinned Espressif C3 decoder. It changes
retained histories by packing/unpacking them; actual live RAM saving is still
**zero**. No production firmware or board was changed.

## Measurements

Below, both SBR and PS histories are selected. Counts are scalar PCM samples,
summed across channels, from one run; three runs reproduce the same results.

| Input | Previous 14-bit maximum | PC16 maximum | Samples beyond ±2 | Total samples | RMS error L / R, LSB |
| --- | ---: | ---: | ---: | ---: | --- |
| Synthetic HE-AAC v2, two passes | 7 | 3 | 1 | 122880 | Not collected |
| ABBA 64 kbps, PS active | 3 | 3 | 96 | 2646016 | 0.226845 / 0.228139 |
| Groove Salad 16 kbps, complex SBR without PS | 3 | 3 | 34 | 1921024 | 0.151813 / 0.151813 |
| Groove Salad 32/64 kbps, real-only SBR path | 0 | 0 | 0 | 2646016 each | 0 / 0; packed history inactive |
| Groove Salad 128 kbps, AAC-LC | 0 | 0 | 0 | 2646016 | 0 / 0; no SBR |

No sample exceeds ±5. On ABBA the >2 count falls from 1499 to 96; on Groove Salad
16 kbps it falls from 304 to 34. These rare remaining three-LSB errors still fail
the final maximum-error requirement, regardless of the low average error.

Raw evidence and per-channel histograms, means, maxima and quantiles are in
[`tests/results/esp32c3-aac-pc16-history-20261001`](../tests/results/esp32c3-aac-pc16-history-20261001/).
The previous results are retained in the [14-bit report](ESP32C3_AAC_PACKED_HISTORY_20261001.md).

## Coverage and controls

There are **201 paired comparisons**: 81 from six synthetic LC/HE/v2 fixtures and
120 from five unchanged 30-second ADTS captures. Separate baseline/candidate
decoders receive the same input, with no gain adjustment, resampling or output
alignment. The harness checks consumed bytes, output lengths, rates, channels,
16-bit PCM and output guards. Existing in-stream format tests also pass.

Variants 1/2/3 use `pc16_pack8`/`pc16_unpack8` for full groups and the scalar API
for tails, on SBR/PS/both. Variants 4/5/6 use scalar storage on the same respective
histories. Variant 7 traverses histories without quantization; 0 bypasses the
wrapper. Coverage counters verify which paths actually ran, including tails.

Block and scalar variants have identical maximum/count statistics, changed-history
counts and shifts in all runs. Their full per-channel histograms and error moments
also match on recordings. The prior arithmetic test separately verifies bitwise
block/scalar storage equivalence. All lossless controls are PCM-identical to the
baseline. Zero remains zero and no tested history input saturates PC16.

The RV32 arithmetic test passes all 65536 mantissa codes at all 16 exponents,
plus 4096 eight-pair blocks against an independent int64 division oracle,
including INT32_MIN/MAX. It verifies the actual target-compiled quantizer.

The history layout, private ABI guards and 544 SBR / 653 PS pair counts are the
same as in the 14-bit experiment. Real-only SBR and LC controls are explicitly
marked `not_exercised`. They cannot establish packed-history precision. These
fixtures do not cover every legal AAC bitstream or every tool/profile.

## Timing limitations

Both-history block trials add about 9.122% QEMU guest instructions on synthetic
HEv2, 10.718% on ABBA and 6.469% on Groove Salad 16 kbps. Counts exclude the raw
PCM comparison but include history traversal, original-value copies, bounds and
diagnostic counters. Only runs 2/3 contribute to the timing summary.

These are not physical CPU measurements or the overhead of a completed compact
decoder. This test cannot establish how much time eight-at-once processing will
save once packing is fused into actual history writes. Hardware cache timing and
the old calibration coefficient are not applied.

## Reproduce

From the active worktree, using the installed ESP-IDF tools and Linux QEMU:

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& ./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-pc16-history `
  -Sdkconfig build-qemu-aac-pc16-history/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.qemu.defaults', 'sdkconfig.qemu-aac-packed-history.defaults', 'sdkconfig.qemu-aac-pc16-history.defaults')

& $python tools/codec_benchmark/run_aac_pc16_history.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --output .build/aac-pc16-quality/synthetic

& $python tests/test-aac-pc16-history.py
```

For a retained recording, add `--input path/to/recording.aac` and use a separate
output directory. Captures are local ignored inputs; their hashes and FFprobe
metadata are retained in each result. The six synthetic fixtures are tracked.
The runner never accesses a board. Exit 0 means the selected **development** gate
passed; consult `production_precision_pass` separately for the final ±2 gate.

The [separately tested supplied FAAD PS-storage patch](FAAD2_PS_PATCH_QUALITY_20261001.md)
has a different scope and write boundary; it reaches 2 LSB on its active-PS inputs.
Its quality cannot be inferred from these PC16 results.
