# Actual collection and offline verification

These receipts record the successful collection and independent offline replay
of the [codebook archive](../vorbis-codebook-20261025/CHECKPOINT.md), manifest
SHA256 `fc1da4905175a9e6baca72affea5d518296d0ad14344e4315aff49ea784f6699`.
Both owned commands terminated normally with exit 0. Their original stdout and
stderr streams are retained verbatim alongside the receipts.

Offline replay runs the archive's verifier from the parent repository directory.
It recomputes all 382 host and 400 native exact comparisons through explicitly
pinned pure definitions. Boundary C assertions and previous protocol method
counts are rebound by receipt/output integrity; no compiler, SDK, QEMU, decoder
or lint command runs during offline replay. The finite layer is qualified;
complete floor0/G6/PCM, radio integration and physical acceptance remain open.

Reproduce with `python tests/results/vorbis-codebook-20261025/verifier.py`.
