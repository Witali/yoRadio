# AAC late allocation failures and malformed frames — 2026-10-04

The real ESP32-C3 AAC library passes eight additional fault/recovery cases in
QEMU using the PC19 candidate, the native streaming adapter and the pointer
audit. This change adds tests; it does not change production decoding or promote
the experimental late-SBR/PC19 options.

## Results

| Case | Variants | Observed result | Recovery |
| --- | --- | --- | --- |
| SBR owner allocation fails after AAC-LC | Odd/even LC history bank | `ESP_AUDIO_ERR_MEM_LACK`, no PCM | Fresh HE-AACv2 decoder: 15 frames each |
| SBR control allocation fails after AAC-LC | Odd/even LC history bank | `ESP_AUDIO_ERR_MEM_LACK`, no PCM | Fresh HE-AACv2 decoder: 15 frames each |
| Header-only ADTS | 7-byte frame | Consumed with zero PCM | 15 HE-AACv2 frames |
| Truncated SBR payload | Retained core and extension type | Consumed with zero PCM | 15 HE-AACv2 frames |
| Oversized SBR FIL count | 269 bytes, exceeding frame | Consumed with zero PCM | 15 HE-AACv2 frames |
| Oversized ordinary FIL count | 269 bytes, exceeding frame | Consumed with zero PCM | 15 HE-AACv2 frames |

All eight cases clear the profile/source-channel metadata and allow complete
decoder destruction. Each checks guards around the 8 KiB PCM buffer and heap
integrity. The allocator hook verifies that its requested failure was exercised
and no SBR owner remains after close. The complete run records **700 allocations
and 700 frees**, with **1,186,057 pointer checks**. Recovery totals 120 HE-AACv2
frames at 44.1 kHz, two PCM channels, 16 bits.

The library normally logs that it has disabled AAC-Plus after SBR allocation
failure and continues with the AAC core. The adapter's existing allocation-failure
flag suppresses that partial output and returns memory failure, including after
13 or 26 successfully decoded LC frames. Recovery here follows the radio's
close-and-create-new-decoder path; same-handle OOM retry is not claimed.

The SDK's simple-decoder layer consumes all four malformed fixtures and returns
OK with zero output, despite an error from the inner AAC decoder. The initial
test incorrectly required a nonzero public error for the header-only frame.
Its assertion failure, source and ELF hash are retained under
`initial-contract-failure/`. The corrected test requires no PCM, cleared metadata,
cleanup and recovery; memory failure still strictly requires the memory error.

## Regression checks

The same process then passes the existing metadata, concurrent-decoder,
reset/cleanup, ordinary-format, missing/resumed-SBR and OLED/audio smoke tests.
The subsequent captured PCM is byte-identical to the preceding PC19 metadata
run: **675,840 SBR-gap samples + 189,440 transition samples = 865,280 channel
samples**, zero differences. This compares the PC19 candidate with its previous
output, not with the original uncompressed decoder; the earlier ±3-LSB precision
qualification remains a separate result.

The decoder task uses a 16,384-byte stack with a measured minimum of 2,844 bytes
free. These are instrumented QEMU checks, not physical CPU or network results.

## Scope and remaining checks

- Malformed fixtures are generated from checked FAAD FIL spans, preserving the
  core prefix and rewriting ADTS lengths. These four mutated frames have not
  separately been decoded by FAAD in this experiment.
- Heap integrity, PCM guards and the existing pointer audit do **not** instrument
  every input read inside the precompiled library. The decompiled
  `get_sbr_bitstream` advances `used_bits` from the advertised FIL count and uses
  unsigned remaining-byte subtraction. Add bounded-reader checks before treating
  malformed input safety as qualified; a no-PCM result alone is insufficient.
- Cover outer transport truncation at every byte boundary, same-decoder recovery,
  output-buffer retry/backpressure and a broader malformed corpus.
- Physical Wi-Fi/HTTPS, CPU, OTA and other-codec acceptance gates remain open.

## Reproduction and evidence

[Results and exact snapshots](../tests/results/esp32c3-aac-faults-20261004/)
include hashed diagnostics, config, generator/test/adapter sources and synthetic
PCM. The initial failed assertion is retained separately.

Build a QEMU configuration with compact adapter, pointer audit, late-SBR and
PC19 side-metadata enabled, as recorded in the evidence `sdkconfig`. Then run:

```powershell
python tools/codec_benchmark/generate_aac_faults.py
python tools/codec_benchmark/run_aac_faults.py `
  --build idf/esp32c3-oled-native/build-qemu-aac-faults-pc19 `
  --dependency-root C:/Work/yoRadio/.idf `
  --output .build/aac-faults/recheck `
  --qemu PATH/TO/qemu-system-riscv32 --bios PATH/TO/qemu/bios --wsl
python tests/test-aac-faults.py
```

`--wsl` is only for Linux QEMU launched from Windows. The runner operates on a
disposable QEMU flash image and does not flash a connected board.
