# Composite AAC-LC fixtures

Same deterministic stereo 44.1-kHz/16-bit, 1-second tone/noise source as
../mp3_composite/tone-noise.wav. The WAV is reused, not duplicated.

Encode AAC-LC in ADTS at target 48/64/96 kbit/s. Each file has 45 complete
1024-sample frames (including encoder priming/padding), 1.044898 seconds.
Actual ADTS-inclusive rates: 48.770 / 63.126 / 93.850 kbit/s.
Maximum ADTS frame sizes: 201 / 227 / 338 bytes. Total flash data: 26,873 bytes.
Encoder version and hashes are recorded in manifest.json.

    node tools/esp8266_audio_profile/generate_composite_aac.cjs

Select YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX=ON and
YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX=OFF together with CODEC_RAM_BENCHMARK.
Set CODEC_RAM_FRAMES=1000 and CODEC_RAM_AUDIO_OUTPUT=ON for about 23.22
seconds of measured PCM per case; OFF for decode-only. All options have
the YORADIO_ESP8266_ prefix. The normal 512-sample mono AAC output blocks
and 2 x 512-word PDM32 DMA buffers are retained.

Files stay in mapped internal flash; read directly into the existing
decoder input buffer and decode sequentially. Wi-Fi and web services
are disabled during measurement. The matrix never selects MP3.
Restore ordinary firmware after the benchmark. These fixtures do not
test HE-AAC/SBR, high bitrates or analog distortion.
