# ESP32-C3 OLED hardware validation — 30 September 2026

## Scope

A physical ESP32-C3 SuperMini / 01Space-style 72x40 OLED board with 4 MiB flash
was used to check the [beginner guide](ESP32C3_BEGINNERS_GUIDE.md). The board has
no external 32.768 kHz crystal. No crystal-enabled image was flashed.

The test PC already had Git, PowerShell and a reusable ESP-IDF toolchain.
A new Python virtual environment was created for esptool. This was not a
clean-Windows installation test.

Tools: PowerShell 7.6.5, Python 3.13.14 and esptool 5.3.1 for prebuilt flashing;
ESP-IDF v6.0.2 and its Python 3.12 environment for source builds.

## Results

| Guide operation | Result and evidence |
| --- | --- |
| P2: install esptool | Passed in a newly created virtual environment with `esptool==5.3.1`. |
| P3: obtain and check binaries | Targeted Git LFS download, manifest hashes and `image-info` passed. |
| P4: identify USB device | Native USB Serial/JTAG identified by VID 303A / PID 1001; chip and 4 MiB flash read successfully. |
| P5: first prebuilt installation | Ordinary production application plus all four shared installation files written at the documented offsets; esptool verified the writes. |
| Step 9: boot and AP setup | Watchdog recovery script completed; the AP served its setup page at `192.168.4.1`. The fresh SPIFFS image had no `wifi.csv`. |
| Step 9: save Wi-Fi | The actual setup form endpoint accepted credentials from a private backup, restarted the board and connected it to the local network. HTTP and status API returned successfully. |
| Web assets and controls | Index, JavaScript, CSS and playlist returned HTTP 200; compressed assets decoded successfully. WebSocket screen/time settings and stop commands worked. |
| P6: prebuilt application update | Production-to-development update passed. NVS and SPIFFS were verified against pre-update copies byte for byte before boot; Wi-Fi and playlist remained available afterward. |
| Source setup/build | Setup completed using the existing dependency directory. Production builds with deep sleep off and on both succeeded, with external crystal off. |
| Step 11: source `app-flash` | Build script wrote and verified the application; watchdog reset restored HTTP access. |
| Step 10: deep-sleep clock | Failed OLED validation: user observed station content on the left and minutes on the right. USB and HTTP became unavailable during sleep, as expected, but this does not validate the display. |

The user confirmed a station screen after Wi-Fi setup. The API reported AAC
44 kHz stereo playback; audible sound was not independently checked.

## OLED defect

The archived `esp32c3-oled-native-deep-sleep-clock` application from `66626be7`
showed an incomplete transition from radio to clock. A candidate built from
`9a5bd70c`, which changed the RTC writer to page addressing, passed host tests
but reproduced the same visual defect on the board. It is not a validated fix.

Use an ordinary firmware variant, or build with `DeepSleepClock = $false`,
while the regression is being investigated. Do not treat successful compilation,
esptool verification or disappearing USB as proof that the sleeping clock works.

## Limits

- Installers on a freshly installed Windows PC were not tested.
- The source-build `flash` command has not yet been exercised in this run.
- Browser rendering and mouse/touch interaction were not visually checked;
  the WebUI checks above used its real HTTP and WebSocket endpoints.
- External-crystal variants and the historical Arduino/I2S firmware were not
  hardware-tested.
- Clock drift and power consumption were not measured.

## Private data

The original 4 MiB flash was backed up before writing the board. Full backups,
Wi-Fi credentials and credential-bearing filesystem images remain in ignored
local directories and are not firmware distribution artifacts. Shared first-install
files contain public WebUI/playlist data and no Wi-Fi credential file.
