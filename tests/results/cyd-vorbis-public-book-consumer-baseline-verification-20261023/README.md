# Public owned-book baseline archive verification, 2026-10-23

The standalone [baseline checkpoint](../cyd-vorbis-public-book-consumer-baseline-20261023/CHECKPOINT.md)
was verified before and after exact create-only promotion. The canonical replay
used cwd C:/Work/yoRadio, different from the task worktree. No compiler, SDK,
QEMU, full-stream decoder or reference PCM was launched by these offline steps.

The earlier SDK6.0.2/Xtensa baseline contains 36 canonical publications, 365
exact Fraction vectors and 439 protocol events. The independent host baseline
contains 331 exact, sanitizer-clean vectors and 34 actual UBSan aborts with
unavailable vectors. Its full sanitizer/numerical qualification remains false.
Verifier exit0 establishes archive consistency; it does not change NONPASS to
PASS, qualify portable C or establish an opaque vendor PCM cause.

| Operation | Actual terminal tool chunk |
| --- | --- |
| Pack01 | `ddac2b` |
| Stage offline verification01 | `2e0605` |
| Exact create-only promotion01 | `128e2a` |
| Canonical offline verification01 from different cwd | `15843e` |

All four actual receipts bind argv/cwd, owned PID, runner/executable hashes,
normal exit0 and exact stdout/stderr. Their copied log bytes are rechecked.
The promotion proof keeps its original COPIED_PENDING_CANONICAL_REPLAY state;
it was not rewritten after later successful canonical verification. Every
canonical file was rechecked against the original promotion inventory.

Main archive: 1739 physical files / 9221016 bytes, 1738 identity rows and 20
explicit binary omissions. Linux compiler/Python tool identities remain
recorded actual facts; no Windows rehash of /usr/bin or current-file fallback
is claimed. Manifest SHA256:
`a9d1e10fea01b75c5df0f0880dfafc26c2a69f941064420ccb7f19cf782c67d4`.
No prior archive is required. The complete original public source/license,
all 26 source controls, raw arrays, independent oracle, host records and frozen
SDK inputs/protocol/compiler/link/QMP records are retained.

The earlier completed zero-guard proposal is historical, record-only analysis.
The later guarded draft is excluded. The separately pinned
[deferral](../../../docs/CYD_PUBLIC_BOOK_ZERO_GUARD_DEFERRED_20261023.md)
records the automatic content flag; no guarded runtime is qualified here.
Earlier PCM NONPASS, full G6, radio integration, resources and physical tests
remain open. Production stream core0/decode-output core1 and their priorities
and stacks are unchanged.
