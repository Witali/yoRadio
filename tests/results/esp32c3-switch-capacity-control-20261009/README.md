# Matched FLAC queue-capacity switching controls

Physical ESP32-C3, ESP-IDF 6.1 revision `9a97f6c54ec6`, 2026-10-09.
Fresh app-only OTA boots run in extra-slot order **0 / 4 / 4 / 0**.
Each boot runs three FLAC -> HE-AAC -> HE-AACv2 cycles, four HTTPS EOF
cases, and 75 seconds of HE-AACv2 with TLS records growing to 16 KiB.

See [the report](../../../docs/ESP32C3_SWITCH_CAPACITY_CONTROL_20261009.md)
for results and limits. `summary.json` retains original verdicts and raw
heap checkpoints; `comparison.json` condenses them. `verified.json` checks
evidence completeness and provenance, not acoustic or production acceptance.
Prior failed observations remain in the preceding experiment unchanged.

The two binaries and their source/configuration audits are reused from
`../esp32c3-flac-input-growth-20261009`. `references.json` pins that archive's
index; `references.py` verifies its indexed files before importing analyzers.
This avoids another copy of the same firmware sources. Obtain Git LFS app
binaries before replaying the linked image/CRC checks.

From the repository worktree, offline replay:

```powershell
python tests/results/esp32c3-switch-capacity-control-20261009/replay.py --output .build/switch-capacity-replay-new
```

Use a new output directory. Replay makes no network or serial calls and
reproduces all verdicts, including failures. The physical controller is a
record of this laboratory run, not a generic flashing shortcut: it binds
specific firmware identities, host addresses, COM9 and a short-lived test
certificate. A new physical run needs a valid trusted laboratory certificate,
a new evidence directory and an outer restoration path for the actual board.
Do not disable certificate validation. Private settings and keys are absent
from this archive.
