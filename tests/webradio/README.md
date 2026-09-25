# WebRadio tests

This directory contains tests specific to the Arduino ESP8266Audio `WebRadio`
firmware.

- `source.test.js` is part of the normal `npm test` run. It checks the pinned
  dependencies, build profile, Web API and playback diagnostics.
- `hardware-playback.mjs` is an explicit physical-board test. It serves the
  repository's 64 kbit/s mono MP3 and AAC fixtures over a local HTTP/1.0 stream,
  selects each URL through `/api/play`, and verifies that the decoder remains
  running while the I2S sample counter and HTTP byte counter advance.

The board and the test computer must be on the same network. Supply the
computer's LAN address explicitly when more than one network adapter is active:

```powershell
node .\tests\webradio\hardware-playback.mjs `
  --board http://192.168.100.6/ `
  --host 192.168.100.2
```

Optional arguments are `--port` (default `18080`) and `--duration-ms`
(default `8000` per codec). The URLs installed temporarily by the test are
`http://<host>:<port>/stream.mp3` and `/stream.aac`. The final `/api/stop`
leaves playback stopped; the last selected AAC URL remains in EEPROM.
