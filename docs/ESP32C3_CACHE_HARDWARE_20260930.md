# ESP32-C3 hardware cache and AAC measurements — 2026-09-30

## Decoder results

Measured on the SuperMini OLED ESP32-C3 revision 0.4, 160 MHz, embedded XMC
4 MB flash, DIO at 80 MHz. **Deep sleep was disabled.** The exact same test
application bytes ran on the board and in QEMU. Each runtime was booted twice;
each boot measured four rounds of three passes in each mode, after warm-up.
That gives 24 hardware windows per table cell, 144 decoder windows in total.

| Stereo fixture | Continuous decoder CPU | Cold-call decoder CPU | Relative slowdown | Cycles / QEMU instruction, continuous |
| --- | ---: | ---: | ---: | ---: |
| AAC-LC, 48 kHz | 16.708% | 17.037% | +1.964% | 2.18182 |
| HE-AAC, 48 kHz | 34.551% | 34.576% | +0.073% | 1.80122 |
| HE-AAC v2, 44.1 kHz | 44.580% | 44.612% | +0.071% | 1.95535 |

CPU percentage is `decoder cycles / 160,000,000 / PCM seconds * 100`.
This table excludes Wi-Fi, output, OLED, logging, fixture copies, cache-flush
time and interrupts. The largest continuous-mode call took 4.773, 17.925 and
22.523 ms respectively; consult the machine-readable summary for exact values.
All cases produced the expected full-rate stereo 16-bit PCM. No 22 kHz limit
was used. Maximum cycle spread was 0.230% for LC and below 0.008% for HE/v2;
repeatability of these short tones is not a bound on other music or bitrates.

`continuous` preserves cache contents between calls but still incurs misses
within the decoder. `cold` invalidates the entire cache before every call,
including parser-only calls. It is a controlled perturbation, not a model of
normal Wi-Fi interference or a worst-case execution-time guarantee. A small
cold/continuous difference does not mean cache stalls are small: both runs
already miss frequently within calls.

## Physical data-cache probe

The probe runs from IRAM and reads one word per distinct 32-byte flash line.
It immediately repeats the reads with those lines cached. Interrupts are masked.
The hardware data counter reports exactly N misses for N cold lines and zero
on the repeated reads; instruction misses are zero. This validates data-counter
line semantics for this probe. Instruction-counter line semantics have not been
independently checked by an instruction-only microprobe.

| Lines read | Cold cycles | Warm cycles | Extra cycles / cold line |
| ---: | ---: | ---: | ---: |
| 1 | 115 | 12 | 103.000 |
| 8 | 2,397 | 61 | 292.000 |
| 64 | 20,653 | 453 | 315.625 |
| 256 | 83,245 | 1,797 | 318.156 |

All 16 repetitions at each size matched. The observed differences follow
`extra cycles = 319 * lines - 216` for these four sizes: the marginal cost is
319 cycles (about 1.994 microseconds), while an isolated read adds 103 cycles
(about 0.644 microseconds). This is a measured sequential data-read pattern,
**not a universal per-miss penalty**. Timing the CPU's read completion does not
necessarily time completion of an entire flash line. Prefetch/overlap/early
restart and instruction-fetch behavior cannot be inferred from this probe alone.

In the decoder experiment, `(cold cycles - continuous cycles) / additional raw
I+D misses` was about 299, 326 and 324 cycles for LC, HE and v2. These are observed
aggregate ratios for the perturbation, not independently separated stall cycles.
Do not multiply every miss by 319 and add it to an already calibrated decoder
estimate: that would count the reference cache cost twice.

## Scoped coefficients for future benchmarks

The [saved hardware profile](../tools/codec_benchmark/calibration/esp32c3-aac-cache-hardware-160mhz.json)
records the three factors and their measurement scope. Use:

```text
estimated decoder % = instructions / PCM seconds / 160,000,000 * 100 * factor
```

These factors reproduce the measured fixture/build combination. They are useful
references for nearby experiments, not universal factors for each AAC profile.
The old AAC-LC 320 kbit/s factor 2.01819 is retained for its historical workload.
Applied to this image's instruction counts, it underestimates LC by 7.50%,
overestimates HE by 12.05%, and overestimates v2 by 3.21%. Thus one AAC factor
does not reliably cover LC, SBR and parametric stereo or different link layouts.

The earlier [QEMU cache model](ESP32C3_CACHE_QEMU_20260930.md) used another ELF
layout and measurement wrapper. Its LRU/FIFO miss counts must not be substituted
for these physical counters. No cache penalty was injected into QEMU, and its
built-in cache counters remain zero. A general correction using modelled misses
still needs a same-layout trace/model comparison and validation of instruction
fetch costs. ESP32-C3 read-only flash-cache eviction has no dirty writeback;
other ESP32 targets with writable PSRAM need separate measurements/models.

## Measurement and reproducibility

- The actual production `native_aac_decoder_process` and Espressif codec archive
  execute in both runtimes. Runtime codec version: `v2.6.0-4-gfd141ab` (package
  2.6.2), ESP-IDF 6.0.2, GCC 15.2.0, `-O3` for the main component.
- Hardware uses the C3 machine performance counter with `PCER=1` (CPU cycles).
  QEMU uses `minstret` with `-icount shift=0,align=off,sleep=off`. A 1,024-NOP
  check returns exactly 1,025 instructions. Emulator elapsed time is not used.
- Timing/cache wrappers are `IRAM_ATTR` **and `noinline`**. ELF symbol addresses
  were checked in IRAM. ROM disable/enable invalidates cache tags while executing
  only from RAM/ROM; the flush itself is outside the timed interval.
- Compressed input (2,048 bytes), PCM (16,384 bytes), decoder state and stack
  live in internal RAM. Copying the embedded fixture is outside timing.
- Firmware asserts output format, samples, frames, progress and heap integrity.
  The analyzer checks every window, duplicate/missing records, the NOP probe,
  cache probes, stack margin and agreement between cycle and microsecond timers.
- A private full-flash backup was retained locally. Only the active application
  slot was written for the cache test. NVS and SPIFFS digests matched the backup
  after both runs. No credentials or backup contents are included in results.

Evidence: [raw runs, summary and provenance](../tests/results/esp32c3-cache-hardware-20260930/).
Build/run commands: [hardware benchmark instructions](../tools/codec_benchmark/cache/HARDWARE.md).

Hardware references: [ESP32-C3 technical reference manual](https://documentation.espressif.com/esp32-c3_technical_reference_manual_en.pdf)
and the ESP-IDF 6.0.2 `esp32c3/rom/cache.h` / `soc/extmem_reg.h` headers used by
this build. Cache geometry follows the
[ESP32-C3 datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.html).
