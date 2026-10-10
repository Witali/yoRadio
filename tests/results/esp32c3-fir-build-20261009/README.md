# FIR rate compensation: build and host evidence

See [the report](../../../docs/ESP32C3_FIR_RATE_20261009.md).
This archive covers the implementation, audited diagnostic image and host
tests only. It does not contain or imply a successful physical campaign.

`build-sources/` contains firmware sources checked before/after the build;
it includes the pre-existing inactive CLZ CMake option as provenance. That
option is explicitly OFF and excluded from compile commands. The top-level
working-tree change is not part of this implementation's commit.

`host/`, `default-regression/` and `default-boundaries/` retain source hashes
and logs. Regenerable PCM/executable files are omitted; reports keep their
sizes/digests. `source-hashes.json` and the artifact manifest pin exact source
bytes. The sandbox DLL failure and successful objdump audit are both retained.

Offline integrity check:

```powershell
python tests/results/esp32c3-fir-build-20261009/replay.py
```

The saved PowerShell build recipe refers to original local lab paths. For
another physical run use new output paths, valid certificates and fresh
source/image checks. No private TLS key or user Wi-Fi settings are archived.
