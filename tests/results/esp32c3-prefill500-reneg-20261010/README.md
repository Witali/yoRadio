# 500 ms minimum prefill: physical TLS renegotiation comparison

Physical acceptance: 30/34. The candidate is not
production-qualified. Exact listened firmware and settings were restored.

```text
python -B tests/results/esp32c3-prefill500-reneg-20261010/review.py
```

Replay PASS reproduces the saved failures. The archive preserves build/source
identities, object comparison, public certificates, physical observations,
test sources and restoration. Private keys and installed packages are excluded.
The existing test key path appears only as a local reference.
Build artifacts are in `firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill500-reneg/`.

[Report](../../../docs/ESP32C3_PREFILL500_RENEGOTIATION_20261010.md).
