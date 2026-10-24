# Vorbis floor1 presence supplement

This finite supplement has 39 cases: 9 mono and 30 stereo, each with 14 raw
packets at 48000 Hz, blocks 256/2048, and mode schedule `SSLLLSLSSSLLSS`.
The complete corpus has 546 packets and 971520 expected PCM16 bytes. It covers
floor1 present/absent, residue0/1/2, stereo coupling and all four floor masks,
fixed packet-to-packet presence changes, and short/long overlap transitions.
Scalar vector dimension1 deliberately gives residue0/1 identical scalar order;
this does not add multidimensional residue0 placement coverage.

Nine constant-all-absent cases and twelve mixed-mask stereo cases separately
witness silence. `pcm_witness.py` derives every guaranteed silent frame span
from the previous/current floor masks and window supports. It checks all silent
samples and requires some nonzero output on channels with a contributing floor.
Current floor absence alone does not imply a silent output packet.

From the repository root, choose a fresh direct child of `.build`:

```powershell
python -B -X utf8 tests/vorbis_format_corpus/generate_floor_presence.py --output .build/vorbis-floor-presence-canonical-01
$FloorMatrixPath = '.build/vorbis-floor-presence-canonical-01/matrix.json'
$FloorMatrixSha = (Get-FileHash -LiteralPath $FloorMatrixPath -Algorithm SHA256).Hash.ToLowerInvariant()
python -B -X utf8 tests/vorbis_floor_presence/test_controls.py --matrix $FloorMatrixPath --matrix-sha256 $FloorMatrixSha
```

Existing outputs are rejected. The generator uses only the pinned canonical
mono/mapping and minimal-block construction helpers. The 17 controls exercise
the protocol, uint64 case mask and silence witnesses with explicitly synthetic
PCM/logs; they do not run a decoder or establish reference PCM equivalence.

Root has recorded 30 passing controls (17 protocol/witness plus 13 reference /
numeric controls), all 39 cases through both reference decoders (78 commands),
and a separate successful recorded-reference qualification using the frozen
preparations. The canonical generator reproduces all 197 payload files exactly,
and all 17 canonical controls pass. CYD target PCM comparison remains pending.
Reference/target numerical acceptance requires
both Xiph libvorbis and independent FFmpeg-native vorbis, complete original
channels/packets, all silence witnesses, and the predeclared maximum error of
2 signed-S16 LSB. That is a project regression bound, not a normative Vorbis
tolerance. These cases do not establish complete Vorbis/G6 conformance, target
Ogg handling, physical audio or production radio integration.

The primary basis is the [Xiph Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html):
sections 4.3.3 (coupling-aware decode-needed propagation), 7 (floor1), 8.6.5
(residue2 bundle skip behavior), and 4.3.8 (overlap output). Xiph v1.3.7
[mapping0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c)
provides coupling and final floor application; [res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c)
provides the distinct residue0/1 and bundled residue2 inverse paths.
