# ESP8266 audio-level LED

GPIO2 / D4 drives the active-low blue LED on the ESP-12F module. GPIO3 / RX
is our I2S-PDM data output; GPIO1 / TX carries the UART0 console. GPIO2 can
alternatively be UART1 TX or I2S WS, but our NoDAC driver routes only GPIO3.
External-DAC I2S needs WS and therefore excludes the LED at build time.

## Configuration

- `CONFIG_YORADIO_STATUS_LED=y`: enabled by default for SPI-PDM, I2S-PDM and
  I2S-RCPDM. Set `n` to remove the LED implementation and PCM taps entirely.
- `CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=10`: default 100-ms envelope refresh;
  `20` selects 50 ms. This is not the frequency of electrical brightness pulses.
- `CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS=32`: cap brightness (0..255).
  The test ESP-12F had reproducible stream stalls at 255; use the tested
  lower default. Full scale is experimental until the coupling is understood.
- `CONFIG_YORADIO_STATUS_LED_DECAY_STEP=8`: release by 8 levels per 50 ms;
  doubled at 10 Hz. Attack is immediate at the next refresh, like C3.

The production build script also accepts `-LedUpdateHz 20` (default 10) and
`-NoAudioLevelLed`. Use a fresh `-Variant` when changing cached SDK settings.

The tap is integrated into the existing post-normalization volume/balance
loop. Once per refresh it measures every fourth of the first 128 frames of
one PCM block: at most 32 peak comparisons. It uses the scaled values already
in CPU registers and the L/R average for stereo, retaining only a 16-bit peak.
There is no second pass over PCM. It handles -32768 safely,
does not change PCM, and stores no PCM buffer. Silent windows decay to dark;
explicit output silence requests clear the envelope at the next refresh.
This replaces the old Wi-Fi-connected/500-ms-blink indicator.

The existing app loop updates registers; the audio task checks one volatile
flag per PCM block. Only when requested does it collect and
publish the peak inside a short critical section. At the default 10 Hz this
is at most 320 peak comparisons/second (640 at 20 Hz), versus up to 1280 in
the initial LED version. All audio samples are still played. No clock
query, critical section or register update is done on skipped PCM blocks.
This is a cosmetic indicator: transients between snapshots can be missed,
and it must not be used as a sample-accurate VU/clipping meter. No new task,
timer, ISR, allocation or native-state snapshot is required. App sleep is
bounded by the next LED update, but higher-priority work and synchronous
services can delay a refresh: this is not a hard realtime refresh guarantee.
Unity (255) maximum brightness needs no multiply/divide; other caps use an exact
shift/add replacement for rounded division by 255 (all 65536 input pairs tested).
No extra persistent state was added by the integrated gain-loop implementation.

## Hardware modulation

ESP8266's SDK PWM is interrupt-driven. Instead this implementation reserves
the single GPIO sigma-delta generator, selects it as GPIO2's source and uses
the SDK register definitions. It does not change I2S, SLC-DMA, UART or their
interrupts. No other component may use this global sigma-delta generator.

The raw target is a high-level density out of 256, inverted for this LED.
Prescaler 255 is the largest hardware divider, giving the minimum 312.5-kHz
bit clock from 80 MHz; pulse repetition varies
with density (minimum about 1.22 kHz), rather than classic constant-period
PWM. Exact off/full brightness bypass modulation and use normal GPIO levels.
Software does not service individual pulses.

References: [Espressif TRM, GPIO/I2S/UART and register appendix](https://www.espressif.com/sites/default/files/documentation/esp8266-technical_reference_en.pdf),
[SDK PWM interrupt implementation](https://docs.espressif.com/projects/esp8266-rtos-sdk/en/latest/api-guides/pwm-and-sniffer-coexists.html),
[NodeMCU sigma-delta target/timing documentation](https://nodemcu.readthedocs.io/en/release/modules/sigma-delta/).
The raw unsigned target convention follows the working NodeMCU interface and
[its register driver](https://github.com/nodemcu/nodemcu-firmware/blob/release/app/driver/sigma_delta.c);
the TRM's description calls the target byte signed.

## Verification

`node --test tests/esp8266-status-led.test.js` compiles the real C module with
mock GPIO/ticks at 10/20 Hz and both LED polarities. Cases cover all brightness
levels, bounded snapshots, skipped blocks, release, exact endpoints, stereo cancellation,
INT16_MIN, stop/restart, initialization failure, tick wrap, preserved other
GPIOs and unchanged input PCM. It does not emulate the electrical peripheral.

`node --test tests/esp8266-output-channel-dispatch.test.js` checks real output
code with LED hooks enabled/disabled across PDM, RCPDM, feedback and simple
variants. PCM, output bits, resampler state and DMA boundaries must match
the existing reference. Physical brightness, RF coupling and CPU cost must
still be checked on the board; host correctness tests cannot establish them.

### Build measurements, 2026-09-09

Production image `firmware/development/esp8266-audio-level-led/app.bin`, source
`a98116e`, compared with the previous logging-enabled image (`4005e04`):

| Section | Previous | LED enabled | Difference |
| --- | ---: | ---: | ---: |
| DRAM data | 1656 | 1656 | 0 |
| DRAM BSS | 20368 | 20384 | +16 |
| IRAM text + BSS + vectors | 27484 | 27484 | 0 |
| Flash text | 533650 | 534566 | +916 |
| Flash rodata | 204492 | 204520 | +28 |
| Application binary | 763328 | 764272 | +944 |

LX106 GCC disassembly confirms the usual PCM-block fast path contains only
a flag load/barrier/test/branch, with no LED function call when capture is not
requested. Pulse generation has no software handler. The LED object's state
symbols total 11 bytes; linker alignment makes the DRAM delta 16 bytes.
No board CPU percentage is claimed from these build/host results.

The first full host run passed 256/257 cases and caught missing LED defaults
in the explicit stereo profile. Those defaults were synchronized without
changing codec/output algorithms; the seven profile/memory tests then passed.
The final full run passed **257/257**, with no skips, in 113.16 seconds:

```powershell
$taskTests = @(rg --files tests -g 'esp8266*.test.js')
node --test @taskTests
```

The four modulator variants each compared 1620 blocks / 351246 output words
with the reference, both with LED hooks disabled and enabled.

### OTA deployment, 2026-09-09

The user subsequently requested installation. Application-only OTA returned
HTTP 200/OK; the board booted into slot `0x110000`, rejoined client Wi-Fi and
served HTML/status plus WebSocket state messages. Playback was already stopped
and was left stopped for the user's listening/LED test. See the
[deployment record](../firmware/development/esp8266-audio-level-led/manifest.md).
No LED brightness observation or audio CPU measurement is claimed.

### Background scheduling correction, 2026-09-09

The initial LED integration shortened the whole app loop from 250 to 50 ms.
Consequently it could queue HTTP server work five times as often, even with
no WebSocket clients. The hardware LED pulse generator itself has no ISR;
this extra background scheduling is a separate software regression.

The corrected loop keeps periodic services at 250 ms independently of the
10/20-Hz LED timer. Real state/input notifications still wake those services
immediately. No extra task, heap buffer or software pulse timer was added.
`tests/esp8266-app-poll.test.js` executes the actual C loop with virtual time:
LED disabled/10/20 Hz, immediate state events, BOOT debounce, tick wrap and
a service taking longer than its period. All 18 targeted scheduling, LED,
state-notification and I2S tests passed. Live audio/RAM verification remains
separate: this correction alone does not establish the cause of decoder OOM.

Full on-board A/B results, the 32/255 brightness limit, firmware hashes and
remaining underrun/HTTP failures are recorded in
[the regression report](ESP8266_LED_REGRESSION_2026-09-09.md).
