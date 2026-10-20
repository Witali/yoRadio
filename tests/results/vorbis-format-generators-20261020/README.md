# Vorbis format generator reproduction, 2026-10-20

Both canonical generators completed with exit 0; all eight canonical books
construction tests passed. Across eight books and nine floor0/residue0 cases,
all 100 nonmanifest files are byte-identical to the original corpora. Only the
two manifest source/provenance fields differ as recorded in `report.json`.

The report retains the size and SHA256 of every generated nonmanifest file,
original/canonical manifest identities and the exact permitted metadata changes.
The three actual command receipts and stdout/stderr files retain command argv,
working directory, owned PID, terminal status and log identities. Source-relation
and adaptation files preserve the reviewed scope of the generator changes.
Original `.build` paths identify historical runs; this small record does not
include the generated corpora. Recreate them with the canonical generator commands
in `tests/vorbis_format_corpus/README.md` and compare against the recorded hashes.

This is construction/reproducibility evidence. No new codec, SDK or target ran.
The earlier host result remains Xiph 17 accepted and FFmpeg native NONPASS
(7 accepted, 10 lookup2 refusals); this record does not qualify target formats.
