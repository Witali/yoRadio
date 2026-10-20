# CYD playback acceptance tools

Stage CYD-C3-15 reuses the [shared synthetic audio server](../tools/audio_test_server/README.md)
and the existing C3 observation/playback checks. The controller is
[tools/cyd_tests/run.py](../tools/cyd_tests/run.py). It supports PDM, continuous
DAC and legacy DAC through an explicitly selected, saved production artifact.
It never flashes, uploads firmware, reboots or opens a serial port. OTA acceptance
is a separate controller and physical gate.

An implemented test, an executed test and a passed physical measurement are
different results. The tests described below qualify host controller behavior;
they do not establish playback on a board.

## Identity and public APIs

Supply a production `app.bin` with its original adjacent `manifest.json` and
`sdkconfig`. Before Play/Stop, the controller uses the existing production
exporter's complete ESP image parser: chip0, segment bounds, application
descriptor, segment checksum and complete image SHA are checked. The CYD project
must be `yoradio_cyd2usb_native`, with pinned SDK6.0.2 and exactly one matching
saved backend. App/config hashes, embedded ELF hash, version and manifest must
agree. Every playback write rechecks unchanged local files, live OTA metadata
and capabilities. The generic status value `esp-idf-native` alone cannot identify
the board, image or backend.

The controller reads `/api/native/status`, `/api/native/health`,
`/api/native/ota` and `/api/native/capabilities`. Playback uses existing
`POST /api/native/play?codec=...` and `/api/native/stop`. Only the implemented
WebSocket `getindex` snapshot is used by the WebSocket scenario. Settings are
compared in memory through CYD REST settings, time, network settings and radio
smartstart fields. Their values, station names, titles and credentials are not
written to reports. C3 screen/control queries and C3 reboot commands are not
part of this controller.

CYD `sample_rate_hz` and `pcm_sample_rate_hz` are normalized for the common
playback checks. AAC expectations retain exact fixture PCM rate/channels and
encoded hashes. CYD's public decoder reports `AAC PCM`, so the controller does
not invent a nominal HE/PS decoder profile tag. The default local matrix covers
existing AAC/MP3/FLAC and public vendor Vorbis/Opus fixtures. Finite HTTP/HTTPS
and EOF cases run both AUTO detection and the explicit codec hint. This uses the
already implemented public OGG dispatch; deferred private-bridge/Ogg target work
is not extended or qualified by these controller tests.

## Evidence and limits

Every status observation is paired with a native CYD health observation. Quiet
profiles retain heap/largest/minimum, internal/DMA heap, allocation/decoder/stream/
output faults, input ownership and native driver counters. Boot ID and uptime
detect observed restarts. CYD has no exported watchdog-event counter: reports
state that limitation and do not manufacture a zero. No UART is opened.

During decoded playback, the controller requires driver write/byte progress and
no new driver errors, timeouts or short writes. Counter saturation and decreases
fail; CYD counters are not interpreted with C3 modular arithmetic. Driver byte
counts include prime/idle traffic and backend expansion. Short-write/error
counts may overlap. They do not count audible clicks or prove analog continuity.
PDM completion-queue observations must be available during active playback;
pre-registration `null` is permitted. Continuous/legacy DAC keep queue drops
unavailable (`null`), which never becomes a fabricated zero.

Diagnostic profiles retain overall and both core CPU percentages, task percentages
relative to one core, stack minima and sample age. Quiet `null` measurements stay
unavailable. `--require-cpu` requires a diagnostic artifact and a sustained
load/soak scenario, allowing the sampler's startup interval. CPU/stack data are
observations rather than arbitrary C3 resource budgets. Keep stream core0 and
decode/output core1 bindings from the saved production profile.

Reports include exact app/config/manifest/test-source hashes, technical status,
health samples and controlled server delivery events. HTTPS additionally requires
negotiated TLS evidence from the owned fixture server. Socket writes do not prove
board reception or playback. Failed cases retain partial status/health and a
bounded diagnostic snapshot before cleanup. Cleanup failures remain separate
failed rows. Outputs must be fresh; old results are never overwritten.
KeyboardInterrupt, SystemExit and cancellation cannot produce PASS. Failed or
interrupted cases and partial evidence are saved before diagnostic requests and
Stop. A primary interruption and a cleanup interruption stay separate, and an
interrupted CLI exits nonzero (130 for KeyboardInterrupt).

## Offline checks

Run these host tests without a board. CYD tests inject all HTTP, WebSocket,
server and time behavior and explicitly reject real socket creation. They use
synthetic valid/corrupt ESP images and existing local fixture bytes.

```powershell
python -B -X utf8 tests/test-cyd-acceptance-tools.py
python -B -X utf8 tests/test-production-health.py
python -B -X utf8 tests/test-quiet-file-gates.py
python -B -X utf8 tests/test-sustained-output.py
python -B -X utf8 tests/test-esp32c3-acceptance.py
```

The CYD tests cover identity before writes, all three profiles, strict schemas and
unavailable observations, actual controller file/EOF/transition/Stop/switch/load/
soak/HTTPS/WebSocket paths, output progress/faults, snapshots, cleanup, fresh output
and report privacy. Existing C3 defaults and image rejection policy remain strict.
The original C3 acceptance regression additionally uses loopback-only HTTP/HTTPS
servers and a mock build wrapper, never a physical board or real SDK build.
Its HTTPS fixture requires the existing `cryptography` host dependency listed in
`tools/esp32c3_tests/requirements.txt`; use an already configured interpreter.
The shared C3 runner adds only package imports and an optional observation clock;
its normal script behavior is preserved.

## Physical commands, pending separate execution

First select and install a reviewed production image through the separately
authorized deployment workflow. This controller requires an initially stopped
board and finishes stopped; it does not restore a station by rebooting. Run the
matrix separately with the matching saved image for `pdm`, `continuous` and
`legacy`. These example commands have not been executed as physical acceptance.

```powershell
python -B -X utf8 tools/cyd_tests/run.py --board http://BOARD_IP --host HOST_IP --backend pdm --firmware firmware/development/esp32-cyd2usb-native-production-pdm/app.bin --suite http --suite eof --suite stop --suite switch --suite transitions --suite websocket --output .build/cyd-physical-pdm-files
python -B -X utf8 tools/cyd_tests/run.py --board http://BOARD_IP --host HOST_IP --backend pdm --firmware firmware/development/esp32-cyd2usb-native-production-pdm/app.bin --case lc-48000-stereo --suite load --suite soak --load-seconds 60 --soak-seconds 3600 --output .build/cyd-physical-pdm-sustained
```

The server binds `HOST_IP`; fixtures and SHA256 values come from the same checkout.
Use `--fixture-manifest` for a previously generated long finite MP3/FLAC/Vorbis/Opus fixture
that outlasts the observation. The default AAC stream repeats its original bytes.
OGG soak uses one sufficiently long standalone container through `/file`; raw
Vorbis/Opus containers are never repeated to imitate a continuous stream.
Delivery pacing is explicitly1.0. Load polls status+health every100ms, soak every
second. Memory recovery compares settled idle samples and persistent losses;
there is no arbitrary absolute free-RAM floor.

For controlled HTTPS, use a certificate/hostname normally trusted by the selected
image, with its private key kept locally. Certificate validation stays enabled.

```powershell
python -B -X utf8 tools/cyd_tests/run.py --board http://BOARD_IP --host HOST_IP --backend pdm --firmware SAVED_APP_BIN --suite https --https-origin https://CONTROLLED_HOSTNAME:8771 --tls-cert SERVER_PEM --tls-key LOCAL_PRIVATE_KEY --output .build/cyd-physical-pdm-https
```

The hostname must resolve to the controlled server from the board. Add
`--require-cpu` to a sustained command only with its matching saved diagnostic
artifact. Physical RF reconnect, watchdog coverage beyond sampled restarts,
DMA/IRQ timing, analog listening/loopback, OTA/data/power-loss behavior and the
full transfer-plan hardware matrix remain separate acceptance work.
