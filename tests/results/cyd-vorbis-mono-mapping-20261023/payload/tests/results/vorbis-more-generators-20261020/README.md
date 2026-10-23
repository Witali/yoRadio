# Additional Vorbis generator reproduction, 2026-10-20

The two canonical generators completed with exit0. Their internal field,
packet, CRC and spectral-model checks, including14 exact rejection controls,
passed. All29 cases/406 packets retain689920 expected PCM16 bytes.

All149 nonprovenance output files are byte-identical to the original corpora,
including145 complete binary packets/carriers. Only four provenance files
changed: each pure-checks input list and each manifest source list/pure-checks
hash. The comparison rejects any other change. `report.json` records every
unchanged output size/hash and both complete source-input lists. The receipts
retain actual argv, owned PID, terminal status and log identities.

The mono bank contains18 mono/stereo cases at nine advertised rates and three
mapping supplements. The map2 bank contains four sparse/dense or single/twin
pairs, sequence0/1; the single-entry audio exercises both0/1 bits.
`source-projection.json` and both diffs preserve the limited source adaptation.
The exact generator bytes are in `tests/vorbis_format_corpus/`; generate fresh
outputs with the commands in that directory's README.

This is construction/reproducibility evidence. The generated binary corpora
are represented by hashes rather than duplicated here. Historical `.build`
paths identify the actual commands. `compare_outputs.py` documents that run;
it requires those original corpora and create-only output paths. It is not a
standalone replay of the host or target campaigns. No codec, SDK, QEMU or device
was executed by these generator/comparison commands. Finite construction checks
do not qualify target formats or complete Vorbis conformance.
