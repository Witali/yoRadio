# Synthetic maximum-duration Ogg Opus fixture

`stereo-510-120ms.ogg` preserves the complete original 11-second synthetic
calibration audio. Its source is the pinned lossless
[`flac-level8.flac`](../esp32c3_calibration/flac-level8.flac), originally generated
by [`generate.ps1`](../../../tools/codec_benchmark/generate.ps1). No radio audio,
credentials or board configuration are included.

The installed FFmpeg `libopus` encoder produces 92 stereo CELT packets. Each
contains six 20 ms frames, or 5760 samples per channel: **23040 PCM16 bytes**.
This deliberately exceeds the production caller's initial 12288-byte buffer.
[RFC 6716 section 3](https://www.rfc-editor.org/rfc/rfc6716.html#section-3)
permits packets up to 120 ms. The container has 14 CRC-valid consecutive pages.

Raw packets contain 529920 frames; pre-skip is 312 and terminal granule is
528312. The required playback is 528000 frames / 2112000 PCM16 stereo bytes,
after 1608 terminal padding frames are excluded.
[RFC 7845 sections 4.2–4.4](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2)
define this timeline. Independent full decoding through FFmpeg's `libopus`
wrapper confirms that length. Its bundled libopus version is not reported;
numeric equivalence to the Espressif decoder is not claimed.

Generate into a fresh ignored capture directory:

```text
python -B tests/fixtures/opus_ogg_long_packets/generate.py --output .build/cyd-opus-long-fixture-<fresh>
```

The generator records executable/source hashes, all commands and actual child
statuses, validates CRCs/framing/timeline, and requires repeated encoding to be
byte-identical with the same installed tool. Original source/playback PCM and
the full capture remain local. The checked-in `evidence` preserves the exact
generation report and command logs; `manifest.json` binds the fixture.

Run the data-only verifier, including five malformed-container/packet guards:

```text
python -B tests/fixtures/opus_ogg_long_packets/verify.py
```

This is input preparation only. No MCU decoder, SDK, QEMU or physical board was
run. Public `BUFF_NOT_ENOUGH` sizing/retry behavior, consumed input and actual
task playback with this fixture remain **unqualified**.
