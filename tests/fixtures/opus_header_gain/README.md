# Paired OpusHead output-gain fixture preparation

`generate.py` derives zero, +6 dB and -6 dB variants from the complete existing
706319-byte synthetic 20 ms Opus stream. It changes only the signed little-endian
Q7.8 gain at OpusHead bytes 16–17 and the first page's CRC. All 551 audio packets,
comments, lacing, granules, serial/sequence fields and later pages stay identical.
The zero variant is byte-identical to the original. All page CRCs are rechecked.

```text
python -B tests/fixtures/opus_header_gain/generate.py --output .build/opus-header-gain-new
python -B tests/test-opus-header-gain.py --output .build/opus-header-gain-tests-new
```

Generation runs no decoder, compiler or emulator. These data checks do not prove
that the Espressif Ogg path applies or ignores output gain. A separate measured
public-vendor experiment is required before applying application gain, to avoid
doubling adjustment already performed by the library.

[RFC 7845 section 5.1, field 6](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1)
defines scaling by `10^(gain_q8/(20*256))`. Default playback application is a
SHOULD; any chosen volume/normalization adjustment must be added to that header
gain. Header edits also require updating or removing existing R128 gain tags,
so the generator refuses originals containing those tags instead of silently
leaving inconsistent metadata. Our pinned original has no such tags.

The independent reference plan uses the creator's
[public raw Opus decoder](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html),
then explicit normative gain before PCM16 rounding/clipping. Its optional
[public gain control](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoderctls.html)
can provide a separate cross-check; no private state is inspected.
