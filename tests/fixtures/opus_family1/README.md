# Public family 1 diagnostic inputs

`tests/run-opus-family1-reference.py` creates fresh ignored captures with the
installed, measured creator libopus public multistream surround encoder. The
complete 3-, 6- and 8-channel inputs use its default family 1 mappings and have
eleven 20 ms packets, 9600 logical samples per channel, queried encoder delay,
and genuine final padding. Distinct low-amplitude tones activate every speaker;
LFE uses 73 Hz. No existing fixture is edited.

The independent Python writer owns OpusHead, OpusTags, lacing, page sequence,
serial, granules and CRC. It retains every complete creator packet. Framing and
malformed-input controls are data-only; they do not claim codec correctness.
The separate creator libogg reader walks every complete generated file under
whole and 257-byte schedules, reconstructing all original packet bytes and
checking pages, granules, BOS/EOS, CRC synchronization and packet holes.

The separate reference executable opens a fresh public multistream decoder and
decodes all channels. It writes full raw PCM, full stereo PCM and the logical
stereo window. The stereo matrix uses the exact formula coefficients in
[RFC7845 section 5.1.1.5](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.5),
figures 4, 7 and 9. Every speaker contributes to at least one side, including
LFE. Rounding is nearest, ties away from zero, then saturation to PCM16. The
native observation does not introduce a numeric acceptance tolerance.

`tests/run-cyd-opus-family1-qemu.py` measures stock public Espressif Ogg decoding
before the current playback wrapper. Whole and 257-byte schedules each use a
fresh handle. Exact real public returns, consumption, reported PCM layout,
resize requests, drain and cleanup are retained. Reported refusal is an
observation, not an assertion that rejecting a mandatory mapping is permitted.
Full executable, fixture transport and PCM payloads remain local diagnostics.
