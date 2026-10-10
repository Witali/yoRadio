# Clock-only listening installation, 2026-10-10

The user requested the precise hardware 48 kHz mode for listening. The quiet
application was built from the installed `8c1f2d2d` production source, with
only the frozen clock-build overlay, and installed through WebUI app OTA.

- `source-manifest.json`: original Git source hashes and the three overlay files.
- `overlay/`: CMake integration, opt-in Kconfig setting and audited driver generator.
- `build-audit.json`, `code-objects.json`: only one effective setting changed;
  19 codec/output objects have identical text/constant sections; RAM unchanged.
- `host-tests.json`: five existing divider/driver tests passed.
- `deployment.json`: OTA acceptance, app identity, three playing observations,
  and settings comparisons. It contains no Wi-Fi credentials or station URLs.
- `logs/`: original build console and compiler/configuration logs. The first
  configuration attempt lacked the tracked root `playlist.csv` in the isolated
  source snapshot. It was restored from the same commit before the successful
  build; no firmware from that failed attempt was installed.

## Rebuild

Use the pinned local ESP-IDF and audio-codec dependencies. From the repository
root, with `.build/c3-pdm-listening-20261010` absent:

```powershell
python tests/results/esp32c3-pdm-listening-20261010/prepare.py
./tests/results/esp32c3-pdm-listening-20261010/build.ps1
python tests/results/esp32c3-pdm-listening-20261010/audit.py
```

The source snapshot and build directory are isolated under `.build`; the
successful app is exported to `firmware/development/esp32c3-idf61-listen-48k`.
The audit also needs the retained original production build for object and
section comparison. Rebuilding changes build metadata and is not a promise
of byte-identical application hashes.

`deploy.py` records the executed app-only procedure and expected initial
image. It refuses to overwrite the original deployment report; a future
installation must use a fresh evidence destination and verify board identity.
Successful deployment leaves the new image playing for the user, rather than
restoring the integer clock automatically.

Analog listening remains pending. The short status check is not an acoustic
test or a complete codec/network regression matrix. Repository defaults remain
unchanged. See [the report](../../../docs/ESP32C3_PDM_LISTENING_20261010.md).
