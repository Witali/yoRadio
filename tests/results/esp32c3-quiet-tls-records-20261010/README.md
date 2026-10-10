# Quiet HE-AAC TLS record-size campaign

Physical verdict: **58/58**; failed checks: None.
The exact listened application and settings were restored.

Run the offline review from the repository root:

```text
python -B tests/results/esp32c3-quiet-tls-records-20261010/review.py
```

Replay PASS means saved verdicts reproduce; it does not turn a failed physical
gate into PASS. Frozen test modules, numeric status/health, request-phase timing,
actual TLS record lengths, completed write counts, public certificates, image
identity and restoration evidence are retained. Private keys, Wi-Fi credentials,
playlist contents and TLS plaintext/ciphertext are excluded. The running
controller's arguments contain only a local key path, never key contents.

The build is reused byte-for-byte from the preceding AAC growth campaign.
`reused-build-*` files and `firmware-manifest.json` identify that saved audit;
the original full build evidence is in `../esp32c3-aac-growth-tls-20261010/`.
Host checks: three quiet-record gate tests, six real local TLS server tests,
three sustained-output gate tests. Initial sandbox access failure did not run
the server tests; the saved six-test log is from the successful permitted run.

`index.json` covers all archived files except itself with size and SHA-256.
`verify_commit.py` also checks byte-for-byte equality with committed Git blobs.
[Report](../../../docs/ESP32C3_QUIET_TLS_RECORDS_20261010.md).
