# Normal-trust one-second prefill qualification

See [results and limitations](../../../docs/ESP32C3_PREFILL1000_QUIET_20261010.md). Production qualification
is still open. The exact previously listened app was restored after tests.

```text
python -B tests/results/esp32c3-prefill1000-quiet-20261010/review.py
python -B tests/results/esp32c3-prefill1000-quiet-20261010/inspect_file_windows.py
```

Review PASS means the recorded verdicts reproduce within the documented scope.
Raw evidence, source snapshots, build audit and restoration are preserved;
private settings and private keys are not saved. The build is available under
`firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000/`.
