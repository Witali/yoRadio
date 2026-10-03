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

A fresh build of the shared numerical probe also passes all 36 synthetic paired
comparisons, repaired reset and lifecycle checks, with **2 LSB maximum** and the
same 6,144-byte cumulative owner-block saving. This rerun tests the shared source
after its move out of the QEMU-only file.

## Physical radio qualification

The awake DIO/80 MHz image was installed through the native WebUI while an
AAC-LC stream played. OTA completed in **20.953 seconds**; the running ELF hash
matched the uploaded image. Wi-Fi, playlist and settings comparisons passed,
with no retained panic/capture errors. Neither bootloader nor storage partitions
were rewritten.

Public streams were probed with FFprobe immediately before each test. Each
requested run lasts 60 seconds with status polling every 0.1 seconds. A transport
failure can end a run early; such a run is a failure, not a shorter passing test.

| Public stream | HTTP | HTTPS |
| --- | --- | --- |
| AAC-LC 128 kbit/s | Failed: WebUI transport error after about 38 s of observations | Passed; mean CPU 53.42% |
| HE-AAC 64 kbit/s | Failed: WebUI transport error after about 3 s | Failed: runtime allocation/TLS errors; only brief PCM |
| HE-AAC 32 kbit/s | Failed: runtime allocation errors; full 44.1 kHz stereo observed | Failed: runtime allocation/TLS errors; intermittent PCM |
| HE-AACv2 16 kbit/s | Failed: WebUI timeout; full 32 kHz stereo briefly observed | Failed: runtime allocation/TLS errors; no PCM observed |
| MP3 256 kbit/s | Passed; mean CPU 58.22% | Passed; mean CPU 66.03% |

HTTP records 24 allocation failures, all requesting 1,700 bytes. HTTPS records
38 failures, including network requests and a 47,980-byte compact owner request.
At failing allocations the minimum observed largest free block was **1,408 B**;
aggregate free heap reached minima of **4,632 B (HTTP)** and **4,240 B (HTTPS)**.
The extra owner saving therefore does **not** resolve full-radio memory pressure.
Both suites recovered their settled idle heap and restored settings/saved
playback after reboot.

The failed HTTP HE-AAC 32 kbit/s window averaged 56.23% CPU, but is not a passing
performance qualification. Failed HTTPS windows include stalled/idle time and
must not be presented as continuous HE-AAC decoding benchmarks. RSSI ranged
approximately -86..-74 dBm; the isolated AAC-LC HTTP transport error is not
attributed to compression, flash mode or signal strength without a controlled
comparison.

The separate local finite-file matrix passes **14/14 playback/EOF checks**:
MP3 320 kbit/s, FLAC level 8, Vorbis q10, Opus 510 kbit/s, HE-AAC 44.1/48 kHz
stereo and HE-AACv2 44.1 kHz stereo, each with automatic and explicit codec
selection. Board restoration also passes. These short LAN checks do not replace
the failing public radio/TLS workload above or long-running codec qualification.
Two additional HE-AACv2 EOF checks pass: REST retains `stream ended` with cleared
PCM metadata, and WebSocket reports the stopped state. No allocation/decoder
errors were retained during the local matrix. The saved station is playing
again on the verified new image after the tests.

Use `summarize_public_windows.py` for these logs. It clips CPU samples to each
recorded station window and leaves aggregates unavailable for short failed runs.
The older checkpoint-only summarizer could incorrectly use the next station's
CPU samples after an early error; its historical summaries should not be used
for those short cases.

**Not a production default.** Further RAM reduction and physical full-radio
qualification are required, followed by sustained playback/OTA and malformed
input checks. Numerical precision and a successful upload alone are insufficient.

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
