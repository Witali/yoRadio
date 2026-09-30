# ESP32-C3 AAC instruction demand — 2026-09-30

## Result

The actual Espressif AAC Plus RISC-V decoder was profiled in the ESP32-C3 QEMU
emulator. **Physical CPU utilization was not measured.** The board was neither
flashed nor reset; the user requested emulator testing.

QEMU counts instructions but does not model their hardware execution time:
[QEMU TCG instruction-counting documentation](https://www.qemu.org/docs/master/devel/tcg-icount.html).
Therefore the percentages below are explicitly conditional calculations, not
claims about real-time headroom on the board.

| Fixture | Input bitrate | Million instructions per second of audio | Hypothetical decoder load at 160 MHz, 1 cycle/instruction |
|---|---:|---:|---:|
| AAC-LC 22.05 kHz mono | 128 kbit/s | 3.27 | 2.04% |
| AAC-LC 44.1 kHz stereo | 128 kbit/s | 11.14 | 6.96% |
| AAC-LC 48 kHz stereo | 128 kbit/s | 12.06 | 7.54% |
| HE-AAC 44.1 kHz stereo | 64 kbit/s | 27.83 | 17.39% |
| HE-AAC 48 kHz stereo | 64 kbit/s | 30.63 | 19.15% |
| HE-AAC v2 44.1 kHz stereo | 32 kbit/s | 36.52 | 22.83% |

On these fixtures, full HE-AAC uses about **2.5 times** the instruction demand
of LC stereo at the same output rate; HE-AAC v2 uses about **3.3 times** the LC
44.1 kHz stereo demand. The encodings have different bitrates: these ratios
compare these particular inputs, rather than isolate the SBR/PS algorithms alone.

The hypothetical percentage scales with average cycles per instruction. For
example, HE-AAC v2 would take 45.7% of a 160 MHz core at two cycles/instruction,
or 68.5% at three, before other tasks. **The actual value is not established by
this test.** No 22 kHz cap was introduced on the basis of emulator timing.

Decoder plus ADTS buffering allocated 61,412 bytes for LC and 117,932 bytes for
HE/HEv2, excluding the shared 16 KiB PCM test buffer. These are emulator heap
deltas for the isolated decoder, not total firmware memory consumption.

## Method and reproducibility

- ESP-IDF v6.0.2; Espressif audio codec 2.6.2, library commit
  `67b8d0e98f58c774b8652480893037273190e8dc`.
- Production decoder/ADTS implementation from `7b5d257c`, unchanged by the profiler.
  Profiling code is compiled only into the optional QEMU AAC test.
- QEMU 9.2.2 (yoRadio ESP32-C3 QEMU), fixed instruction counting:
  `-icount shift=0,align=off,sleep=off`. `minstret` is read around each production
  `native_aac_decoder_process()` call. Counter reads and incidental RTOS interrupts
  are included; deliberate sleeps, UI, output, logging and metadata queries are not.
- A 1,024-NOP probe must return exactly 1,025 instructions, including the counter
  read. Without that calibration, the firmware and summary cannot report success.
- Three independent decoder instances per fixture; each receives one complete
  warm-up and eight measured repeats of the original half-second synthetic tone.
  Every decoded frame is checked for the expected rate, channels and bit depth.
  All three runs produced identical counts for every fixture (0% observed spread).
- Instruction demand = instructions × PCM sample rate / PCM samples per channel.
  Encoder delay is included in the actual decoded sample count, rather than
  assuming each encoded file contains exactly 0.5 seconds of PCM.
- Hypothetical percentage = instruction demand / 160,000,000 × 100.

The recorded [raw log](../tests/results/esp32c3-aac-qemu-20260930/qemu.log),
[machine-readable results](../tests/results/esp32c3-aac-qemu-20260930/summary.json)
and [provenance hashes](../tests/results/esp32c3-aac-qemu-20260930/provenance.json)
allow the calculation to be checked independently.
Text hashes use UTF-8 with LF line endings; executable/image hashes use raw bytes.
See [build/run instructions](../idf/esp32c3-oled-native/QEMU.md#aac-instruction-demand-profile).

Validation also passes the normal AAC format/OLED/PCM QEMU checks. Six summary
tests verify the calculation and reject missing calibration, incomplete logs,
wrong PCM sample counts, duplicate measurements and firmware panics.

## What still requires the board

The real CPU has instruction latencies, flash/cache stalls and interrupts that
this emulator does not model. Wi-Fi/TCP/TLS, production PDM output and the full
radio task pipeline are absent from this isolated profile. Synthetic tones also
do not establish worst-case complexity for live music streams.

When the board is available, use `sdkconfig.cpu-profile.defaults` with the normal
hardware build and collect `PERF CPU` plus `PERF` decoder lines while playing
the same fixtures over HTTP/HTTPS. Check idle margin and output underruns with
WebUI/OLED active. The existing profiler reports busy/idle and stream, decode,
output, Wi-Fi, TCP/IP and web task shares. Until then, total CPU load and stable
full HE-AAC playback on physical hardware remain unverified.
