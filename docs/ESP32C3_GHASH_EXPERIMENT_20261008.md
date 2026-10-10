# ESP32-C3 GHASH byte recurrence experiment

Date: 2026-10-08. ESP-IDF revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`.

## Decision

**Keep `CONFIG_YORADIO_GCM_BYTE_GHASH` disabled.** The host comparison is bit
exact, but the physical FLAC HTTPS test still fails with watchdog events and
delayed DMA service. This is an experimental implementation and a retained
negative performance result, not a production optimization.

The existing task measurements put about 35% of CPU time in `radio_stream`
during the heavy FLAC case. That task includes TLS, HTTP and input delivery;
this is not a measurement attributing all of that time to GHASH. The current
linked-code audit proves the new dispatch exists, but does not count dynamic
calls or establish how much playback time reaches each branch.

## Exact arithmetic and scope

The SDK's four-bit recurrence processes the low and high nibbles of a byte:
`S4(S4(Z) XOR H[lo]) XOR H[hi]`. Polynomial shifts are linear, so this equals
`S8(Z) XOR S4(H[lo]) XOR H[hi]`. The experiment prepares `S4(H[i])` for all 16
entries once per GHASH call of at least 128 bytes. Short calls retain the
original code. It preserves the SDK's zero padding, partial-block buffering,
tag calculation and context layout; it does not reduce cryptographic precision.

The reference multiplication is the independent bit-serial Algorithm 1 in
[NIST SP 800-38D, sections 6.3–6.4](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf).
The upstream [Mbed TLS optimization discussion](https://github.com/Mbed-TLS/mbedtls/pull/9489)
concerns a different implementation and Xtensa measurements; its speedups are
not evidence for this ESP32-C3 experiment.

A build-local copy replaces the audited `esp_aes_gcm.c` in `tfpsacrypto`.
The generator pins the normalized source and context-header hashes, rejects
unknown versions, and leaves the shared SDK unchanged. The temporary table is
explicitly wiped before return. There are no heap allocations or new mutable
global state. As with the original implementation, lookup indices depend on
GHASH values; this is not a constant-time or side-channel qualification.

## Verification

Both the original SDK math and the candidate passed ASan/UBSan with:

- 16 zero/all-ones/alternating input pairs and 16,384 basis-vector pairs;
- 8,192 random products, including in-place operation and all 16 byte alignments;
- 640 lengths, covering every short length through 511 bytes and long inputs
  near 16 KiB, with guard bytes and exact-sized input allocation;
- 176 independently generated AES-128/256-GCM tag equations, each delivered
  whole, byte-by-byte and in mixed chunks through the actual SDK GHASH buffer;
- rejection of altered SDK source or context layout.

The independent tags use Python `cryptography` AESGCM, while the C test uses a
separate bit-serial field multiplication. This host seam extracts SDK GHASH and
buffering functions; it does not execute the hardware AES peripheral or the
complete ESP GCM authentication API. The linked RISC-V check confirms the
large/small dispatch, fast multiply, explicit wipe, flash reduction table and
absence of allocation calls in the large-block helper. AAC, HTTP and TLS
allocation-route link checks also pass.

```powershell
python tools/codec_benchmark/run_gcm_ghash_host.py --idf C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6 --output .build/ghash-host-new
```

For a diagnostic firmware, append `sdkconfig.gcm-byte-ghash.defaults` to the
defaults list in a fresh build directory. The exact tested build recipe is in
the archive below. Do not enable the option in production based on host math
tests alone.

## Physical results

Same heavy cases and 1 ms tick as the
[scheduler experiment](ESP32C3_FREERTOS_TICK_20261008.md): FLAC HTTPS for 60
seconds and HE-AACv2 alternating 1/16 KiB TLS records for 90 seconds. CPU and
decoder values use complete windows after ten seconds of warmup. The baseline
is the earlier staged-DMA image, not a freshly randomized control.

| Case / implementation | Mean CPU | Stream-task CPU | Decoded audio / wall time | DMA overruns / observed time | New watchdog events |
| --- | ---: | ---: | ---: | ---: | ---: |
| FLAC / baseline | 100.00% | 34.65% | 0.96588 | 154 / 45.109 s | 11 |
| FLAC / byte GHASH | 100.00% | 34.79% | 0.96323 | 159 / 45.062 s | 11 |
| HE-AACv2 / baseline | 74.76% | 0.44% | 1.00158 | 0 / 75.110 s | 0 |
| HE-AACv2 / byte GHASH | 72.63% | 0.37% | 1.00156 | 0 / 75.110 s | 0 |

AAC passed its original short-run gates and retained full 44.1 kHz stereo.
FLAC failed the original runtime gate; its measured real-time deficit was
3.68%. No allocation failure or SDK write error was captured. DMA/CPU telemetry
coverage was complete. Queue overruns indicate delayed descriptor service,
not an exact number of audible gaps. No acoustic capture was made. Sequential
run conditions and code placement can affect these small differences; the
AAC CPU difference alone does not qualify a general speedup.

The candidate's minimum observed unused `radio_stream` stack was 1,868 bytes
versus 1,936 bytes in the baseline. These are whole-task high-water marks,
including other paths, not the incremental cost of this function. GCC reports
a 304-byte frame for the large-block helper, containing the 256-byte table;
the unchanged small-block body uses 48 bytes. They are separate dispatch paths.

| Linked section | Baseline | Candidate | Change |
| --- | ---: | ---: | ---: |
| IRAM text | 47,690 B | 47,690 B | 0 B |
| DRAM data | 12,856 B | 12,856 B | 0 B |
| DRAM BSS | 45,664 B | 45,664 B | 0 B |
| Flash text | 1,158,788 B | 1,159,402 B | +614 B |
| Flash rodata | 395,444 B | 396,484 B | +1,040 B |

The app grows by 1,664 bytes to 1,619,792 bytes. The physical controller
restored the previous quiet image and verified unchanged Wi-Fi, playlist,
settings and the original playing state over 15 seconds.

## Remaining investigation

1. Measure calls, byte counts and time inside the full TLS/AES/HTTP path before
   assigning the stream task's CPU budget to a particular primitive. Sparse
   watchdog PCs are not an unbiased profiler.
2. Compare the byte reduction table with fixed XOR/shift reduction. For an
   eight-bit remainder `r`, the same reduction word is
   `(r << 17) XOR (r << 22) XOR (r << 23) XOR (r << 24)` using uint32 arithmetic.
   This may avoid the additional 1 KiB indexed flash table; performance is
   unmeasured and the variant is not enabled in this build.
3. Before any promotion, exercise invalid authentication tags/ciphertext,
   nonce/AAD and record fragmentation, concurrent contexts, full format/OTA
   coverage and longer playback. Preserve the separate AAC heap-trend failure
   described in the [TLS reserve report](ESP32C3_TLS_RX_RESERVE_20261008.md).

## Saved artifacts

[Raw evidence, exact sources and hashes](../tests/results/esp32c3-gcm-byte-20261008/)
include the first and final host runs, deterministic synthetic vectors, build
logs, linked audits, stack usage, physical reports and restoration checks.
The [laboratory image](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-ghash8/)
has ELF SHA-256 `403b436a3a3298244732f5406a4f3a7de3b451edace3262be215cf0ce0a23196`
and app SHA-256 `d584e98569c95a426a8c828afe2d54d3ccee8beedebf2e6f25c2740fdc309a65`.
It includes a temporary test CA and remains **NOT_QUALIFIED**. No private keys
or broadcast recordings are archived.
