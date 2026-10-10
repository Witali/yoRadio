# Quiet production QIO 80 MHz deployment, 8 October 2026

Read `docs/ESP32C3_PRODUCTION_QIO80_20261008.md` for configuration and scope.
The application and matching bootloader are saved in
`firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/`.

- `build.ps1` and build logs record the fresh production build.
- `quiet-audit.json`, `verify-aac.json` and `verify-http.json` record build/link
  checks. They are not hardware performance qualification.
- `physical/flash-verification.json` confirms programmed bytes and unchanged
  settings partitions; `installed.json` records the initial identity and
  in-memory settings comparison.
- `physical/http-smoke/report.json` retains twelve completed PASS cases.
- `physical/checks-skipped.json` records the user's request to stop remaining
  tests. The HTTP matrix is incomplete and the OTA roundtrip was not started.
  Runtime/status captures normally flushed at suite completion are unavailable
  because the controller and its test child were terminated on request.
- `physical/final-board.json` confirms the production identity and resumption
  of the stored station after the interrupted tests.
- `source-index.json` and `index.json` authenticate the saved source and
  evidence bytes. Private Flash backups, Wi-Fi/playlist snapshots, audio
  fixture contents and keys are excluded.

`deploy.py` is the exact installation controller prepared for this specific
board and local fixture origin. Its planned test sequence was interrupted;
the presence of a step in the script does not mean it ran. It is not a generic
flasher, and its fixed prerequisites must be reviewed before reuse.

The quiet image has no CPU/heap diagnostics or Flash-mode boot probe. The
earlier DIO/QIO laboratory report remains the source for those measurements,
including its unsuccessful heap checks. This deployment does not promote the
whole production acceptance status to PASS.
