# ESP8266 audio profile tools

These tools generate deterministic MP3/AAC fixtures, serve one fixture at its
encoded bitrate, capture five-second CPU/heap profile windows from a physical
ESP8266, and summarize the UART log.

Generate 48 kHz stereo fixtures:

    .	oolsesp8266_audio_profilegenerate_fixtures.ps1

Configure the native ESP8266 firmware with:

    -DYORADIO_ESP8266_AUDIO_PROFILE=ON
    -DYORADIO_ESP8266_AUDIO_PROFILE_URL=http://<PC-IP>:8765/stream.bin

Use esp8266/rtos-sdk-native/sdkconfig.audio-profile.defaults so FreeRTOS
runtime counters are enabled. To discard PCM after decode and bypass
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