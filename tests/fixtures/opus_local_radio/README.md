# Own local-radio fixtures

Five-minute continuously encoded files, not concatenations of Ogg files or
loops of already encoded packets. Source is the repository's deterministic
tone/noise WAV (440/997Hz tones, chirp, seeded white/filtered noise and bursts).
The one-second source repeats before encoding. No recorded music is included.

- mono-24-60ms.opus: CBR24kb/s, hybrid mono,5001 packets of60ms,180B each.
- mono-12-20ms.opus: CBR12kb/s, SILK mono,15001 packets of20ms,30B each.

Final decoded duration after Ogg pre-skip/tail trimming is exactly300s.
Raw packet duration includes encoder delay/tail. Ogg headers add wire bitrate.
Manifest records source/output SHA256, encoder version and exact arguments.
Reproduction: tools/esp8266_opus_profile/generate_local_radio.cjs (refuses to
overwrite an existing output directory).

## LAN-only station

Run from repository root, using the PC's actual LAN address:

```
node tools/esp8266_opus_profile/local_radio.cjs --file tests/fixtures/opus_local_radio/mono-24-60ms.opus --host 192.168.100.253 --port 8765 --seconds 900 --tcp-info --output .build/NEW-server.jsonl
```

Only /buffered.opus and /live.opus are served. Both contain identical bytes,
Content-Length and Connection:close. Buffered mode fills TCP as permitted by
backpressure; live mode schedules complete Ogg pages by granules, with1s lead.
Each connection starts a new five-minute file. No chained looping is hidden.
No filesystem browsing, playlist/credentials uploads or adapter changes.
The listener automatically closes after the specified bounded lifetime.
TCP telemetry is optional and requires the existing native Node addon.

```
node tools/esp8266_opus_profile/run_local_station.cjs --url http://192.168.100.253:8765/buffered.opus --directory .build/NEW-test --windows 2
```

The board needs the diagnostic Opus URL and autonomous-window endpoints.
This command changes only current temporary playback. It waits65s without
board requests, reads a closed25s window, then reads RAM/status outside that
window. Failures remain in reports. This excludes the Internet, not Wi-Fi,
TCP scheduling, decoding or the PCM/PDM output path. It is not a CPU meter.
