# Full TLS renegotiation: preserved output failures

Initial campaign: 17/18. HE-AAC record-size comparison: 16/18.
Both controllers restore the listened application and verify saved settings.

```text
python -B tests/results/esp32c3-tls-renegotiation-20261010/review.py
python -B tests/results/esp32c3-tls-renegotiation-20261010/review.py physical-comparison
```

Replay PASS reproduces the saved failures; it does not certify the firmware.
Numeric health/status, TLS handshake callbacks, completed writes, request
timing, dependency versions/hashes, test sources and restoration are retained.
Private keys and dependency installation contents are excluded. Only public
certificates and a local path to the existing test key are saved.

Host verification: two real renegotiation/refusal cases, four quiet gate
tests, and six existing record-server regressions. `host-renegotiation.log`
retains the initial callback-count assertion failure; `host-renegotiation-final.log`
is the corrected positive/negative result. Frozen module names identify the
final implementation; the initial failure is not represented as a passing run.

The firmware is reused from the AAC growth campaign; its full build audit is
in `../esp32c3-aac-growth-tls-20261010/`. Index hashes protect raw file bytes.
[Report](../../../docs/ESP32C3_TLS_RENEGOTIATION_20261010.md).
