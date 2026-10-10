# Public HTTPS evidence for one-second prefill

See [the report](../../../docs/ESP32C3_PREFILL1000_PUBLIC_20261010.md). Original acceptance failures are retained.
`review.json` saying `review: PASS` means that evidence/identity/restoration checks
succeeded, not that the firmware passed all acceptance gates.

`physical/` contains original observations and controller restoration evidence.
`test-sources/` freezes the exact runner sources. `prior-build/` references the
previous committed build audit instead of duplicating the build.
`firmware-manifest-before.json` and `firmware-manifest.json` retain earlier gates.

From the repository root, replay without board access:

```text
python -B tests/results/esp32c3-prefill1000-public-20261010/review.py
python -B tests/results/esp32c3-prefill1000-public-20261010/verify_commit.py
```

`index.json` records byte sizes and SHA-256; `.gitattributes` prevents conversion.
Network/OTA/private-settings equality checks remain recorded live assertions.
The controller script requires a reachable board and changes firmware; do not
run it as part of offline review. Public audio and private keys are not included.
