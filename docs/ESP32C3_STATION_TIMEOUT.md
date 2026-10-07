# ESP32-C3 station availability timeout

## User setting

In **Settings → System**, set **station unavailable timeout (seconds)**.
The range is **1–120 seconds**, with a **10-second default**. The value is
stored in NVS and survives reboot and application OTA. It takes effect on the
next station start; it does not change a connection attempt already in progress.

The field is added to the shared WebUI only when the firmware advertises
`stationtimeout` in its `getsystem` response. Other boards retain their existing
interface. The C3 embeds the updated script in its application image, so this
upgrade does not require a SPIFFS upload or replacement of Wi-Fi/playlist files.

With Audio watchdog enabled, transient connection failures can retry within
the chosen time window. Pauses increase from 1 to 2 to 4 seconds, up to 30
seconds for longer configured windows, and never extend the deadline. The
default ten-second window allows immediate failures at approximately 0, 1, 3
and 7 seconds. At the deadline, the state becomes **`station unavailable`** and
automatic attempts stop. A new Play or station selection starts a fresh window.

Stop, another station, or disabling the watchdog cancels a pending retry.
Watchdog off disables automatic retries. Permanent request errors, such as
401/403/404, terminate without repeated requests. Finite files retain normal
EOF behavior; decoder failures are not turned into connection retry loops.

For an established stream, the same configured interval controls the watchdog
for missing compressed audio data. Already queued PCM drains before the
unavailable terminal status. Backpressure from a full PCM queue does not create
a new connection attempt. The network reader still polls at 250 ms; this setting
does not increase that polling interval or the decoder's input wait.

The stopped state and error text are published to REST and WebSocket clients.
The OLED also shows the error even when Audio info is disabled. Normal stopped
playback retains its empty secondary row. Existing clock/screensaver behavior
continues after idle time.

## Implementation and memory

The stream task retains its existing play command while waiting, without a
second URL buffer, a new task or timer allocation. It closes and cleans up the
HTTP/TLS client before each backoff. A new command wakes the queue immediately;
Stop/watchdog changes are checked at most every 100 ms during backoff.

HTTP connection, response headers and redirects share the connection deadline.
Each blocking API receives the remaining time, and a late success is rejected.
The deadline is checked again before opening a client and while waiting for
the previous decoder to release its resources. These are task-level checks;
they cannot forcibly interrupt an SDK call that does not honor its timeout.

The NVS key is `runtime/stationtimeout` (unsigned byte). Missing or out-of-range
saved values retain the default. WebSocket accepts only whole seconds in range;
invalid text does not get narrowed into an accepted byte value. A failed NVS
write does not update the in-memory setting.

The awake test image preserves all existing codec/storage configuration and
stream/decoder/output priorities 5/7/8. IRAM remains 43,354 B, data 12,620 B and
BSS 29,464 B. Application size is 1,581,552 B, **2,432 B larger** than the ordinary
priority-8 image. The small retry state lives on the existing stream task stack.
Codec sample rates, arithmetic and PCM samples are unchanged.

## Verification

Native sanitizer tests execute the actual HTTP-open and stream-task code with
deterministic RTOS/transport stubs: 35 scenarios cover transient/permanent
errors, resource lifetime, cancellation, EOF, stalled data, 1/2/10/120-second
deadlines, and a response arriving too late. The EOF regression additionally
executes the real terminal-marker/state operations after buffered HE-AAC PCM.

The shared recovery server serves `/recover/FIXTURE`: it first returns a chosen
number of empty 503 responses, then the exact finite fixture bytes. It is usable
by ESP32-C3, ESP8266, CYD or any HTTP audio client. Only the C3 runner controls a
board. Example:

```text
python tools/audio_test_server/server.py --host PC_LAN_IP --initial-failures 2
python tools/esp32c3_tests/connection_retry.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM_PORT --firmware firmware/development/esp32c3-station-timeout/app.bin --output NEW_DIRECTORY
python tests/run-stream-connection-retry.py --output NEW_HOST_DIRECTORY
node --test tests/webui-station-timeout.test.js tests/esp32c3-native-idf.test.js tests/esp32c3-memory-stability.test.js
```

The physical test includes recovery with AAC-LC and HE-AACv2, EOF without
restart, watchdog off, Stop, station switching, disabling a pending retry,
3/10-second unavailable deadlines, a stalled stream, invalid setting rejection,
reboot persistence and settled heap recovery. Wi-Fi/playlist/settings snapshots
stay in RAM and are compared after restoration. Reports preserve failures.

Measured physical outcomes and exact image/source identities are retained in
`tests/results/esp32c3-station-timeout-20261007/`. These checks cover connection
availability, not broad codec/TLS qualification or physical audio continuity.

### Physical results, 2026-10-07

The final awake image (`0117c66082ec`, full ELF SHA-256 in the manifest) passed
all **15 recorded checks** and remains installed on the board. Both application
OTA transitions passed; the upgrade introduced the default of 10 seconds while
preserving existing settings, Wi-Fi and the playlist.

| Check | Observed result |
| --- | --- |
| Ordinary firmware before the change | One 503 request, no recovery; expected baseline failure retained |
| AAC-LC 48 kHz stereo / HE-AACv2 44.1 kHz stereo | Two 503 responses, then playback; finite EOF did not restart |
| Timeout set to 3 seconds | Unavailable observed at 3.297 s; two requests, none after the deadline |
| Timeout set to 10 seconds | Unavailable observed at 10.422 s; four requests, none after the deadline |
| Connected stream stalls | Stops with `station unavailable` using the 3-second setting |
| Cancellation | Stop, another station and disabling watchdog cancel pending retries |
| Persistence and validation | 3 seconds survives software reboot; six invalid values rejected |
| Settled heap before / after | Median 147,702 / 147,972 B; largest block 114,688 B; 17 tasks in both windows |
| Final restored state | Saved station playing AAC PCM 44.1 kHz stereo; timeout 10; served WebUI script matches the artifact |

The observed times include status polling and are not a measurement of the
exact internal deadline. The first full run passed its functional checks but
reported the intentional persistence-test reboot as an unexpected reset. That
failed report is retained unchanged. The corrected runner permits only the
recorded software-reset banners inside the requested reboot interval; other
resets, panics and allocation/decoder errors still fail. The repeat passed.

The final host stream test passed 35 sanitizer scenarios, the EOF regression
passed, and the WebUI/native tests passed 50 checks. A live browser preview was
unavailable because the automation runtime failed to start. The UI control was
tested by executing its JavaScript, checking the served asset and exercising
the real WebSocket setting; browser layout and OLED appearance were not
visually verified. These results do not qualify the image for every codec,
TLS failure or uninterrupted physical audio output.
