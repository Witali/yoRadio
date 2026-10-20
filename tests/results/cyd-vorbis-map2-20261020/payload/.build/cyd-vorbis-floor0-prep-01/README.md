# Complete floor0/residue0 packet candidates

Source-only construction in an ignored directory. No codec, SDK, compiler,
emulator, Git or physical-device command is part of this preparation. The
generator performs bit-syntax/CRC round trips, not floor-curve, IMDCT or PCM
synthesis. Validity and actual nonzero PCM remain pending independent references.

Nine stereo/48000 Hz cases combine these variants with block pairs 64/256,
256/2048 and 64/2048:

| Variant | Floor | LSP order/dimension | Bark map | Amplitude width | Floor books |
| --- | --- | --- | --- | --- | --- |
| floor1-r0 | floor1 control | none | none | present + Y255/Y255 | none |
| floor0-even6-r0 | floor0 | 6/3 | 64 | 6 bits, raw 44..55 | one |
| floor0-odd5-r0 | floor0 | 5/3 | 128 | 8 bits, raw 176..207 | two |

Floor0 offset is 60 dB and its rate field is 48000. Its codebooks use maptype2,
minimum 0, delta 1/16 (`62000001`), sequence_p0 and two one-bit Huffman entries.
Even-order vectors are `[7,14,21]/16` and `[8,15,22]/16`. Odd-order book0 uses
`[8,16,24]/16` and `[9,17,25]/16`; book1 uses `[7,15,23]/16` and `[8,16,24]/16`.
The second decoded vector adds the last coefficient of the first. Used LSPs
are strictly increasing, at least 7/16 radians apart and below 3 radians. The
odd-order variant consumes both full words and ignores the sixth scalar.
Packets vary amplitudes, selected book, LSP words and residue vectors by packet
and channel. These conditioning properties are arithmetic construction checks;
they are not numerical synthesis or audible-quality results.

All variants use residue0 with begin 0/end 16, partition 16, one classification,
one pass, scalar single-entry classbook 0 and mapped stagebook 1. Stagebook1 is
dimension 2/entries 4 with length 2 codewords and maptype1 vectors
`[-1,-1], [1,-1], [-1,1], [1,1]`. Words have their Huffman bit order reversed
when sent through the LSB integer writer. Residue0 writes vector components at
indices `i` and `i+8`, not adjacent indices. Both classwords precede both
channels' VQ words. Every encoded vector contains both signs. Residue end 16 is
inside the minimum block's 32-bin vector, so no residue clipping is needed.

The 14 modes `SSLLLSLSSSLLSS` retain all SS/SL/LS/LL transitions and all long
previous/next flags. Each case provides full `identification.bin` (30 bytes),
prefixed `setup.bin`, `comment.bin`, concatenated `audio.bin`, offsets/modes,
`packets.json` with exact floor/residue fields and expected frame/PCM sizes,
and `reference.ogg`. There is one complete audio packet per Ogg page: primer
granule 0, subsequent cumulative `(previous_N+current_N)/4`, natural final EOS.
Manifest paths are relative to the fresh output directory.

`minimal_support.py` is an unchanged byte copy of canonical
`tests/vorbis_block_matrix/generate_minimal.py`, SHA256
`8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1`.
Only its pure definitions are imported; its main/generator is never called.
This reuses the already reviewed bit writer, packet prefix, identification,
comment, deterministic sign selection and Ogg framing/CRC helpers. Local input
hashes and exact primary-source URLs/tags are in `inputs.json`; web source bytes
were read, not archived or assigned fabricated raw hashes.

```powershell
& $python -B .build/cyd-vorbis-floor0-prep-01/generate.py `
  --output .build/cyd-vorbis-floor0-prep-01/generated01
```

Root's independent host gate should retain all nine cases, check FFprobe/WAV
rate 48000/channels 2 and actual per-frame durations, decode with Xiph and FFmpeg
without forced rate/channel conversion, inspect diagnostics and demonstrate
nonzero PCM in each channel. Full sample totals must match the matrix. Preserve
failures rather than removing difficult variants.

The later public raw target gate should use opaque open/decode/close only,
complete packets and an ample 16384-byte output buffer. Retain one metadata
object for each opened handle; expect metadata 48000 Hz/stereo/16-bit even on
primer packet 0, then full packet consumption, zero primer output, exact later
PCM bytes, unchanged buffer canaries, successful close and nonzero PCM.
No buffer-shortage, partial-packet, EOF/reset/OOM, target Ogg or private-state
behavior is being qualified here.

Primary sources: [Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
sections 3.2.1, 4.2.4, 6.2.1–6.2.3, 8.6.1–8.6.3, 9.2.2 and appendix A;
[Xiph v1.3.7 floor0](https://github.com/xiph/vorbis/blob/v1.3.7/lib/floor0.c),
[codebooks](https://github.com/xiph/vorbis/blob/v1.3.7/lib/codebook.c),
[residue0](https://github.com/xiph/vorbis/blob/v1.3.7/lib/res0.c) and
[LSP curves](https://github.com/xiph/vorbis/blob/v1.3.7/lib/lsp.c).
They confirm the floor-book selector width `ilog(numbooks)`, accumulated LSP
vectors, allowed unused final coefficients and residue0 interleave. No broad
Vorbis/G6, physical audio, resource-benefit or unrelated codec claim follows.
