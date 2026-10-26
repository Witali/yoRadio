# Isolated native floor1 product qualification

This project exercises only `native_vorbis_floor1_scale_measure` and
`native_vorbis_floor1_scale`. Setup ownership, packet/frame decoding, Xiph DSP,
floor0, transforms, PCM, radio tasks and previously deferred targets do not run.
The generic host fixture is copied unchanged into the frozen project and its
main renamed; only its refusal helpers execute. Production files are unchanged.

The controller derives2957 bounded calls from all1663 host rows. Endpoint rows
are split into positive/negative256-coefficient batches. Each1792-bin pattern
row becomes seven256-coefficient batches. Every original selected scalar is
retained exactly once, including all1087 widths, all256 coefficients and both
signed endpoints. These batches retain the original common factor-grid extrema.
Three additional small3-channel rows exercise channel selection. Their per-call
shapes differ from the host campaign; this is not full host-metadata parity or
a complete-stream format claim. Synthetic1087-bit shapes exceed the format's
actual1079-bit residue bound and qualify the arithmetic helper's stated domain.

Peak wide input/output storage is approximately72KiB before small guards and
SDK overhead. Input samples are regenerated for exact immutability comparisons;
the fixture avoids a second full input snapshot. Capacity and failure controls
use bounded cases and the unchanged generic helper. Assertions remain enabled.

The coordinator stays on core0. A priority3 worker with16384-byte stack runs on
core1 for ESP32 and core0 for C3. Only the worker mutates test counters. Each
bounded output chunk and each row yields one tick; watchdog settings stay at
their SDK defaults. This is new standalone fixture scheduling, not a change to
any deferred decoder target. Compiler stack records are individual frames,
not complete call-chain or physical performance measurements.

Output words use canonical run-length encoding inside contiguous128-word
chunks. This encoding is lossless: the pure reader expands and independently
compares every word with rational table conversion and Python integer products.
No digest substitutes for per-value comparison. Duplicate, truncated, malformed,
wrong-core, altered-output and panic transcripts fail strict parsing.

From the task worktree on Windows:

```powershell
python -B -X utf8 tests/test-vorbis-floor1-product-protocol.py
python -B -X utf8 tests/run-vorbis-floor1-product-qemu.py --target esp32 --output .build/floor1-product-esp32-fresh
```

Use `--target esp32c3` for the separately installed pinned C3 SDK/QEMU. Every
campaign requires a fresh output directory. `--prepare-only` writes the finite
model and frozen sources without compiling or executing a target. Installed
SDK revisions and tool hashes are checked/retained. The private installation
path of an executable, when under a personal home directory, is intentionally
replaced by a tool alias in public metadata; its exact SHA256 is retained.
Other SDK/project/QEMU arguments remain explicit. Raw logs need a local privacy
review before any publication.

Actual results are reported only after a complete native transcript and exact
numeric comparison. A fixture build is not a production firmware handoff and
does not establish physical audio timing, full decoder conformance, memory
benefit or production readiness.
