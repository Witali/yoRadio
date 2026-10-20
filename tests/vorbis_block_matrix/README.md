# Vorbis block-size fixture generators

These standard-library generators preserve all 36 legal ordered short/long
pairs from 64 through 8192 samples. They prepare public raw-format fixtures and
Ogg carriers for independent host references. They do not run codecs, SDKs,
compilers or emulators. Existing target and physical gates remain separate.

`generate_minimal.py` constructs a stereo two-book fixture. Its 14 packets cover
SS/SL/LS/LL and every previous/next flag combination on long modes. Each mode
uses the same floor1/residue1 setup; floor endpoints 16 fit inside even the
smallest transform. Deterministic residue vectors contain both -1 and +1.
`matrix.json` records all 36 cases, raw headers/packet offsets, expected samples,
bitfield accounting, CRCs and hashes. Equal-size pairs retain both mode labels
and all flag syntax even though their window lengths coincide.

The default sample rate is 48000. `--rate` accepts integers 1..4294967295; it changes
the identification header and matching metadata, without rate conversion. A
positive rate is structurally encodable; this does not mean every rate has been
independently decoded. Output must be fresh and stay beneath this checkout's
`.build`; the default is `.build/vorbis-minimal-block-<rate>-01`. Existing outputs
are rejected. Resolve this generator from the current worktree, not another
checkout.

```powershell
& $python -B tests/vorbis_block_matrix/generate_minimal.py --rate 48000 `
  --output .build/vorbis-minimal-48000-01
& $python -B tests/vorbis_block_matrix/generate_minimal.py --rate 192000 `
  --output .build/vorbis-minimal-192000-01
```

`generate_encoder_matrix.py` preserves the realistic 42-book setup and donor
audio from the adjacent pinned `encoder-192000.ogg`. It emits 36 identity cases
and 36 transition cases at 192000 Hz. Only block exponents and the documented
transition-neighbor flag bits change. The source carrier SHA256 is
`82ef0b5354ac3baea18d24479360a4b1d84956c789b969333f333efcb018e2f1`;
both carrier and concatenated audio hashes are checked before output. It reads
the supplied FFmpeg/FFprobe bytes to record identities and writes command plans;
it does not execute those commands. Use fresh output under `.build`:

```powershell
& $python -B tests/vorbis_block_matrix/generate_encoder_matrix.py `
  --output .build/vorbis-encoder-matrix-01 --ffmpeg $ffmpeg --ffprobe $ffprobe
```

The historical 48000 Hz minimal 36 cases passed both FFmpeg native and Xiph
libvorbis references. The original combined 108 dual-reference campaign remains
NONPASS: native FFmpeg 8.1.1 rejected 30 encoder-derived cases because of its extra
floor1 endpoint-versus-largest-block bound. A later completion qualified all 108
through Xiph, retaining 78 successful native cross-checks and those 30 explicit
native limitations. No cases were dropped. The normative floor1 algorithm
extends or truncates a curve to the selected transform length; it does not add
that setup bound. Preserve the original refusal evidence alongside completion.
This statement describes frozen historical corpus results, not qualification of
the adapted generator bytes or any target decoder.

Before treating these canonical generators as reproducing that evidence, run
pure generation at 48000/192000 and compare actual raw/header/carrier payloads
against the corresponding frozen corpus. Generator-hash metadata necessarily
changes. Independent decode must retain actual metadata, sample counts, nonzero
PCM and failures, without forced sample-rate/channel conversion. A new rate or
fixture change needs its own reference result. The tiny fixture supplements the
realistic corpus and cannot establish broad G6 conformance alone.

Primary references: [Xiph Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
sections 2, 3.2.1 (single-entry erratum), 4.2.2/4.2.4, 4.3.1/4.3.8,
7.2.2–7.2.4, 8.6.1–8.6.2, 9.2.2 and appendix A;
[Xiph Ogg framing](https://xiph.org/ogg/doc/framing.html);
[Xiph libvorbis floor1 implementation](https://github.com/xiph/vorbis/blob/v1.3.7/lib/floor1.c);
[FFmpeg 8.1.1 floor parser](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/vorbisdec.c).

Ogg carriers here serve host references only. These generators do not qualify
target Ogg handling, EOF/reset/pending/OOM, private AAC, resource savings,
physical audio or the complete Vorbis standard.
