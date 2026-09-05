# ESP8266 build-time mono / stereo

## Selection

`menuconfig -> yoRadio ESP8266 options -> Decoded audio channels`:

- `CONFIG_YORADIO_AUDIO_MONO=y`: default for the Wemos one-pin PDM profile.
- `CONFIG_YORADIO_AUDIO_STEREO=y`: retain both decoded PCM channels.

The choices are mutually exclusive. For a fresh stereo build, supply
`-DSDKCONFIG_DEFAULTS="<repo>/esp8266/rtos-sdk-native/sdkconfig.stereo.defaults"`.
This is a complete profile, not an overlay (this SDK accepts one defaults file).
Use a new build directory when changing profiles; existing `sdkconfig` values
take precedence over defaults. Stereo decoding alone does not turn one-pin PDM
into stereo: physical stereo requires `CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PCM`
and an external stereo DAC. Arduino/ESP32 keep their previous stereo path:
the shared Helix macro `YORADIO_HELIX_MP3_MONO` defaults to zero.

## What mono optimizes

For M/S joint stereo without intensity stereo and with matching transform
windows, Helix skips the side channel's Huffman payload and dequantization.
Only one IMDCT and one polyphase synthesis run. The existing dequantizer's
M/S scaling already produces `(L+R)/2`; adding another divide would attenuate
audio incorrectly. Side scalefactors are still parsed to preserve MPEG1 SCFSI,
and compressed side bits are consumed to preserve reservoir/frame alignment.
Network bandwidth is unchanged.

Ordinary L/R, dual-channel, intensity stereo and incompatible windows use
both spectral/IMDCT paths, average their results, then run a single synthesis.
AAC and experimental libmad also honor mono output, but downmix after their
normal decoding; side-channel skipping is specific to Helix MP3.

The overlap history is explicitly kept in the mono domain during the fast
path. Compatible old L/R overlaps can be averaged on entry; on fallback the
mono overlap is copied to both paths. Differently windowed previous overlaps
force a full granule before the fast path can resume. Nothing is allocated or
freed between granules. Decoder reset also resets this domain state.

MP3 callback PCM storage drops from 2304 to **1152 bytes** (576 mono samples),
saving 1152 bytes DRAM. Spectrum, fallback overlap and the 16-KiB IRAM arena
remain allocated. This is not a claim of halving total decoder RAM.
PCM channel metadata reflects the decoded output. Independent left/right
balance cannot be recovered after early mono downmix.

## Regression checks

Run `node --test tests/esp8266-helix-golden.test.js tests/esp8266-mp3-memory.test.js`.
Tests compile actual Helix code in both channel modes and compare mono with
the averaged stereo reference. Coverage includes MPEG1/2/2.5, original mono,
M/S, L/R, dual-channel, intensity, frame-mode switches, long/short/mixed
windows, stereo-to-mono headers, decoder reset, and PCM-buffer canaries.
The full-frame and synchronous granule callback APIs must produce identical
PCM. A private-state test compares fast/fallback IMDCT against the full path.

Own short tone fixtures are stored in `tests/fixtures/helix_mono/` and regenerated
with `tools/esp8266_audio_profile/generate_mono_fixtures.ps1` (FFmpeg/libmp3lame).
The original 320-kbit/s noise fixture is also tested with deliberately changed
MPEG1 mode bits; these are decoder regression vectors, not listening samples.

Host results, 2026-09-05, Helix SSO on both sides:

| Vector | Huffman calls stereo -> mono | SNR vs averaged stereo | Max PCM error |
| --- | ---: | ---: | ---: |
| Forced M/S, 320 kbit/s | 72 -> 36 | 49.79 dB | 21 |
| Alternating stereo modes | 72 -> 58 | 49.78 dB | 21 |
| MPEG1 tones | 72 -> 50 | 49.65 dB | 22 |
| MPEG2 tones | 36 -> 26 | 49.07 dB | 21 |
| MPEG2.5 tones | 20 -> 12 | 48.84 dB | 21 |
| Original mono | 19 -> 19 | bit-exact | 0 |

Window/history tests without SSO differ by at most one PCM level. Stereo
golden MP3/AAC hashes are unchanged. Small differences are expected because
fixed-point rounding now occurs after early averaging; clipped stereo PCM
is not a linear reference for high-amplitude input.

New MPEG2.5 coverage also exposed an older 12-bit sync-mask bug: the decoder
now uses the correct 11-bit sync and rejects the reserved MPEG version.

These are correctness and invocation-count tests, **not ESP8266 CPU timing**.
Physical speed, RF-load stability and listening checks remain to be measured.
The board is not flashed by this change.

Final verification: **329 host tests passed** (33.79 seconds), recorded in
`docs/benchmarks/esp8266-mono-2026-09-05/regression.log`. Native Mono firmware
and the Helix/AAC Stereo and libmad/AAC Mono components compiled with Xtensa
GCC 8.4. The application and manifest are saved under
`firmware/development/esp8266-native-mono/`; the previous board-tested binary
is preserved separately.
