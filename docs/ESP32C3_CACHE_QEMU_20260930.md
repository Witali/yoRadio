# ESP32-C3 QEMU cache-traffic experiment — 2026-09-30

Follow-up: [physical board measurements](ESP32C3_CACHE_HARDWARE_20260930.md)
now provide actual cycle timing and a cold-data-line probe in a separate test
image. The model-only results below remain unchanged.

**Two independent QEMU boots produced identical cache traces for AAC-LC,
HE-AAC and HE-AAC v2.** The experiment adds reproducible modelled miss counts;
it does not measure physical cache latency or change the saved CPU coefficients.
The board was not reset or flashed.

## Results

Each boot decodes one warm-up pass and two measured passes per fixture with the
production AAC adapter and actual Espressif RISC-V codec. The table averages
the two measured passes and divides by their decoded PCM duration, rather than
QEMU time or host runtime. All cases output stereo, 16-bit PCM.

| Fixture | Continuous LRU misses / audio second | Cold-call LRU misses / audio second | Change in misses | Continuous FIFO misses / audio second | Continuous LRU refill MB / audio second |
| --- | ---: | ---: | ---: | ---: | ---: |
| AAC-LC, 48 kHz | 32,406 | 34,354 | +6.01% | 33,638 | 1.037 |
| HE-AAC, 48 kHz | 42,489 | 42,688 | +0.47% | 42,609 | 1.360 |
| HE-AAC v2, 44.1 kHz | 36,403 | 36,545 | +0.39% | 36,654 | 1.165 |

MB means 1,000,000 bytes; one modelled miss loads 32 bytes. Both instruction and
read-only data misses are included. **The percentages describe miss counts,
not CPU utilization or decoder slowdown.**

`continuous_lru` retains the shared cache between calls, including surrounding
harness activity. `cold_call_lru` clears the model before every decoder call,
including calls that only buffer incomplete input. It does not flush the guest's
cache. FIFO provides a second replacement assumption: it raises continuous
misses over LRU by 3.80%, 0.28% and 0.69%, respectively. Neither policy is claimed
to reproduce the chip's actual replacement policy or bound every possible policy.

For these traces, most misses remain present even when contents survive between
calls. The additional cost of starting each call empty is much smaller for HE
than for LC. This suggests that the measured HE access sequences already replace
much of the useful cache contents within calls. It does **not** establish that
cache stalls are insignificant, nor reconstruct interference from Wi-Fi/TLS.

## Workload and validation

| Fixture | Frames / pass | PCM samples / channel / pass | Decoder calls / pass | Instructions, pass 1 / pass 2 |
| --- | ---: | ---: | ---: | ---: |
| AAC-LC 48 kHz | 26 | 26,624 | 30 | 6,679,492 / 6,679,492 |
| HE-AAC 48 kHz | 15 | 30,720 | 17 | 19,591,786 / 19,591,786 |
| HE-AAC v2 44.1 kHz | 15 | 30,720 | 16 | 25,439,863 / 25,440,176 |

- Input chunks: 2,048 bytes copied into internal RAM; PCM buffer: 16 KiB in RAM.
  The original synthetic AAC files and hashes are retained in
  [`tests/fixtures/aac_stream_format/`](../tests/fixtures/aac_stream_format/).
- Firmware: ESP-IDF v6.0.2, 160 MHz configuration, Espressif codec package 2.6.2,
  runtime `v2.6.0-4-gfd141ab`. The full-rate AAC Plus adapter is enabled.
- Host: Linux under WSL, GCC 13.3.0, QEMU 9.2.2 built with TCG plugins enabled.
  QEMU source: `413834d79a1ac46570cdf4839f136e3b9a8e6ffd` of the yoRadio fork
  with SSD1306 and virtual PCM support. Source semantics were unchanged; the
  Windows source copy needed LF text and restoration of Git symlinks for Linux.
- `-icount shift=0,align=off,sleep=off`; the 1,024-NOP probe reports exactly
  1,025 instructions. The table's counts are identical to the same image run
  on the installed Windows QEMU without the plugin. The HEv2 pass difference
  is 313 instructions, about 0.00123%, with ticks permitted during decoding.
- PCM rate/channel/sample checks, heap integrity and OLED/audio/storage smoke
  checks pass. Minimum reported remaining test-task stack is 17,448 bytes.
- The plugin observes 1,724 MMU writes, with zero unmapped measured accesses
  and zero protocol/control errors. The two complete JSON traces have identical
  SHA-256 hashes: `bd29d0d80e7eb6eb189d5697f473735ca3dc45396ea74d2448174580bc5bee87`.
- Cache-model unit checks pass; nine analysis regression tests validate saved
  runs, matching instruction counts, and rejection of missing windows, lost
  mappings, wrong PCM, corrupt counters and firmware failures. Ten existing
  QEMU/codec Node tests also pass.

## What the model does and does not establish

The model uses the C3's 16 KiB, eight-way, 32-byte geometry from the
[ESP32-C3 datasheet, section 4.1.2.3](https://documentation.espressif.com/esp32-c3_datasheet_en.html).
It follows executed instruction fetches and successful flash reads, resolves
the shared IROM/DROM MMU mappings, and models a single cache. SRAM, ROM and MMIO
do not allocate lines. The model creates no dirty-line writebacks on this
read-only C3 cache; it is not a PSRAM-cache model for other ESP32 variants.

Physical flash tags, modulo set indexing, LRU/FIFO replacement, immediate refill
and the absence of prefetch are modelling assumptions. Cache-control commands,
bus contention, speculative fetch, critical-word-first timing, overlapping
transfers and cache locking are not simulated. Cache/MMU writes inside measured
calls fail the trace. Counts depend on this test image's linker layout, which
differs from the production image. Short tone fixtures are not a representative
sample of all broadcast material.

No numerical cache penalty is added to the empirical instruction-to-time
factors: their reference measurements already include cache stalls. A physical
refill penalty and corresponding reference/target stall costs remain unknown.
See the [calibration accounting explanation](ESP32C3_QEMU_CALIBRATION_20260930.md#cache-refill-and-eviction-costs).

## Saved evidence and repetition

Raw traces, serial logs, per-run summaries, a Windows run without instrumentation
and hashes/commands are in
[`tests/results/esp32c3-cache-qemu-20260930/`](../tests/results/esp32c3-cache-qemu-20260930/).
The emulator-only build is kept separate from production firmware. Virtual
waveform smoke files remain replaceable build outputs.

See [`tools/codec_benchmark/cache/README.md`](../tools/codec_benchmark/cache/README.md)
for the plugin build, exact model boundaries and commands to repeat the experiment.
