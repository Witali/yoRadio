# Advertised mono/stereo and mapping construction proposal

Source-only fixture preparation. All cases contain complete valid-data candidate
packets and await independent decoding. No PCM is generated or observed here.
No decoder, SDK, compiler, QEMU, reference tool, Git or device is executed.

`generate.py` imports the canonical `tests/vorbis_block_matrix/generate_minimal.py`
only after requiring raw SHA256
`8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1`.
It reuses its bit writer, fixed small books, integer packed-float helpers,
deterministic sign function, comment and CRC/page routines. It copies no helper
file and does not mutate imported globals/functions.

Exactly 18 base cases cover channels 1 and 2 at each rate 8000, 11025, 12000,
16000, 22050, 24000, 32000, 44100 and 48000. Each case has short256/long2048,
14 packets (`SSLLLSLSSSLLSS`) and all four adjacent/long-neighbor transitions.
Identification contains the actual channel/rate values. Audio explicitly loops
over the requested channels for floors, classwords and residues. Uncoupled
single-submap setup has no per-channel mux fields, so its identical mono/stereo
bytes are intentional; changing only identification would be insufficient.

The explicit common setup difference from the minimal helper is floor1
`rangebits=10` (endpoint1024, long block/2), versus helper4 (endpoint16).
This isolates channels/rates from the previously observed native FFmpeg endpoint
restriction. Both endpoints have y255, multiplier1, no floor partitions. Stage
vectors have bounded mixed signs and are distinct per channel in a pure integer
symbol model. Those facts do not establish decoded PCM, clipping or sound.

Three separate stereo48000 supplements retain the same blocks/modes/floor:

- `coupled`: one magnitude0/angle1 pair. A complete four-entry, dimension1,
  length2 map1 book has values -2,-1,+1,+2. Magnitude uses ±2, angle ±1;
  the first four bins exercise all sign quadrants. Wire codewords are bit-reversed.
- `submaps`: channel mux is [1,0], with separate residue1 spans/partitions16 and32.
  Floors stay in channel order; residue bundle0/channel1 precedes bundle1/channel0.
- `residue2`: one32-scalar interleaved bundle, one classword, deinterleaving16
  bins/channel. This differs from two independently coded residue1 vectors.

Each case supplies full30-byte `identification.bin`, full prefixed `setup.bin`,
`comment.bin`, concatenated `audio.bin`, offsets/modes, expected overlap frames
and s16le byte counts per packet, raw SHA256s and a CRC-checked `reference.ogg`.
One complete audio packet/page, primer granule0 and natural final EOS are used
only as future host-reference carriers. Target Ogg APIs are outside this work.

The pure checks extract actual setup/audio fields with a bounded reader,
reconstruct integer residue/coupling vectors, check all field padding, CRCs,
packets, granules and ordering, and reject six named wrong-channel/order/packing
controls. This is neither an audio decoder nor independent conformance proof.
`construction.json` records exact fields and symbol vectors, not synthetic PCM.
`manifest.json` pins every emitted file and source; input identities must remain
unchanged. No prior fixture, campaign or canonical source is changed.

```powershell
& $python -B .build/cyd-vorbis-mono-mapping-prep-01/generate.py `
  --output .build/cyd-vorbis-mono-mapping-prep-01/generated01
```

Root must independently decode all21 candidates, retain every refusal/nonpass,
verify actual rate/channels, per-packet sample counts and nonzero/distinct PCM,
then own any ample-buffer public raw open/decode/close target campaign. This
does not cover >2 channels, allocation pressure, errors, streaming lifecycle,
private decoder state, audio hardware, or broad Vorbis conformance.

Primary source audit:

- [Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
  4.2.2/4.2.4, 4.3.2–4.3.8, 8.6.2/8.6.4/8.6.5: channel metadata,
  mapping fields, channel-floor/submap-residue order, inverse coupling and
  interleaved residue2. Mono has no coupling; stereo pair indices use one bit.
- Xiph v1.3.7 [mapping0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c)
  `mapping0_unpack`/`mapping0_inverse` and
  [res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c)
  `res1_inverse`/`res2_inverse`: field widths, bundle order and interleaving agree.
- Xiph [sharedbook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c)
  `_make_words`/`_book_unquantize`: four equal-length entries map to reversed
  wire words0,2,1,3 and the explicit scalar values used here.
- [Espressif public codec README](https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_codec/README.md),
  VORBIS: nine rates, mono/dual and16-bit output are advertised; no claim that
  the pinned target has passed them follows from that advertisement.
- Local public setup source `idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c`
  SHA `d23fd5cb2ad7d8c3a87ebcda2197421245f571dea5724de3d328058264e491c2`,
  `repair_mapping_info_unpack`: submap/mux/residue indices and coupling widths
  match these candidates. Its local `ilog(channels)` first decrements, therefore
  stereo width1 matches normative `ilog(channels-1)`; no source edit is needed.

Web sources were read through the browser tool; URLs/sections identify the audit,
not fabricated downloaded-byte hashes. The actual imported/local source bytes are
pinned separately. Source qualification remains pending real reference evidence.
