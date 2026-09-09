# ESP8266 native: volume 0..100

Built 2026-09-09 from `be0207e10354be7c6ff9be52f06bac5b77532c03`.
Not flashed during this task. This is a replaceable development build of
the production profile, not a versioned release or tone-test firmware.

- `app.bin`: 763952 bytes, SHA-256
  `fdb5565b24e72a7badadca7bac90ebf7a0dc1f04d5ad8ae11374cafee4aa0214`.
- Companion `script.js.gz`: 10406 bytes, SHA-256
  `f755b140f2aeb4dde1e9ea907c043252ac7da3a65cf56758281549338c84c9ac`.
  Exact copy of shared `yoRadio/data/www/script.js.gz` at that revision.
- Bundle revision `89964e82`; player/settings gzip 27249/26974 bytes.
- `sdkconfig` SHA-256
  `2e1e9dd769f6fac8be01f2acae3947a85aadb17d9f2a904f528345c1b5937f1`.

## Update order

1. Upload companion `script.js.gz` to SPIFFS `/www/script.js.gz` using the
   existing file-maintenance workflow. It is compatible with the old app.
   Keep Wi-Fi, playlist and other SPIFFS files; no format/partition rewrite.
2. Use native application OTA for `app.bin`. Do not send serial commands or
   reset over UART while the audio circuit is connected to RX/GPIO3.
3. Reload all browser tabs. Slider must have min 0, max 100, step 1; API
   `volume=N` now uses percent. Update third-party clients accordingly.
   Old WebUI/API clients sending 128/254 will be clamped to 100.
4. Verify endpoints and save/reboot on the board at a safe listening level.
   These physical steps have not been performed for this artifact.

## Verification

Command:

```powershell
$taskTests = @(rg --files tests -g 'esp8266*.test.js' -g 'webui*.test.js')
node --test @taskTests
```

Result: 324 passed, 0 failed, 0 skipped; 139.171 seconds.
Full host output: [host-tests.log](host-tests.log).
Includes compiled actual volume-control/command functions, all 101 levels,
old raw values and simulated persistence/readback, mutex/error paths and
real shared-script capability handling. Existing PCM/PDM tests still pass.
No physical power-cycle persistence or browser rendering claim is made.
The expanded run also exposed an older test-fixture omission: reconnect
code was unchanged, but its bootstrap helper was missing from the harness.
The fixture was corrected in separate commit `e340395`.

Build command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-volume100-production -WebAudioPause short
```

GCC build: success, no compiler warnings in build log.
Compared with `esp8266-led-production` from `82edaf2`:

| Section | Previous | This build | Delta |
|---|---:|---:|---:|
| DRAM data | 1648 | 1648 | 0 |
| DRAM BSS | 19840 | 19840 | 0 |
| IRAM vectors + text + BSS | 27484 | 27484 | 0 |
| Flash text | 533686 | 534050 | +364 |
| Flash rodata | 204392 | 204732 | +340 |
| Application image | 763248 | 763952 | +704 |

No new runtime allocation. Conversion is integer and outside the PCM loop;
legacy gain and NVS version 1 remain unchanged. Default raw 160 displays 63.
All percent values round-trip through raw storage exactly; old values retain
their original gain until the user changes the control.

This does not resolve or remeasure the existing occasional WebUI transfer
delays / short DMA underruns; see the separate LED regression report.
