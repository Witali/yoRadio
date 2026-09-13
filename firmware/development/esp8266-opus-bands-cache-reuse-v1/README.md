# Rejected experiment: Opus ASM PVQ cache reuse

This is a **raw decoder benchmark**, not an ordinary radio image. Do not use
it as the production/default firmware. Native app OTA only; no SPIFFS image
or partition change is involved.

- Image: 903232 bytes, SHA256
  `a3110a46703df7a543616619d27c957c574de72e7baf1a854e98bc2194faf463`.
- Best tell-inline parent; same CPU160/QIO40, features, fixtures and RAM.
- 53 Node tests, host PCM/PLC/reset/OOM and 320/510-kbit/s compatibility PASS.
- Ten A, ten B, ten repeated A runs: CPU192 88.135 / 92.242 / 88.165%.
  All exact PCM, no decoder errors; candidate is slower and remains disabled.
- Ordinary radio restored by OTA; see `ota-restore.json` and
  `restored-snapshot.json`. Device left stopped as before the test.

`comparison.json` contains distributions, maximum calls, heap/stack results,
profile checks and exact fixture hashes. `controls/` and `runs/` contain all
30 original JSON/log pairs, without discarded outliers. `preflight.json`
contains the linked instruction graphs and RAM/flash map. The firmware
manifest pins the recipe built from the worktree; its pre-build HEAD is
`99a12b5c`, and that implementation was subsequently committed as `e0157c50`.

[Full explanation](../../../docs/ESP8266_OPUS_ASM_CACHE_REUSE.md)
