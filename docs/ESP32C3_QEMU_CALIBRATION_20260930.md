# ESP32-C3 QEMU codec calibration — 2026-09-30

## Saved factors

The original physical-board test files were replayed through the Espressif RISC-V
decoders in QEMU. **Use a separate correction factor for each decoder.** A universal
factor is not supported by these results.

| Espressif decoder / fixture | Saved factor | Observed window factors |
|---|---:|---:|
| AAC-LC, 48 kHz stereo, 320 kbit/s | **2.0182 ≈ 2.02** | 1.7709–2.0208 across two builds |
| MP3, 48 kHz stereo, 320 kbit/s | **1.7853 ≈ 1.79** | 1.7851–1.7855 |
| FLAC, 48 kHz stereo, level 8 | **1.4133 ≈ 1.41** | 1.4125–1.4142 |
| Vorbis, 48 kHz stereo, quality 10 | **1.5331 ≈ 1.53** | 1.5318–1.5344 |
| Opus, 48 kHz stereo, 510 kbit/s | **1.4801 ≈ 1.48** | 1.4785–1.4818 |

Machine-readable profiles for future benchmarks:

- [AAC factor and source windows](../tools/codec_benchmark/calibration/esp32c3-aac-160mhz.json).
- [Other codec factors and source windows](../tools/codec_benchmark/calibration/esp32c3-codecs-160mhz.json).

The AAC default uses the later hardware backend-comparison run (about 21.3%
decoder load). The earlier optimized run measured about 18.7%, giving a weighted
factor around 1.77. Both are retained, rather than averaging different builds.
The other four factors use the earlier optimized hardware run. Even within that
same build, factors range from about 1.41 to 1.79.

These are empirical **decoder-call elapsed-time factors** for a 160 MHz ESP32-C3,
not universal cycles per instruction, QEMU wall-clock multipliers or total CPU
utilization. The observed ranges are not confidence intervals or guaranteed bounds.
FLAC here means the **Espressif** backend; the current custom FLAC decoder and
Helix/minimp3 need their own calibration.

## How to apply

```text
instruction demand = counted instructions / decoded audio seconds
estimated decoder % = instruction demand / 160,000,000 × 100 × codec factor
```

For example, the current HE-AAC 48 kHz fixture's 19.15% hypothetical one-cycle
value becomes approximately **38.6%** with the AAC factor. HE-AAC v2 44.1 kHz
becomes approximately **46.1%**. Both are **unvalidated extrapolations from LC**:
SBR and PS execute different code. These are not measured hardware results or
proof of stable playback. Wi-Fi, TCP/TLS, PDM output, UI and other work must be
measured separately before claiming whole-radio CPU headroom.

The [six AAC estimates](../tests/results/esp32c3-aac-calibration-20260930/estimated-aac.json)
retain the raw instruction counts, assumed one-cycle percentages, applied profile
hash, observed-factor range and extrapolation labels. No 22 kHz cap was introduced.

Apply the saved AAC profile to a future compatible instruction-profile log:

```powershell
python tools/codec_benchmark/summarize_qemu_aac.py `
  idf/esp32c3-oled-native/build-qemu-aac/qemu-smoke.log `
  --calibration tools/codec_benchmark/calibration/esp32c3-aac-160mhz.json `
  --output .build/estimated-aac.json
```

The summary rejects a missing/different runtime decoder version, target or CPU
clock. Recalibrate when the library, memory placement, firmware build, workload or
instruction mix changes. Keeping the version constant alone does not guarantee
the factor transfers to a different workload.

## Method and evidence

- Recovered original 11-second generated noise/tone files, not the half-second
  AAC fixtures used for stream-format regression. [Fixture manifest](../tests/fixtures/esp32c3_calibration/manifest.json).
- ESP-IDF v6.0.2, package `esp_audio_codec` 2.6.2. The linked library reports
  runtime build **`v2.6.0-4-gfd141ab`**; both identifiers are retained because they
  differ. [Build and archive hashes](../tests/results/esp32c3-aac-calibration-20260930/provenance.json).
- QEMU 9.2.2, `-icount shift=0,align=off,sleep=off`; the 1,024-NOP probe returns
  exactly 1,025 instructions including the counter read.
- Historical streaming SDK path: default codec configuration, AAC Plus off,
  2,048-byte input chunks copied to RAM, initial 12,288-byte PCM buffer with the
  same grow-on-demand behavior. Count only `esp_audio_simple_dec_process()`.
- Two windows per fixture, approximately five seconds of PCM each. Every window
  matches the physical log's **calls, input bytes and PCM bytes exactly**. Every
  output frame is checked for 48 kHz, stereo, 16-bit PCM.
- Three independent decoder instances. Counts are identical except FLAC's first
  window, where run 1 differs by 27 instructions out of approximately 79 million
  (0.0000342%). The analysis retains the spread and uses its median; it rejects
  spread above 0.1% for investigation. This threshold is a test policy, not an
  accuracy claim about physical timings.
- Hardware timing uses `esp_timer_get_time()` around decoder calls. Printed
  milliseconds and percentage tenths were floored. Fits use decode milliseconds
  and exact PCM counts; precision is limited by the retained logs. Timers,
  preemption and incidental interrupts contribute to the effective factor.
- `factor = sum(hardware decode ms) × 160,000 / sum(QEMU instructions)`.
  Window-specific factors are saved too. Predictions on those same windows are
  a fit, not independent validation on held-out hardware tests.
- The current AAC adapter is also checked against the same PCM windows. Its
  instruction demand is approximately 0.6–0.7% below the historical SDK path.
  This establishes comparable work on LC, not measured new-board performance.

Original hardware logs lack fixture and codec archive hashes; the original code
also included local changes. Matching recovered lengths and exact decode windows
provides useful evidence, but does not make the historical build fully reproducible.
All raw hardware/QEMU logs are retained in
[`tests/results/esp32c3-aac-calibration-20260930/`](../tests/results/esp32c3-aac-calibration-20260930/).
The board was not reset or flashed for this work.

### Test harness correction

An initial FLAC run completed its decoder windows but later failed with a corrupted
semaphore in the smoke task. The original 4 KiB smoke-task stack was too small for
the expanded codec tests: the successful FLAC run uses about 5.6 KiB and Opus about
12.2 KiB. The optional profile now gets the production decoder stack plus 4 KiB
for its parent harness (20 KiB total), with 8,016 bytes still free after Opus.
Heap integrity checks pass after decoding and freeing each instance. Hardware
builds are unchanged. The failed run was rejected and retained as
[`rejected-flac-small-stack.log`](../tests/results/esp32c3-aac-calibration-20260930/rejected-flac-small-stack.log).

## Repeat the saved test suite

Prepare the QEMU AAC build as described in
[QEMU.md](../idf/esp32c3-oled-native/QEMU.md#aac-instruction-demand-profile), enabling
`CONFIG_YORADIO_QEMU_AAC_TEST=y` and `CONFIG_YORADIO_QEMU_AAC_PROFILE=y`.
Then, from the repository root:

```powershell
.\tools\codec_benchmark\run-qemu-calibration.ps1 `
  -DependencyRoot C:\Work\yoRadio\.idf `
  -QemuExecutable C:\path\to\qemu-system-riscv32.exe `
  -QemuBiosDirectory C:\path\to\qemu\share\qemu
```

The wrapper runs MP3, FLAC, Vorbis, Opus and the AAC-only profile, verifies pass
markers, saves all logs and recalculates profiles/estimates under
`.build/qemu-codec-calibration/`. It does not overwrite the committed reference
profiles. Use `-OutputDirectory` for another results folder. Original physical
logs stay fixed; re-running this suite does not create new physical measurements.

Run the analysis regression tests independently:

```powershell
python tests/test-qemu-codec-calibration.py
python tests/test-qemu-aac-profile-summary.py
node --test tests/esp32c3-qemu-profile.test.js tests/codec-benchmark.test.js
```

The tests reject altered fixtures, mismatched physical/QEMU windows, duplicate or
incomplete runs, wrong decoder versions and cross-codec mixups. They also verify
the units and preserve the distinction between estimates and measured CPU load.
