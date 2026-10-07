# AAC fixtures with missing SBR extension data

These are synthetic tones, not radio recordings. Three source files are
byte-identical to the pinned HE/HEv2 files in `../aac_stream_format/`. A fourth
is a 0.5-second, 32 kHz mono, 24 kbit/s HE-AAC tone encoded with the same FDK
encoder. `manifest.json` records input, encoder, trace and generated hashes.

The generator verifies all 129 files of the pinned FAAD source archive, then
adds passive `fill_element` tracing to a disposable `syntax.c` copy. The
reference extraction stays unchanged. The trace identifies the complete SBR
FIL element (extension type 13/14) in every frame. Only that element is removed.
AAC core bits and trailing fill-data/empty FIL elements stay unchanged; ADTS
frame length and final byte alignment are updated. Unknown suffix elements,
CRC-protected frames, multiple raw blocks and inconsistent counts are rejected.
The resulting files are parsed again to verify that no SBR element remains.

The QEMU test plays `source → missing → source` without resetting between
phases. This is controlled extension loss, not a recording of a network outage.
All frames, including startup and the artificial loop boundaries, enter the
precision comparison. The sequence deliberately contains 11–15 consecutive
frames without SBR, extending the earlier single synthetic LC/HEv2 transition.

FAAD float/fixed retain full decoded rates and SBR/PS state in these sequences.
The native SDK duplicates HE mono into stereo PCM by default. The QEMU test
requires that behavior to match the unchanged controller byte-for-byte, and
checks that every output L/R pair is identical. The mono **source** remains
mono; duplicated PCM does not establish parametric stereo (PS).

From the worktree root, with the installed host tools:

```powershell
python tools/codec_benchmark/generate_aac_sbr_gaps.py --source <verified-faad-source> --encoder <aac-enc> --work .build/aac-sbr-gaps/generator --output tests/fixtures/aac_sbr_gap
python tools/codec_benchmark/check_aac_sbr_gap_reference.py --output .build/aac-sbr-gaps/faad
```

The second tool uses the verified executable hashes/paths retained by the
previous FAAD comparison; relocate/rebuild and verify those tools before using
it on another machine. Source-level reference:
[pinned FAAD extension parser](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/syntax.c).
This is reference implementation evidence, not full MPEG conformance proof.
