# ESP32-C3 input buffer retention and heap-owner study

Physical ESP32-C3, pinned ESP-IDF 6.1 revision `9a97f6c54ec6`, 2026-10-09.
See [the report](../../../docs/ESP32C3_INPUT_RETENTION_20261009.md).

`physical/` captures original expanded and control queues. `physical-fixed/`
compares the original expanded queue with the retention fix. Each trial has
one continuous serial capture, three FLAC -> HE-AAC -> HE-AACv2 cycles,
four HTTPS EOF cases, a 75-second HE-AACv2 TLS record-growth test, and a
60-second idle window without WebUI polling.

The first fixed-image capture ends with an incomplete serial line after its
runtime gate. Its original report has 15 passes, but the independent complete
capture gate fails. `physical-confirmed/` repeats the same firmware with
bounded final-line completion and an explicit runtime gate after capture
closure. Original truncated evidence remains intact. The shared capture
change and its tests are saved in `capture-sources/`.

`trial-fixed.py` changes only the record server's shutdown ordering: Stop
and settled idle complete inside its lifetime. Both old and fixed images use
this corrected runner in `physical-fixed/`. The original early-shutdown TLS
errors remain in `physical/`; the replay does not waive them.

`review.json`, `review-fixed.json` and `review-confirmed.json` derive owners, independent format/EOF
checks and cross-stage heap recovery. `verified.json` checks identities,
sources and provenance. An evidence-verification PASS does not convert any
failed playback report to PASS and is not analog or production qualification.

The prior 226-file source snapshot and shared analyzers are referenced by a
hash-pinned index in `references.json`; the three changed firmware files
are saved in `fixed-sources/`. Host snapshots include the failing regression
before the fix and sanitizer results afterwards. Initial audit diagnostics
are preserved, including the inlined-helper symbol-check correction.
`build-audit.json` contains the completed linked-image audits.

Run offline from the worktree (Git LFS app binaries must be present):

```powershell
python tests/results/esp32c3-switch-owner-20261009/replay.py --output .build/input-retention-replay-new
```

Use a new output directory. Replay does not contact the board. The physical
controllers are records of this lab run, with specific image identities,
host address, COM9 and short-lived certificates. A new physical experiment
needs a fresh trusted certificate, new evidence directory and restoration
path. Public certificates are retained; private TLS keys and board settings
are excluded.
