# Quiet production health qualification, 2026-10-10

Candidate: `idf61-quiet-mpi-health`, ESP-IDF `9a97f6c54ec6`, QIO 80 MHz,
nominal fractional 48 kHz, early MPI initialization and on-demand health.
The binary is saved in
`firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health/`.

This archive preserves failed acceptance cases. `review.json` gives the
original case counts, health observations and restoration evidence. A passed
replay establishes evidence consistency, not production qualification.

## Evidence

- `source-hashes.json` and `build-sources/`: actual inputs captured before
  building. `source-head.txt` predates the health implementation commit;
  the overlay includes that implementation and the inactive CLZ CMake edit.
- `quiet-mpi-health/`: image/config/codec/link audits. The inactive CLZ
  experiment is excluded from compilation. Codec arithmetic is unchanged.
- `health-audit.json` and disassembly: quiet fault callbacks, RAM and startup.
- `native-health/`: actual callback/handler C tested with SDK doubles and
  ASan/UBSan, both watchdog configurations. This is not target timing evidence.
- `physical/`: five ordinary-root public HTTPS station observations and
  original failures, independent source-format checks, request phases, heap
  and lifetime fault counters. Later phases in this controller are skipped
  when the public phase fails.
- `physical-local/`: a separately identified installation for local HTTP,
  transitions, network faults, WebSocket and OTA cases. Its phases file
  identifies which suites actually completed; no skipped case is a pass.
- `test-sources/`: byte-exact tools used by both controllers.
- `latency-analysis.json`: device-snapshot timing bounds for the retained
  slow public HTTPS observation. This is not a packet capture or proof of
  the network component responsible.
- `public-fixture-candidates.json`: discovered HTTPS candidates, not tests.

Each controller restores the previously listened fractional-clock image,
verifies settings persistence and observes the stopped state three times.
Only persistence booleans are saved; credentials and broadcast audio are not
retained. Source URLs are public. Local board/test-host IPs identify the lab.

The health endpoint detects boot changes, allocation failures and task
watchdog events. It does not measure DMA continuity, analog quality or every
decoder error. Existing diagnostic measurements remain separate evidence.

## Replay

From the repository worktree, run the following using Python 3.12 or newer,
with a new output directory outside this archive:

```text
python tests/results/esp32c3-quiet-health-20261010/replay.py --output .build/quiet-health-replay
```

Replay checks archived file hashes, source and image identities, test source
identities, both restorations, then recomputes the review. It sends no board
commands and does not replay OTA. The original physical controllers are
retained for audit; do not run them merely to replay saved evidence.
