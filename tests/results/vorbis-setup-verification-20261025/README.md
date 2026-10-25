# Actual collection and offline verification

These receipts record successful collection and independent offline replay of
the [setup archive](../vorbis-setup-20261025/CHECKPOINT.md), manifest SHA256
`9d20f00c136500492c36a69fffda9ba01c55613ad529755204289303b122f27a`.
Both owned commands terminate normally with exit 0; their original stdout and
stderr streams are retained verbatim.

Offline replay runs from the parent repository directory and uses explicitly
pinned pure definitions. It regenerates all 300 inputs and their predeclared
200-case native subset from retained raw fixture bytes, then repeats every host
and all 400 native exact comparisons. No saved main, compiler, SDK, QEMU,
reference decoder or lint command executes offline. Legacy protocol method
counts have receipt/output integrity scope only. Full synthesis, PCM, raw/radio
integration and physical acceptance remain open.

Reproduce with `python tests/results/vorbis-setup-20261025/verifier.py`.
