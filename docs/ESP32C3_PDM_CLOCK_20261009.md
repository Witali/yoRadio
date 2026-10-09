# ESP32 C3 PDM clock accuracy experiment

The normal PDM driver replaces its calculated fractional clock divider with
an integer divider to reduce background noise. For this board's fixed-rate
DAC configuration, that predicts 48,076.923 PCM frames/s rather than the
requested 48,000. The optional fractional mode keeps the calculated divider.
In the paired ten-minute HE-AACv2 test, delayed DMA queue-service events fell
from 102 to 20. The option remains disabled by default pending further
continuity testing and analog noise qualification.

## Previous ESP IDF versions

The same integer override and DAC defaults are present in all five inspected
local SDK checkouts:

| SDK | Integer override | DAC BCLK divider | DAC FP and FS at 48 kHz |
| --- | --- | ---: | --- |
| 5.5.4 | Present | 13 | 960 / 480 |
| 6.0.2 | Present | 13 | 960 / 480 |
| 6.0.3 | Present | 13 | 960 / 480 |
| 6.1 release | Present | 13 | 960 / 480 |
| 6.1 revision `9a97f6c54ec6` | Present | 13 | 960 / 480 |

The SDK source comment identifies noise reduction as the reason for the
override. Espressif's [5.4.2 source](https://github.com/espressif/esp-idf/blob/v5.4.2/components/esp_driver_i2s/i2s_pdm.c#L68-L72)
also contains it. Therefore this behavior predates the 6.1 upgrade.
The comparison verifies source code against each checkout's Git revision;
older versions were not reflashed for this experiment. The calculated rate
assumes the same application settings and nominal 160 MHz clock source.

## Divider and implementation

At FP/FS 960/480 the converter uses 128 PDM clocks per PCM frame. With BCLK
division 13, the two settings are:

| Clock mode | MCLK divider | Nominal PCM rate | Error |
| --- | --- | ---: | ---: |
| SDK noise workaround | 2 | 48,076.923077 Hz | +1,602.564 ppm |
| Fractional experiment | 2 + 1/312 | 48,000 Hz | 0 ppm |

These are ratios relative to the nominal clock source, not external frequency
measurements. Absolute accuracy still follows the board's reference crystal.
The [C3 technical reference manual](https://documentation.espressif.com/esp32-c3_technical_reference_manual_en.pdf)
describes the divider fields in section 29.6 and register 29.18.

The error is small for playback tempo, but consumes an extra 96.15 ms of
audio per minute, or 0.96154 seconds over ten minutes. Under exactly real-time
delivery this draws down finite buffering. Wi-Fi jitter, server burst sizes,
initial prebuffering and scheduling can cause separate interruptions. A
divider correction alone does not explain decoder faults or memory failures.

All codecs use this common output clock. The preceding [QIO comparison](ESP32C3_QIO80_RECHECK_20261008.md)
passed its 44 finite HTTP/HTTPS format and EOF cases, and heavy FLAC passed
its 60-second load with no DMA queue overruns. FLAC's observed DMA-written
audio/wall ratio was 1.00162, consistent with the predicted clock error.
Short and overfed tests can pass despite drift; they do not establish
ten-minute continuity with delivery constrained to exactly real time.

`CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y` enables the experiment. It supports
only the audited ESP32-C3 configuration: PCM input at 48 kHz, PLL 160 MHz,
BCLK divider 13, FP 960 and FS 480. An unsupported configuration fails setup.
`CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS=y` independently reports actual divider
and converter register fields during setup, under the existing lock, with
logging after unlocking. Both options default to disabled.

The build generates a private copy of `i2s_pdm.c`; it does not modify the
shared SDK installation. The generator checks the complete normalized source
hash and rejects an unknown driver. Fractional mode omits the integer
overwrite and keeps the HAL result. Clock-source management, critical
sections, start-time register update and RX code retain the SDK behavior.
The change runs at initialization and adds no per-sample work or heap
allocation. Existing public cached clock information alone cannot confirm
the effective integer setting.

To build an isolated candidate with production defaults, from the repository
worktree:

```powershell
./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-pdm-fractional `
  -Sdkconfig build-pdm-fractional/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.pdm-fractional-clock.defaults')
```

This command requires the pinned dependencies and a new build directory.
The saved laboratory comparison additionally enables profiling, clock
readback and its test trust root; it is not a production qualification.
Diagnostic images are saved under `firmware/development/esp32c3-idf-6.1-r9a97-pdm-integer/`
and `firmware/development/esp32c3-idf-6.1-r9a97-pdm-fractional/`.

## Physical comparison

The paired comparison uses fresh boots, the same HE-AACv2 44.1 kHz stereo
fixture over trusted HTTPS, ten minutes of playback per setting, real-time
server pacing (1.00x), continuous WebUI requests, and settled idle checks
before and after playback. Integer mode runs first, fractional second.
It is one sequential pair, not randomized repeated trials.

Build audits verify that the only active configuration differences from the
previous laboratory image are the two PDM options. Both images retain full
compact AAC/SBR/PS, dynamic TLS RX reservation, adaptive input buffers, QIO
at 80 MHz and the same output/decoder priorities. Linked AAC and HTTP length
guard audits pass. Four host tests cover divider math, damaged readback,
unchanged SDK code outside the explicit insertions, and rejection of an
unknown or already-patched SDK source.

The linked RAM sections match in size and address: IRAM text 47,690 B, DRAM
data 12,856 B and DRAM BSS 45,664 B. Integer and fractional application images
are 1,619,264 B and 1,619,328 B respectively. Their Flash code and constants
are not byte-identical, so small timing changes still have a binary-layout
confounder. Neither image allocates a new audio buffer for the clock option.

Setup readback confirms integer=2, X=1, Y=1, Z=0, YN1=0 in the control,
and integer=2, X=311, Y=0, Z=1, YN1=0 in the fractional candidate. Source=2,
BCLK divider=13, SINC OSR=2 and FP/FS=960/480 match in both. The saved app ELF
identities, actual QIO 80 MHz registers and four mapped-image CRC32 reads per
image agree with the corresponding binaries.

| Measurement | Integer control | Fractional candidate |
| --- | ---: | ---: |
| Original playback and heap gates | PASS | PASS |
| Selected diagnostic telemetry | Incomplete: two merged lines | Complete |
| DMA queue-overrun delta | 102, readable cumulative boundaries | 20 |
| DMA write errors at those boundaries | 0 | 0 |
| Total CPU busy, time-weighted | 61.444% | 62.083% |
| CPU-log free heap, first / last three-sample median | 25,996 / 25,832 B | 26,024 / 26,076 B |
| CPU-log minimum free heap | 25,432 B | 24,920 B |
| Minimum largest block | 14,848 B | 14,336 B |
| Settled idle free heap before / after | 133,108 / 132,926 B | 133,060 / 133,096 B |
| Settled idle largest block before / after | 102,400 / 102,400 B | 102,400 / 102,400 B |
| Median RSSI | -68 dBm | -66 dBm |

Both requested 600-second playback runs and their settled-heap checks pass
the original gates; no runtime fault is recorded. These gates do not require
zero DMA queue overruns. The control's two merged DMA/AAC lines remain in the
raw journal and fail the stricter telemetry-completeness check. Its delta of
102 is the difference between intact cumulative boundary samples spanning
585.859 seconds, not a repaired complete-capture verdict. The fractional
capture has no such damage and spans 585.969 seconds between DMA boundaries.
CPU rows are intact in both captures; no CPU-budget threshold is applied.

The lower event count supports clock drift as a contributing factor under
real-time delivery, but does not isolate its causal contribution: RSSI,
scheduling and binary layout differ, and this is one sequential pair. The
remaining 20 events occur in three diagnostic intervals ending within about
121 seconds of playback. No further increment is observed for the rest of
the selected fractional window. Investigate initial buffering and delivery
bursts before claiming gap-free output. The CPU difference of 0.639 percentage
points is not an isolated measurement of divider overhead.

After the experiment, app-only OTA restores `idf61-qio80-8c1f2d2d`, app SHA-256
`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
The expected production ELF identity and three playing AAC observations are
verified. Wi-Fi, playlist and settings comparisons pass. The board therefore
returns to the previous production clock mode.

## Noise and acceptance limits

The integer override is intentional. Nominal clock accuracy and DMA service
do not establish analog SNR or THD+N. Digital PDM capture through a validated
internal loopback could compare the digital sequence, but would omit GPIO
edge timing, supply noise, RC filtering and amplifier behavior. The current
experiment does not implement that capture.

Retain the production default until output noise is compared through the
existing audio path and, for quantitative results, an ADC or audio input
after the filter. Additional all-format playback, switching and EOF checks
are needed before production adoption. A zero DMA queue-overrun count alone
does not prove acoustic continuity; nonzero counts are delayed queue-service
events, not an exact count of audible gaps.

Exact nominal 48 kHz is the preferred target if the comparison finds no
significant sound-quality regression. Listening and analog measurements have
not been performed for these images, so the production default is unchanged.

See the [preceding pacing comparison](ESP32C3_HEAP_PACING_20261009.md) for
the independent effects of server overfeeding, receive-buffer filling and
clock drift. Keep its original failures and the 1.02x backpressure case.

## Saved evidence

The [evidence archive](../tests/results/esp32c3-pdm-clock-20261009/) contains
both original reports and journals, clock readback, configuration and linked
code audits, SDK version snapshots, source overlays, restoration checks and
a byte-exact SHA-256 index. Private settings snapshots and TLS private keys
are excluded. The unrelated inactive CLZ CMake block is captured only as
build provenance; the CLZ experiment was not compiled into either image.

Replay the saved comparison without contacting the board:

```powershell
python tests/results/esp32c3-pdm-clock-20261009/summarize.py --output .build/pdm-replay/summary.json
python tests/results/esp32c3-pdm-clock-20261009/verify_evidence.py --summary .build/pdm-replay/summary.json --output .build/pdm-replay/verified.json
python tests/test-pdm-clock.py
```

The first two commands write derived JSON outside the archive, preserving
the original verdicts and malformed rows. The archived physical controller describes the
procedure; a new physical run needs fresh output paths, a current trusted
test certificate and the correct board address and USB port.
