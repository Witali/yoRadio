# Synthetic Opus corpus

These fixtures contain locally synthesized tones and seeded white noise, not
recorded music. `manifest.json` pins both Ogg files and raw packet streams by
SHA-256 and records the actual Opus TOC mode, duration and channel coverage.

| Fixture | Encoder input | CBR | Mode observed | Packets |
| --- | --- | --- | --- | --- |
| mono-12 | mono | 12 kbps | SILK | 61 × 20 ms |
| mono-24 | mono | 24 kbps | hybrid | 61 × 20 ms |
| stereo-64 | stereo | 64 kbps | CELT | 61 × 20 ms |
| stereo-128 | stereo | 128 kbps | CELT | 61 × 20 ms |
| stereo-510 | stereo | 510 kbps | CELT | 61 × 20 ms |

`*.opus` is the original Ogg Opus container. `*.opuspkt` repeats a two-byte
little-endian unsigned length and that many raw Opus packet bytes, excluding
OpusHead and OpusTags. The decoder processes every packet to 48 kHz mono,
producing 58,560 samples per fixture. It does not trim Ogg pre-skip or end padding.

The 1.2-second source combines 997 Hz and 10,007 Hz tones in the left channel,
a 1,703 Hz tone in the right channel, and noise seeded with 7349. Generation used
FFmpeg 8.1.1's libopus encoder at constant bitrate, with `voip` for mono fixtures
and `audio` for stereo. The fixed synthesis seed makes the source reproducible;
encoder versions and Ogg serial/metadata can change file bytes. The committed
hashes are the authoritative test inputs; normal tests never regenerate them.

To deliberately replace the corpus, run
`node tools/esp8266_opus_profile/generate_fixtures.cjs`, then
`node tools/esp8266_opus_profile/fixtures.cjs --write-manifest`, and rerun the
full baseline/bounded/pristine comparison before updating its saved evidence.
The generator requires FFmpeg on PATH and overwrites the named fixture files.
