# Physical DIO/QIO recheck, 8 October 2026

This archive retains the sequential DIO 80 MHz and QIO 80 MHz comparison on
the ESP32-C3 rev. 0.4 with 4 MiB XMC Flash. Read
`docs/ESP32C3_QIO80_RECHECK_20261008.md` in the repository for the result,
interpretation and limitations.

## Evidence

- `physical/*/report.json`: original per-case outcomes, including failures.
- `physical/*/status.json` and `performance.json`: observations used by the
  acceptance and timing calculations. Boot-readiness suites have no status file.
- `physical/*-boot-{1,2}.log` and `.json`: actual SPI0 mode/clock, image identity
  and four mapped-image CRC reads per boot.
- `physical/*-ota.json`: negative/interrupted upload, roundtrip and slow OTA.
- `physical/phases.json`: controller exit codes and durations.
- `physical/flash-restoration.json` and `final-board.json`: restoration checks.
- `physical/restoration-recovery.json`: failed first readiness wait and the
  successful extra watchdog reset; the original failure is not discarded.
- `summary.json`: reproducible aggregation; an evidence-test pass does not
  change an unsuccessful physical test into a pass.
- `dio/`, `qio/`, `artifacts/`, `sources/`: build commands, linked-code audits,
  exact configurations and relevant source snapshots.
- `index.json`: SHA-256 and size of each retained file; `source-index.json`
  separately authenticates the source snapshots.

Application and matching bootloader binaries are saved outside this archive in
`firmware/development/esp32c3-idf-6.1-r9a97-flash-{dio,qio}80/`.

## Replaying the analysis

From the repository root:

```powershell
python tests/test-flash-mode-probe.py
python tests/test-qio80-recheck-evidence.py
python tests/results/esp32c3-qio80-recheck-20261008/summarize.py --output "$env:TEMP/qio80-summary.json"
```

The last command recomputes the summary without overwriting retained evidence.
The tests check file hashes, actual mode, application CRCs, original outcomes,
restoration and rejection of missing cases or telemetry. They do not flash a
board or perform audio playback.

`physical.py` is the exact laboratory controller used for this run, not a
general-purpose one-command flashing tool: it pins a particular board,
original image, partition layout, local fixture origin and trust material.
Recreate those prerequisites and choose a fresh output directory before a new
physical run. The laboratory builds contain an eight-second boot probe delay
and experimental memory overlays; they are not production releases.

Private full-Flash backups, Wi-Fi/playlist snapshots, TLS keys and audio fixture
contents are excluded. Settings were compared in memory before restoration;
the archive retains only equality results. After the original controller exited,
its reference snapshot was unavailable. Final persistence evidence uses the
exact pre-boot NVS/SPIFFS readback and the last successful pre-restore comparison,
not a newly claimed post-retry snapshot comparison. NVS and SPIFFS were not
written during restoration.
