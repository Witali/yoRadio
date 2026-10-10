# One-second input prefill: physical TLS renegotiation

Physical acceptance: 34/34. Production qualification is pending.
Exact listened firmware and settings were restored after the campaign.

```text
python -B tests/results/esp32c3-prefill1000-reneg-20261010/review.py
```

Replay PASS means all saved verdicts reproduce, including any failed checks.
The archive contains source/build identities, host tests, measurements,
public certificates and restoration evidence. Private keys and dependencies
are excluded. Firmware: `firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000-reneg/`.

[Report](../../../docs/ESP32C3_PREFILL1000_RENEGOTIATION_20261010.md).
