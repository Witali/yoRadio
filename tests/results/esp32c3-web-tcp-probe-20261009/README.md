# WebUI TCP probe physical repeat

See [the report](../../../docs/ESP32C3_WEB_TCP_PROBE_20261009.md).
Application checks pass 16/16; TCP telemetry is incomplete and rejected.
No timeout was reproduced. This does not resolve the prior WebUI failure.

`physical/` preserves app-only OTA identities, the full filtered trial,
individual socket attempts, settings-equality booleans and restoration.
`sources/` freezes firmware main sources and test/server helpers. The CMake
snapshot includes an unrelated inactive CLZ experiment; the linked audit
confirms that it was not compiled. `host/` contains sanitizer results and
the wrapper harness, without native test executables. `audit/` preserves
the linked routes and AAC/FLAC object-section comparisons.

`review-in-progress.json` is an explicitly incomplete intermediate view.
`review.json` is the final strict review, including merged-line rejection.
The failed telemetry gate is retained in both. `build.log` contains wrapper
output and saved image identity; the SDK build's child console output was
not fully redirected. The compiled artifact and ELF route audits provide
separate build evidence.

Run offline from the repository root (no network or board needed):

```powershell
python tests/results/esp32c3-web-tcp-probe-20261009/replay.py --output NEW_DIRECTORY
```

This verifies exact archived bytes, firmware/config/source hashes,
restoration evidence and reproducible analysis. A successful replay means
the observations reproduce, not that the failed TCP telemetry gate passes.

`physical.py`, `trial.py`, `build.ps1` and `audit.py` retain the original local
recipe. They use explicit host/board addresses and a short-lived local CA;
the private key is intentionally absent. Do not rerun them without preparing
fresh paths and trust material. Saved source/build paths reflect the original
workspace. No packet bodies, credentials or TLS private keys are archived.
