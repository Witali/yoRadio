# ESP32 C3 HE AAC delivery rate and buffer use

Two ten-minute HTTPS runs compare real-time delivery (1.00x) with a two-percent
surplus (1.02x) on the same saved diagnostic QIO firmware. The comparison tests
whether receive-queue filling explains the earlier falling-heap result. It
also records delayed DMA queue service independently of the original gates.

## Purpose of the delivery margin

The fixture server's historical 1.02x default provides extra encoded data so
that the source does not throttle a throughput test. The number is a test
choice, not an AAC or HTTP requirement. It configures server delivery only.
The firmware does not request a two-percent playback speed increase.

For this HE-AACv2 fixture, the average encoded rate is 4,000.869 bytes per
audio second. A two-percent surplus is approximately 80 bytes/s, or 48,010
bytes over ten minutes relative to exactly real-time consumption. This is
12 seconds of extra audio. Some surplus can remain in the host's socket
buffers; completed socket writes do not establish board receive ownership.

Use an explicit `--pacing-ratio 1.0` when testing real-time source delivery and
`--pacing-ratio 1.02` when testing overfeeding/backpressure. Both are needed:
an excess-rate run can hide starvation, and real-time delivery alone does not
qualify full receive queues. The historical default and acceptance thresholds
remain unchanged.

## Measurement scope

The diagnostic image has dynamic TLS RX reservation, adaptive input buffers,
full compact AAC with SBR/PS, and staged DMA profiling. It differs from the
quiet production image. Each run starts after a fresh boot of the same image,
uses the same fixture and trusted TLS server, and includes continuous WebUI
polling, idle baseline and recovery. The order is 1.00x, then 1.02x; this is one
paired comparison, not randomized repeated trials.

The server writes up to 1,024 encoded bytes at a time, paced by average media
duration. At this bitrate, a full chunk represents about 256 ms of audio.
This is not per-frame timing; scheduling jitter and encoded frame-size
variation can affect input starvation independently of long-term clock drift.

## Results on the board

| Measurement | 1.00x | 1.02x |
| --- | ---: | ---: |
| Original sustained-load verdict | PASS | FAIL: progressive heap loss |
| CPU busy, time-weighted | 60.630% | 60.624% |
| CPU-log free heap, first / last three-sample median | 26,300 / 26,308 B | 26,356 / 18,540 B |
| CPU-log minimum free heap | 25,828 B | 14,784 B |
| Minimum largest free block | 17,408 B | 4,608 B |
| Same-snapshot heap/receive pairs | 116 | 116 |
| Maximum outstanding TCP receive credit | 1,053 B | 8,640 B |
| Heap/receive-credit Pearson r | -0.9461 | -0.9883 |
| Active connections / TIME_WAIT | 2 / 0 | 2 / 0 |
| DMA queue-overrun delta during selected playback | 98 | 0 |
| DMA write errors | 0 | 0 |
| Decoded audio / wall time | 0.999800 | 1.001579 |
| Settled idle heap before / after | 133,384 / 133,408 B | 133,336 / 133,372 B |
| Settled idle largest block before / after | 106,496 / 106,496 B | 106,496 / 106,496 B |
| Median RSSI | -64 dBm | -64 dBm |

The CPU-log values retain the original gate's sampling method. Independent
NET_HEAP snapshots have minima of 25,152 B and 14,796 B; sampling instants
differ. Both captures have complete selected telemetry and no recorded runtime
faults. No CPU-budget threshold is applied.

The 1.00x run keeps memory stable, but its 98 delayed DMA queue-service events
prevent a claim of gap-free playback. They occur inside the playback window,
after excluding warmup and idle. This counter is not an exact acoustic gap
count. The 1.02x run records zero such events but repeats the original memory
trend failure. Neither result is rewritten as a complete playback pass.

The strong association of receive credit with heap consumption at 1.02x,
stable connection counts, and settled recovery after Stop support receive
queue filling as the main explanation for this observed trend. Credit counts
payload rather than allocator capacity and must not be subtracted from heap
to override a failure. A smaller leak is not excluded by this one comparison.
The correlation is descriptive; samples are not independent trials.

The test used saved image `idf61-flash-qio80`, app SHA-256
`eb80d669af3122324370fc776c0a752a70cd83162a673049412890c4eb5d991c`.
Afterward, app-only OTA restored `idf61-qio80-8c1f2d2d`, app SHA-256
`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
The expected ELF identity and three playing AAC status observations were
verified. Wi-Fi, playlist and settings comparisons all passed.

## PDM clock hypothesis and follow up

The subsequent [integer versus fractional clock experiment](ESP32C3_PDM_CLOCK_20261009.md)
confirms the configured divider fields on the board and compares two
ten-minute real-time HE-AACv2 runs. The source/binary findings below describe
the evidence available during this initial pacing comparison.

The pinned ESP-IDF revision is `9a97f6c54ec638111ce55cd36581b3c192f15207`.
The application's DAC configuration requests 48,000 PCM frames/s, selects a
160 MHz source, and uses BCLK division 13 with 128 PDM clocks per PCM frame.
The precise MCLK divider would be `625/312`, or `2 + 1/312`.

After computing that divider, the SDK applies a PDM noise workaround that
writes the integer divider with zero fractional numerator. Source inspection
and disassembly of the measured ELF both show this operation. Assuming the
nominal source and this effective divider, the predicted output is:

```text
160,000,000 / (2 * 13 * 128) = 48,076.9230769 PCM frames/s
error relative to 48,000 = +0.160256%, or +1,602.56 ppm
extra consumption over 600 seconds = 0.961538 audio seconds
```

This is a source/binary prediction, not a live-register or physical frequency
measurement. The SDK's cached BCLK information remains the requested value
after the overwrite, so `i2s_channel_get_info()` alone cannot confirm the
effective rate. The application resampler currently assumes exactly 48 kHz.

Espressif documents the PCM-to-PDM upsampling relationship in its
[I2S guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/peripherals/i2s.html#pdm-tx-mode-in-pcm-format-with-pcm-to-pdm-converter).
The precise workaround is retained in the archived pinned SDK sources and
linked disassembly. Its purpose is noise reduction; changing the clock needs
audio-quality validation.

## Exact nominal 48 kHz is representable

Keeping BCLK division 13 and OSR 128, MCLK division `2 + 1/312` gives exactly
48,000 PCM frames/s relative to a nominal 160 MHz source. The SDK mapping uses
integer=2 and raw fractional fields X=311, Y=0, Z=1, YN1=0. These fit the C3
register fields. See the [C3 TRM](https://documentation.espressif.com/esp32-c3_technical_reference_manual_en.pdf),
sections 29.6 and register 29.18. Absolute accuracy still follows the reference
crystal; this calculation removes the deliberate divider error.

For an experiment, restore the calculated fractional divider after the PDM
noise overwrite, before enabling output, using the SDK's named HAL fields,
critical section and required divider-update sequence. This is an initialization
change, so it does not add work to the decoding loop. It needs a build option,
live-register readback, sustained playback comparison and noise measurement.
The follow-up implements the optional divider and register readback, tests
both settings on the board, and retains analog noise qualification as pending.

Changing only the PCM-to-PDM FP/FS ratio is not a verified substitute. The
pinned driver truncates FP/FS to an integer oversampling ratio and writes that
ratio separately; the TRM describes the low FP register bits as reserved.
The apparent generic ratio in the API documentation is insufficient to claim
that arbitrary fractional FP/FS values correct the C3 output clock.

## Noise checks without extra hardware

Registers, DMA timing, underflow diagnostics and known digital test samples
can be checked on the existing board. These checks do not measure analog
noise. Listening through the existing audio path can reveal gross changes,
but does not establish SNR or THD+N.

The I2S guide documents internal GPIO data loopback and independent PDM TX/RX
simplex channels. A dedicated diagnostic might capture raw digital PDM for
software filtering and spectral comparison. It needs an implementation and
timing/coverage validation; ordinary PDM full-duplex is not supported. Even a
successful digital loopback omits GPIO edge amplitude/timing effects, supply
noise, the physical RC network and the amplifier. Analog noise qualification
requires recording the filtered analog output through an ADC or audio input.
The chip's ADC has no existing internal connection to that external node.

## Next checks

1. Read the live source/divider and PCM-to-PDM fields using their named SDK
   fields, then confirm the effective output rate against time or an external
   capture. Preserve the current low-noise clock sequence.
2. Test the representable fractional clock first and compare its noise with the
   existing integer setting. If noise requires keeping the integer clock, test
   matching resampling to the effective rate, including the existing 48 kHz
   bypass, and quantify PCM accuracy and CPU cost at all supported rates.
3. Repeat real-time delivery with controlled initial prebuffering to distinguish
   mean clock drift from the server's 1,024-byte delivery bursts and Wi-Fi jitter.
4. Retain the 1.02x backpressure test, inspect settled heap windows and Stop
   recovery, and qualify production settings separately before enabling changes.

## Saved evidence and replay

[Evidence archive](../tests/results/esp32c3-heap-pacing-20261009/) includes
original reports, status/performance samples, server delivery windows, image
identities, OTA persistence checks, source snapshots and a SHA-256 index.
The six staged-DMA parser tests and four heap/receive pairing tests pass.
No Wi-Fi configuration snapshot or TLS private key is stored in the archive.

Replay the measurements without contacting the board:

```powershell
python tools/esp32c3_tests/heap_receive_correlation.py --input tests/results/esp32c3-heap-pacing-20261009/physical/rate100 --output .build/pacing-rate100-heap.json
python tools/esp32c3_tests/heap_receive_correlation.py --input tests/results/esp32c3-heap-pacing-20261009/physical/rate102 --output .build/pacing-rate102-heap.json
python tools/esp32c3_tests/staged_dma.py --input tests/results/esp32c3-heap-pacing-20261009/physical/rate100 --output .build/pacing-rate100-dma.json
python tools/esp32c3_tests/staged_dma.py --input tests/results/esp32c3-heap-pacing-20261009/physical/rate102 --output .build/pacing-rate102-dma.json
```

The archived controller describes the physical procedure. A new physical run
needs a currently valid laboratory certificate matching the firmware's test
trust root, a fresh output directory and the correct connected board.
