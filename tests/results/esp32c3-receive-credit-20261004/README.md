# Receive credit experiment evidence

See [the measured report](../../../docs/ESP32C3_RECEIVE_CREDIT_20261004.md).
The production goal is still open; a passing evidence check is not a passing
physical acceptance suite.

- `baseline/`: original network image, three 180-second paced codec cases.
- `receive/`: receive-credit image, the same files and durations; includes the
  post-Vorbis largest-block recovery failure.
- `https-after-load/`: 180-second HE-AAC HTTPS test starting from that fragmented
  heap, before any reboot. The restore step intentionally reboots afterward.
- `unpaced/`: three 60-second ordinary HTTP download controls; all ten gates pass.
- `ota/`: application-only transition to the receive-credit image.
- `baseline-sources/`, `sources/`, `control-sources/`: exact runner bytes for each
  stage, matching the respective `test_sources_sha256` maps. Firmware sampler
  and host test snapshots are included under `sources/`.
- `physical/`, `netrx-build.json`, `build-delta.json`: build/configuration identity
  and measured layout. The installable application is retained separately in
  `firmware/development/esp32c3-aac-pc19-netrx/`.

`stress-fixtures.json` records the FFmpeg version, deterministic input filters,
encoder options, durations and hashes of the three 200-second source files.
Regenerate them with `tools/audio_test_server/generate_stress.py --seconds 200
--codec mp3 vorbis opus --output <new-directory>` using the recorded encoder
version. The source is synthetic; these evidence folders contain no music PCM.

The paced device runner uses `diagnostic.py run --suite load --load-seconds 180
--load-idle-recovery` with the generated fixture manifest and those three case
names. The control adds `--unpaced-files` and uses `--load-seconds 60`.
Supply the board/server addresses, passive serial port, exact SDK configuration
and a fresh output directory as described in the main testing document. The
board must be awake and installed image identity must match the report.

Run `python tests/test-esp32c3-receive-credit-evidence.py` to verify retained
hashes, time-window summaries, original failures, heap-recovery decisions and
the unchanged acceptance gates on the successful control. It makes no network
requests or hardware changes. `manifest.json` hashes every retained evidence
file except itself.
