# ESP8266 audio profile tools

## AAC PCM block-size matrix

`run_aac_block_matrix.ps1` compares the retained full-frame bridge and
32/64/128/256/512-frame AAC output on the connected board, first decode-only
or with `-PhysicalOutput` through real I2S-PDM DMA. It writes app0 only and
leaves a diagnostic app installed; restore ordinary firmware afterwards.
The selected default is 512 frames / 1024 bytes mono PCM. See
[measurements and safety invariants](../../docs/ESP8266_AAC_PCM_BLOCKS.md).

## RAM decoder with physical DMA output

To remove network delivery from the timing comparison while exercising the
actual decoder, PCM processing, PDM packing and GPIO3 DMA, configure:

```text
-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=ON
-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=ON
-DYORADIO_ESP8266_AUDIO_PROFILE=OFF
-DYORADIO_ESP8266_AUDIO_TRACE=OFF
```

This copies retained MP3/AAC fixture frames into test-only static RAM, runs
eight warm-up and 200 measured frames, and does not start Wi-Fi/WebUI.
Volume 128, neutral balance and disabled normalization are applied in RAM
only; saved settings are not overwritten. Reported wall time includes output
backpressure: it is not decoder-only CPU cost. Restore ordinary firmware
after this isolated benchmark.

`YORADIO_ESP8266_DMA_COMMITTED_PREFIX=OFF` restores the original full-buffer
handoff and long neutral retry for an A/B control. Its default ON enables
both safe committed-prefix handoff and short underrun retries. Compare
duration and FIFO-empty flags, not just underrun counts: an active neutral
retry is now 64 words instead of 512 words.

See [physical results and limitations](../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).

## Live-radio DMA starvation diagnosis

Keep the production sdkconfig (including its flash frequency, decoder and
output mode), and enable only these CMake options:

    -DYORADIO_ESP8266_AUDIO_PROFILE=ON
    -DYORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS=30000

Leave the profile URL empty to select the ordinary saved station through
WebUI. Do not enable decode-only mode. Capture UART TX without sending UART
commands; GPIO3 remains the audio output. Restore the saved production app
after the experiment, flashing only the currently running application slot.

The report includes `pcm_gap`: time from the previous PCM output return to
the next PCM call. This overlaps decoding/network work; do not add it to
those stages as extra CPU load. All timings are wall time and include task
preemption. Runtime-counter CPU percentages are not reliable for the SDK's
direct ISR task-notification path (see `docs/ESP8266_AUDIO_PROFILE.md`).

DMA counters are sampled before reporting and rebased after reporting, so
UART logging itself is excluded from the counter window. Discard the first
window after connection when evaluating steady state. Long reporting periods
reduce, but cannot completely eliminate, profiler interference.

- `late_start`: existing warning that the next buffer is not ready at EOF.
  It does not prove audible silence if the producer catches up with DMA.
- `empty_start`: the next free buffer has not been claimed by the producer.
- `incomplete_eof`: the current producer buffer is still partial when DMA
  finishes transmitting it; stronger evidence of missed output deadlines.
- `incomplete_words`: sum of the unwritten tails at those EOFs, not an exact
  analog silence duration. These are software observations, not a GPIO trace.

The extra ISR counters exist only with the audio profile enabled. Production
buffer ownership, DMA operation, PDM conversion and decode behavior are unchanged.

These tools generate deterministic MP3/AAC fixtures, serve one fixture at its
encoded bitrate, capture five-second CPU/heap profile windows from a physical
ESP8266, and summarize the UART log.

Generate 48 kHz stereo fixtures:

    .	oolsesp8266_audio_profilegenerate_fixtures.ps1

Configure the native ESP8266 firmware with:

    -DYORADIO_ESP8266_AUDIO_PROFILE=ON
    -DYORADIO_ESP8266_AUDIO_PROFILE_URL=http://<PC-IP>:8765/stream.bin

Use `esp8266/rtos-sdk-native/sdkconfig.audio-profile-qio80.defaults` for the
reproducible 160 MHz/QIO80 profile with FreeRTOS runtime counters. The older
`sdkconfig.audio-profile.defaults` fragment only enables those counters and is
kept for custom configurations. To discard PCM after decode and bypass
normalization, PDM conversion, queueing, and physical output, also set:

    -DYORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY=ON

After flashing the app image, run one physical case:

    .	oolsesp8266_audio_profileun_case.ps1 -Fixture mp3-320.mp3 -BitrateKbps 320 -MimeType audio/mpeg -Port COM10 -PythonPath C:path	opython.exe

The case runner starts stream_server.py hidden, resets the board with RTS,
captures UART at 115200 baud, stops only its own server process, and writes the
log under .build/esp8266-audio-profile/results.

Summarize one or more logs:

    python .	oolsesp8266_audio_profilesummarize.py .buildesp8266-audio-profileesultsmp3-320-run.log

The summary uses the median of complete windows that include a CPU sample.
The first window is a runtime-counter baseline and is intentionally excluded.

## Generated-PCM physical-output profile

For a decoder- and network-independent physical-output measurement, configure the same
QIO80 sdkconfig with:

    -DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=ON

This profile never starts Wi-Fi and never creates an MP3/AAC decoder. It
generates a deterministic 48-kHz stereo block in static RAM, submits the same
128 frames/512 bytes to `native_audio_output_write()`, and reports write time,
SPI queue wait, whole-CPU busy/idle, and free/minimum heap after a two-second
warm-up and ten-second measurement. The saved Kconfig baseline is:

    esp8266/rtos-sdk-native/sdkconfig.audio-profile-qio80.defaults

I2S-PDM SLC DMA uses the ESP8266 fixed I2S pins: GPIO3/RX for DATA, GPIO15
for BCLK, and GPIO2 for WS. UART input is intentionally ignored, while UART
TX logging on GPIO1 remains available. GPIO2 cannot drive the onboard status
LED in this mode because reclaiming WS stops DMA audio. The onboard 470-ohm
resistor is only a current limiter; do not transmit from the host during audio
output.

Select `CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM` for the legacy GPIO13/D7
SPI-PDM comparison. The deprecated CMake option
`YORADIO_ESP8266_FIXED_I2S=ON` now selects standard PCM for an external I2S
DAC rather than the no-DAC PDM path. The benchmark must be followed by
restoring the normal application image.

## Gated 1 kHz physical-output test

Add both CMake options to the generated-PCM profile:

    -DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=ON
    -DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=ON

The resulting isolated firmware continuously produces identical left/right
full-scale 16-bit PCM at 48 kHz: an exact 48-sample 1 kHz sine for 500 ms,
then zero PCM for 500 ms. Normalization, Wi-Fi, WebUI, and codecs remain off.
The GPIO3 PDM bitstream must pass through the documented RC low-pass filter
before an amplifier input. Restore the normal application after the test.
