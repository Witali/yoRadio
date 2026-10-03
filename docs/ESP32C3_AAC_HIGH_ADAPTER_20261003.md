# PC18 high-QMF history in the production AAC adapter

The experimental `CONFIG_YORADIO_AAC_HIGH_HISTORY` option integrates the
[smaller high-history owner](ESP32C3_AAC_HIGH_HISTORY_20261003.md) into the real
radio decoder. It depends on `CONFIG_YORADIO_AAC_COMPACT_SBR`. Both remain
opt-in until physical radio qualification passes. Full-rate SBR/PS arithmetic,
channel counts and AAC format support are unchanged.

## Ownership and memory

`aac_high_history.c` is shared by the numerical probe and production adapter.
Production gets the active frame and copy counters from the decoder's TLS-scoped
context. Numerical statistics and verification unpacking are absent from the
production image. There is no shared mutable history or additional unpack buffer:
the native working rows receive reconstructed values.

| Item | Previous lossless adapter | PC18 adapter |
| --- | ---: | ---: |
| Requested SBR owner | 49,708 B | 47,980 B |
| Unguarded owner allocator block | 51,200 B | 49,152 B |
| Per-decoder adapter context | 8 B | 24 B |
| High-history payload, stereo | 4,608 B | 2,880 B |

PC18 saves another **2,048 B in the owner block**, at a **16 B per-decoder
context cost**. The cumulative owner-block saving is 6,144 B against the original
55,296-byte block. These are allocation-level figures, not a claim that the
entire radio has that much more free heap. Under light heap poisoning the
adapter test reports 49,140 B usable allocation; the separately retained
unguarded allocator probe measures the full 49,152-byte block.

The consumer audit and all 87 compiler-derived instruction patches from the
high-history experiment still apply. Reset uses typed compact frames; PS
relocation and the preserved imaginary history on real-only reset retain their
audited semantics. Each decoder frees its own owner. SBR allocation failure
returns `ESP_AUDIO_ERR_MEM_LACK` with zero output, rather than accepting the
vendor's reduced-format fallback.

## QEMU qualification

- Ten format/reopen checks include AAC-LC mono/stereo, HE-AAC at 44.1/48 kHz,
  HE-AACv2 stereo and restart after format changes.
- Both SBR allocation-failure paths, two direct resets, ordinary allocation in
  an unrelated task, cleanup and poisoned-heap integrity pass.
- Two tasks decode HE-AACv2 concurrently. A test-only yield deliberately leaves
  both decoder frames active at once. Each produces 61,440 PCM samples with
  checksum `2cf5d6da`, identical to an independent sequential decode. Production
  contains neither this yield nor its counters.
- Compared with the retained native/lossless output WAV, **10 of 657,540
  signed-16 channel samples differ**, all by **1 LSB**; RMS error is
  **0.00389977 LSB**. WAV shape/duration are identical. This WAV includes the
  normal output gain/resampling path. The earlier direct-decoder corpus result
  remains **2 LSB maximum**, below the production limit of 3.

[Raw evidence and source snapshots](../tests/results/esp32c3-aac-high-adapter-20261003/)
retain the configuration, PCM hashes, logs and compiler patch provenance.
This finite corpus is not a universal error bound. The known unchanged-ADTS-header
implicit-SBR transition limitation remains; stream restart is still required.

## Reproduce

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-qemu-aac-high-adapter `
  -Sdkconfig build-qemu-aac-high-adapter/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.qemu.defaults',`
    'sdkconfig.qemu-aac-compact-adapter.defaults','sdkconfig.aac-high-history.defaults')
python tools/codec_benchmark/run_aac_high_adapter.py --help
python tests/test-aac-high-adapter.py
```

The runner requires `--reference-wav`, `--dependency-root`, `--qemu` and `--bios`;
use `--wsl` with Linux QEMU. The reference WAV hash is retained in the result.
The physical awake build uses `sdkconfig.defaults`, `sdkconfig.aac-ram.defaults`,
`sdkconfig.cpu-profile.defaults`, `sdkconfig.cpu-profile-http.defaults`,
`sdkconfig.iram-safe.defaults`, `sdkconfig.tcp-pcb-pool.defaults`,
`sdkconfig.tls-dynamic.defaults` and `sdkconfig.aac-high-history.defaults`.
Its application and exact configuration are saved under
`firmware/development/esp32c3-aac-high-history/`.
