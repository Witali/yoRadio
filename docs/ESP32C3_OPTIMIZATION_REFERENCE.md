# ESP32-C3 reference for code optimization

Use this reference when optimizing the native C3 audio firmware. Preserve the
codec output and measure the complete radio after testing individual functions.
A smaller binary or a faster host benchmark does not establish faster playback.

Checked on 2026-10-08 against ESP-IDF 6.1 revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`. Board observations and build settings
below describe specific measurements; recheck them after changing hardware,
SDK, compiler or configuration. Start with the [testing guide](ESP32C3_TESTING.md)
for acceptance criteria.

## Processor and memory

| Property | ESP32-C3 |
| --- | --- |
| CPU | One 32-bit RISC-V core, RV32IMC, up to 160 MHz |
| Integer arithmetic | Hardware 32-bit multiplication and division |
| Floating point | No hardware FPU; floating-point operations require software |
| Internal storage | 384 KiB ROM; 400 KiB SRAM including 16 KiB cache; 8 KiB RTC SRAM |
| Cryptography | Hardware AES-128/256, SHA and RSA accelerators |

Source: [ESP32-C3 datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.html),
CPU, memory and cryptography sections. Accelerator availability alone does not
prove that a particular TLS operation uses it; inspect the selected backend.

The CPU has a four-stage pipeline. The TRM describes zero additional wait states
for internal SRAM/cache access, but this is not a one-cycle guarantee for every
instruction. No complete instruction-latency table was identified in the
[TRM v1.4 CPU chapter](https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf#page=31).
Measure dependency chains, branches and memory access in the actual program.

### Implications for this project

- The measured build targets `rv32imc`, without Zbb. Its Rice reader's
  `__builtin_clz` calls ROM `__clzsi2`; a C builtin is not proof of a hardware
  instruction. Inspect final linked disassembly, including helper calls and
  spills. See the [physical Rice audit](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md).
- Keep required wide intermediates in LPC and fixed-point AAC calculations.
  Removing a 64-bit operation requires a proved input bound and exact-output
  tests; fewer multiplications alone do not demonstrate an improvement.
- Guard zero before `__builtin_clz`, and check shift widths, signed overflow,
  alignment and aliasing when changing packed representations.
- Treat SRAM as a shared budget. Track `.iram0.text`, `.dram0.data`,
  `.dram0.bss`, stack margins, peak live allocations, total free heap and largest
  free block separately. A `const` declaration is not a placement audit: check
  the ELF/map and references from code that can run with cache unavailable.
- Before reusing codec storage, enumerate every reader/writer and pointer
  lifetime, including delayed output, reset, error and retry paths. Replace
  unexplained offsets with named fields/constants and layout assertions.

## Hardware cycle measurements

In the pinned SDK, `esp_cpu_get_cycle_count()` in
`components/esp_hw_support/include/esp_cpu.h` calls `rv_utils_get_cycle_count()`.
For C3, `SOC_CPU_HAS_CSR_PC=1`; the machine-mode path reads the custom performance
counter, rather than the generic RISC-V `cycle` CSR. Definitions are in
[`riscv/rv_utils.h`](https://github.com/espressif/esp-idf/blob/9a97f6c54ec638111ce55cd36581b3c192f15207/components/riscv/include/riscv/rv_utils.h).

| Register | SDK name | Check for cycle timing |
| --- | --- | --- |
| `mpcer`, `0x7e0` | `CSR_PCER_MACHINE` | Only event bit 0 selected |
| `mpcmr`, `0x7e1` | `CSR_PCMR_MACHINE` | Enable bit 0 set; saturation bit 1 clear |
| `mpccr`, `0x7e2` | `CSR_PCCR_MACHINE` | 32-bit count |

The counter stops in WFI. Selecting multiple events produces one combined
count, not separate counters. Source:
[TRM registers 1.12–1.14](https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf#page=39).
Use named SDK definitions for register access. Do not repurpose/reset this
counter in the running radio without checking other timing consumers.

For an enabled, wrapping cycle counter, unsigned subtraction handles rollover:

```cpp
#include "esp_cpu.h"

// Validate the event/mode registers and CPU frequency before this region.
const uint32_t start = esp_cpu_get_cycle_count();
const uint32_t checksum = run_runtime_input_batch();
const uint32_t elapsed = esp_cpu_get_cycle_count() - start;
// Consume/check checksum and report elapsed after the timed region.
```

At a fixed 160 MHz, one cycle is 6.25 ns and a full 32-bit wrap takes about
26.84 seconds (`2^32 / 160000000`). Keep a batch well below that interval.
Verify nonzero elapsed counts; keep logging, allocation and input preparation
outside the measured region. Prevent constant folding and dead-code removal,
then confirm the compiled loop. Report an empty/identity batch alongside the
candidate instead of assuming its overhead subtracts perfectly.

With interrupts enabled, an interval can include other tasks and ISRs. Preserve
raw repetitions, minimum and median, rotate candidate order, and record cache
state and CPU frequency. Disabling interrupts for long loops changes the radio
workload. Distinguish elapsed decoder time, task CPU utilization, instruction
counts and physical cycles in every report.

Historical board measurements already use cycle timing in the
[cache/AAC experiment](ESP32C3_CACHE_HARDWARE_20260930.md). The subsequent full-radio
[Rice comparison](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md) instead reports elapsed
decoder time and task CPU; these are different measurements.

## Key guidance from ESP-IDF 6.1

Summary of Espressif's
[ESP32-C3 speed optimization guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-guides/performance/speed.html):

- Profile frequent or latency-critical paths first. Repeat measurements;
  microsecond timers measure elapsed time, cycle counters suit short routines,
  and task statistics or tracing reveal scheduling costs.
- Flash layout/cache misses can distort sub-millisecond benchmarks. Compare
  repeated runs and selective IRAM placement, accounting for lost DRAM.
- Consider performance optimization (`-O2`) and supported Quad flash. Check
  hardware compatibility and correctness after compiler changes.
- Avoid software floating point in hot paths. Reduce logging and formatting;
  full output buffers can block execution.
- Test jump tables for hot switches outside IRAM. An IRAM-safe ISR needs
  cache-independent callees and data, not just an entry annotation.
- High-priority tasks must block or yield. Network tasks should remain below
  TCP/IP priority. Keep interrupts short.
- Network and I/O throughput tuning often consumes more RAM. Evaluate each
  setting instead of copying the throughput example wholesale.
- Keep assertions. Evaluate stack-guard, boot-validation and clock-calibration
  tradeoffs separately from ordinary speed tuning.

### Applying the guidance to YoRadio

The following decisions combine that guidance with our measured configuration:

- **Single core:** the guide's Core 1 placement examples do not apply to C3.
  The Rice comparison used output/decode/stream priorities **8/7/5** and a
  **1 ms** tick. Priority is not a time quantum; changing the tick also changes
  delay granularity. Keep DMA service, input waits and decoder cost separate.
- **Flash mode:** our tested board has revision 0.4 C3, 4 MiB XMC flash and no
  PSRAM. The matched Rice builds configure **DIO 80 MHz**, CPU **160 MHz**.
  The installed `compact-icy-quiet` application was also identified through
  WebUI on 2026-10-08 (ELF SHA starts `da2f5dfeac6a`); its saved
  [configuration](../firmware/development/esp32c3-idf-6.1-compact-icy-quiet/sdkconfig)
  selects DIO 80 MHz, with QIO/QOUT disabled. This identity check did not read
  the live SPI controller registers.
  [Standalone QIO 40/80 MHz tests](ESP32C3_FLASH_QUAD_20260930.md) worked, but
  [full-radio QIO acceptance](ESP32C3_QIO80_ACCEPTANCE_20260930.md) failed.
  Application OTA leaves the bootloader intact; verify runtime controller mode
  before attributing a timing change to Quad operation.
- **Compiler and checks:** the measured configuration selects performance
  optimization and retains assertions and the hardware stack guard. Component
  flags can override global settings; use `compile_commands.json` and the final
  ELF. Do not remove checks to conceal an experiment's failure.
- **Memory placement:** the [native board profile](../idf/esp32c3-oled-native/README.md)
  already trades Wi-Fi IRAM placement for AAC heap capacity. Moving more hot
  code into IRAM requires measuring the remaining contiguous allocation budget.
- **Flash writes and OTA:** assess the exact chip, Auto Suspend configuration,
  driver path and ISR placement. A successful playback benchmark does not
  establish that OTA remains safe; retain the separate OTA/recovery tests.
- **Logging and I/O:** this board uses native USB Serial/JTAG. A UART baud-rate
  change is not its console-throughput setting. FatFs buffering advice is not
  automatically an optimization for the HTTP/TLS audio reader.

The exact Rice baseline settings are retained in its
[sdkconfig](../firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-control/sdkconfig).
These laboratory settings are not a declaration that every overlay is a
production default.

## Evidence to consult before another experiment

| Question | Existing evidence and interpretation |
| --- | --- |
| Does bytewise Rice help? | [Host study](ESP32C3_FLAC_HOTLOOPS_20261008.md) improved, but [C3 screening](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md) showed +2.68% to +10.10% elapsed decoder cost across three FLAC cases. It remains default-off. |
| Can QEMU predict hardware speed? | [Calibration](ESP32C3_QEMU_CALIBRATION_20260930.md) is decoder/build/workload-specific. The historical FLAC factor covers the Espressif backend, not the current custom decoder. |
| What does a cache simulation prove? | [QEMU traces](ESP32C3_CACHE_QEMU_20260930.md) model misses; [physical measurements](ESP32C3_CACHE_HARDWARE_20260930.md) measure timing. Do not add a second cache penalty to a factor that already includes it. |
| Where can RAM be recovered? | Read the [IRAM investigation](ESP32C3_IRAM_REDUCTION_20261001.md), [Flash constant candidates](ESP32C3_FLASH_CONSTANT_CANDIDATES_20260930.md) and [memory stability plan](ESP32C3_MEMORY_STABILITY_TODO.md). Candidate lists are not permission to skip lifetime checks. |

## Validation checklist for optimization agents

1. Save the baseline commit, SDK/toolchain, flags, fixtures and hashes. Change
   one mechanism at a time; use the same workload for both variants.
2. Test arithmetic boundaries, malformed/truncated input, allocation failures,
   retry and reset. FLAC must preserve exact PCM. Compact AAC must retain full
   SBR/PS, output rates/channels and the agreed maximum three-LSB deviation.
3. Inspect final code and section placement. Record code size, static RAM,
   allocator requests, peak live RAM and stack margins independently.
4. Measure hot loops on physical C3, then complete decoder calls and full-radio
   playback with networking, output and WebUI active. Host or QEMU results
   support an experiment; they do not qualify its target timing.
5. CPU utilization is informational. Retain runtime, watchdog, allocation,
   progress, heap and DMA findings. DMA diagnostic counters alone do not certify
   gap-free sound; identify whether output was actually captured.
6. Preserve failed/incomplete runs and the previous firmware/settings. Save
   successful test images under `firmware/development/<variant>/app.bin` and
   archive reproducible evidence without credentials or private test keys.
