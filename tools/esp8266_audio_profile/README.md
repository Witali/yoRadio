# ESP8266 audio profile tools

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
