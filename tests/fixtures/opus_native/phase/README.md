# CELT phase-buffer regression packets

These are generated from our own deterministic noise/tone signal, not recorded
or copyrighted audio. The manifest pins packet bytes and the input PCM digest.
`tools/esp8266_opus_profile/generate_phase_fixtures.cjs` documents the complete
signal and FFmpeg/libopus arguments; it can regenerate these fixtures with the
recorded encoder version. A different libopus encoder version may emit different
valid packets and requires deliberate manifest/evidence regeneration.

The generator drops Ogg headers/tags and stores each audio packet as a little-endian
16-bit length followed by packet bytes. Ogg serial-number randomness therefore
does not enter the checked files. The `.opuspkt` files need no FFmpeg at test time.

The corpus includes 2.5/5/10/20-ms stereo CELT, 20-ms mono CELT, transient-rich
independent stereo channels, CBR packets containing 2/4/8 frames, and two-frame
VBR packets. Repacketization preserves the encoded frame bodies and only changes
Opus packet framing; incomplete final groups are discarded. Every packet is at
most 20 ms. Runtime wrappers, not TOC guesses, verify both transient and
dual-stereo decoding were exercised while the PCM buffer was borrowed.

Run `node tools/esp8266_opus_profile/run_phase_regressions.cjs` for PCM, guard,
reset, short/multiframe, repeated PLC and downsampling-denial tests. The original
five fixtures and mixed SILK/hybrid/CELT corpus are also included. Saved evidence
is `tools/esp8266_opus_profile/pcm-scratch-results.json`.
