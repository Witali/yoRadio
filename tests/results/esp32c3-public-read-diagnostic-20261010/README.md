# Public stream read diagnostics

[Report](../../../docs/ESP32C3_PUBLIC_READ_DIAGNOSTIC_20261010.md). Diagnostic image; no production pass is claimed.

From the repository root:

```text
python -B tests/results/esp32c3-public-read-diagnostic-20261010/review.py
python -B tests/results/esp32c3-public-read-diagnostic-20261010/verify_commit.py
```

`review: PASS` means evidence replay/restoration succeeded, not playback acceptance.
`physical/` retains original failures, independent FFmpeg progress, bounded numeric
health and exact restoration. `build-sources/`, `test-sources/`, `host-test-sources/`
and `host-tests/` freeze the inputs and checks. Source/reference hashes identify
the SDK and tools. `index.json` verifies byte-exact files.
Do not run `physical.py` for offline review: it performs app-only OTA.
