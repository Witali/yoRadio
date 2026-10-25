# Owned quantization evidence replay, 2026-10-25

The [checkpoint](../vorbis-quantization-20261025/CHECKPOINT.md) passes complete
offline replay from the parent checkout. Actual terminal `b8fdfe` exits0.
All6572 host cases and400 native cases are independently replayed, including
exact metadata/multiplicands/affine values and92+184 floor comparisons.
The separate affine phase certificate is recomputed. Exact values include
both reconstructed outputs and direct affine inputs retained through floor
calls; the checkpoint gives their breakdown.

Manifest SHA256:
`db595dc78b39cf104c17356a65604aaca2abf5cd3a0ffef3130fe3ebba805f46`.
The bundle contains359 aliases,163 objects and31 explicit identity-only
omissions. Actual collection terminal `9e1326` exits0. Its original receipts
and complete stdout/stderr streams are saved alongside this README.

Replay uses explicitly pinned pure oracle/protocol definitions. No saved main,
compiler, SDK, QEMU, component or decoder executes. Earlier2376/60541 results
are checked for integrity and full byte parity; their mathematical campaigns
are not recomputed offline. Legacy12/13 protocol results concern parser tests,
not an additional SDK execution.

The accepted result is a standalone quantization/VQ/LSP and affine-floor layer.
Complete entropy/setup/audio parsing, wide synthesis, PCM/raw integration and
full floor0/G6/G8 remain open. Compiler frames exclude callee/libm/task
high-water; selected SDK files and omitted binary identities do not establish
complete dependency closure or physical performance.
