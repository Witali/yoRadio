# HE-AAC TLS pause: PCM starvation with responsive output task

Physical result: 17/18; the 16 KiB record case has 17 output queue drops.
Sixteen detailed events remain; one was overwritten, and the phase histogram
retains all 17. Replay PASS reproduces the saved failure, not production acceptance.

```text
python -B tests/results/esp32c3-pipeline-probe-20261010/review.py
python -B tests/results/esp32c3-pipeline-probe-20261010/analyze.py
```

`physical-walltime/` is the measured final campaign and exact restoration.
`physical/` and `initial-cycles/` retain the earlier CLI-argument failure,
initial cycle-counter build and restoration. No playback result is inferred
from that aborted invocation. The final system-timer source and build audit
are separate from the initial cycle-counter files.

The archive includes frozen source, raw numeric health/status, encrypted
record metadata, source/build audits, host sanitizer evidence and public
certificates. Private keys, package installations and temporary binaries are
excluded. Local key paths are references only. The saved development app is
in `firmware/development/esp32c3-idf-6.1-r9a97-quiet-pipeline-probe/`.

[Report](../../../docs/ESP32C3_PIPELINE_PROBE_20261010.md).
