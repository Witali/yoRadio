# AAC block-output fixtures

Deterministic one-second gated tones, generated with FFmpeg 8.1.1 by
`generate.ps1`: AAC-LC ADTS, mono 22050 Hz/48 kbit/s and stereo 44100 Hz/
192 kbit/s. These complement the retained stereo 48-kHz/320-kbit/s fixture.
The transients exercise window changes; exhaustive synthetic tests separately
compare all four window sequences, both shapes, PCM and next-frame overlap.
No external recording or user data is included.
