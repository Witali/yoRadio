# Public multistream composition diagnostic

The inputs are the unchanged creator-valid family1 packet transports from the
separate public Ogg observation. `framing.py` reads RFC6716 section3 and AppendixB
framing, preserving each original self-delimited segment byte-for-byte. The
ordinary-framing control removes only the extra length field. It never alters
coded frame payload, padding, channel mapping or packet duration.

`tests/run-opus-multistream-public-reference.py` qualifies the split before any
ESP32 run: separate creator public mono/stereo OpusDecoder handles must reproduce
every original multistream float sample exactly after the declared mapping.
It also compares the entire mapped PCM to the previous creator reference and
runs 32 independent expected-byte/malformed framing controls. These are framing
and reference checks, not universal codec conformance tests.

`tests/run-cyd-opus-multistream-public-qemu.py` then measures concurrent public
Espressif raw Opus handles with documented configuration and stable caller-owned
config lifetimes. Coupled streams request stereo, others mono, at48kHz/16bit.
Original self-delimited segments and ordinary-framing controls use separate
fresh cases. Every return, consumed size, output geometry, frame count and close
is observed. Full per-stream PCM is retained locally for the complete mapping
comparison. No production adapter, private codec layout, serialized state,
archive modification or allocation-failure injection is used.

AppendixB support is optional for an elementary decoder. That does not remove
the Ogg player's family0/1 playback requirement. Relevant primary sources:
[RFC6716 section3](https://www.rfc-editor.org/rfc/rfc6716.html#section-3),
[AppendixB](https://www.rfc-editor.org/rfc/rfc6716.html#appendix-B), and
[RFC7845 section5.1.1.5](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.5).
