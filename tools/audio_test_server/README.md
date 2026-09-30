# Shared audio test server

This server works with ESP32-C3, ESP8266, CYD and other HTTP audio players.
It only serves original synthetic fixtures; it never controls or flashes a board.

```powershell
python tools/audio_test_server/server.py --host 0.0.0.0 --port 8770
```

Open `http://PC_LAN_IP:8770/manifest.json` for names, layouts and hashes. Give
any player `http://PC_LAN_IP:8770/file/mp3-320` or another listed fixture URL.
The HTTP server needs only Python's standard library. Optional HTTPS uses
`--cert`/`--key`; each board applies its own normal certificate validation.

Routes: `/file/NAME` (finite), `/stream/NAME` (continuous ADTS AAC),
`/drop/NAME`, `/stall/NAME`, `/error/NAME`, `/redirect/NAME`, `/jitter/NAME`.
No arbitrary local paths are exposed. FLAC and Ogg files are not concatenated
to pretend they are continuous streams.

Generate additional continuous files with FFmpeg/FFprobe:

```powershell
python tools/audio_test_server/generate.py --output .build/audio-60s --seconds 60
python tools/audio_test_server/server.py --fixture-manifest .build/audio-60s/manifest.json
```

Use `--codec`, `--rate`, `--channels` to select the matrix. Manifest output
layouts come from FFprobe, including Opus's 48 kHz decoded rate. The existing
FDK fixtures cover HE-AAC/v2; the generator's native AAC encoder produces LC.
Large soak fixtures belong in ignored `.build/`, not versioned firmware.

C3-specific control, verification and the complete test plan are documented in
[ESP32C3_TESTING.md](../../docs/ESP32C3_TESTING.md). Other boards can reuse this
server with their own playlist/WebUI or test controller unchanged.
