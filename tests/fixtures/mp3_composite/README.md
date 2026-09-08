# Composite MP3 benchmark source

Self-authored, deterministic 1-second stereo 44.1-kHz/16-bit waveform:
440/997-Hz tones, 200..6000-Hz chirp, seeded white and low-pass noise,
short noise bursts, and a changing envelope. Peak is -3.01 dBFS, no clipping.
The two channels share a tonal component but have different noise/sweep content.

All three MP3s encode the SAME WAV at 64/128/320 kbit/s using libmp3lame.
There is no Xing/Info/ID3 header; the normal MP3 bit reservoir remains enabled.
Each file has 40 sequential MPEG1 frames, including normal encoder priming/padding.
Hashes and encoder version are in manifest.json. Regenerate with:

    node tools/esp8266_audio_profile/generate_composite_mp3.cjs

For a physical MP3-only test, enable CODEC_RAM_BENCHMARK,
CODEC_RAM_MP3_MATRIX and CODEC_RAM_AUDIO_OUTPUT with the YORADIO_ESP8266_
CMake prefix. Set CODEC_RAM_FRAMES=1000. Encoded files are embedded in the
test application's mapped internal flash (not SPIFFS); all three total
66,873 bytes. Read at most 1,536 bytes directly into the existing decoder
input buffer, decode in order, then loop the complete file. No clip-sized
RAM allocation or second staging buffer is used. Normal radio builds do
not include these files; Wi-Fi, playlist and WebUI storage is unchanged.
The wall-clock measurement includes flash reads; decode-call timing does not.
AAC is not decoded or selected by this matrix. Restore normal firmware after testing.

This is a reproducible workload, not a claim that synthetic audio covers
every music, speech, MPEG mode, or worst-case decoding path.
