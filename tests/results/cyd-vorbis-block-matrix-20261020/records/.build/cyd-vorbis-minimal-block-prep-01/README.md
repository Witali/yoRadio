# Minimal public raw-format supplement

This deliberately small fixture supplements the realistic 42-book corpus. It
retains all 36 legal short/long block pairs, including equal-size pairs. It is
not a replacement for real-encoder coverage or a broad G6 conformance result.

`generate.py` uses only Python's standard library and writes a fresh child output
directory. It invokes no decoder, SDK, compiler, emulator or other process.
Run it with a non-SDK Python interpreter and `-B`, for example:

```powershell
& $python -B .build/cyd-vorbis-minimal-block-prep-01/generate.py `
  --output .build/cyd-vorbis-minimal-block-prep-01/generated01
```

The proposed bitstream follows the primary [Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
sections 2, 3.2.1 (including the 20150226 single-entry erratum), 4.2.2/4.2.4,
4.3.1, 7.2.2/7.2.3 and 8.6.1/8.6.2. Ogg carriers follow appendix A and
[Xiph's Ogg framing specification](https://xiph.org/ogg/doc/framing.html).

Construction: two stereo modes share a floor1 and residue1 through one mapping,
with no coupling. Floor partitions=0, multiplier=1 and rangebits=4 produce two
implicit X endpoints; both packet Y endpoints are 255. Residue occupies bins
0..15, one partition of 16, inside even the 64-sample block's 32-bin vector.
Book0 is scalar, dimension1, one entry, length1, map0; its codeword consumes one
zero bit. Book1 has two one-bit entries mapping to -1/+1. The packed-float
equation independently yields `e2800001=-1` and `62800002=2`, with exponent788
and mantissas -1/2. These are Vorbis packed floats, not IEEE-754 values.

Fourteen mode labels `SSLLLSLSSSLLSS` cover SS/SL/LS/LL and all four previous/next
flags on long modes. Flags come from actual neighbors. Equal-size pairs retain
the distinct mode/flag syntax even though their window lengths coincide.
Both channels' floors precede both classwords, followed by each channel's 16
deterministic varying VQ signs. Every vector contains both signs. The constructed
spectrum is nonzero; actual nonzero PCM remains an independent decode gate.

`matrix.json` exposes a `cases` list: id, relative ogg, short, long, rate,
channels, mode_flags, expected_raw_samples per channel, packet sample counts,
granules and hashes. `bitfields.json` records every field's bit offset, width
and value. `fixture.h` exposes the raw headers/packets and all per-case expected
sample counts. `manifest.json` binds every generated payload and the generator.

The carriers exist only for future independent host references. Each header and
audio packet occupies one page; packet0 primes at granule0, subsequent granules
sum `(previous_block + current_block)/4`, and only the final page has EOS.
The generator reconstructs packets and verifies each CRC with a separate table
path, and rejects a corrupted-page control. These are construction checks.

Root's next gate is all 36 cases through FFprobe and separate FFmpeg native and
libvorbis decode, without forced sample-rate/channel conversion. Check actual
metadata, exact sample counts, nonzero PCM and decode diagnostics. Keep every
case, including any failure, and preserve this construction as history if a
successor is needed. Float decoders need not produce bit-identical PCM. Actual
target raw API proof remains separate. No target Ogg API, EOF/reset/pending/OOM,
private AAC or physical audio claim follows from these files.
