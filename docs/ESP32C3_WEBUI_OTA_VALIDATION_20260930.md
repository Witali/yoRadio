# ESP32-C3 OLED WebUI application OTA validation — 2026-09-30

## Scope and compatibility

Source: `ab56a923e1ff8bc5f1d92fa7d03e88a8aaff2ec4`, ESP-IDF v6.0.2.
Target: ESP32-C3 SuperMini 0.42-inch OLED, 4 MiB flash, internal RTC oscillator.
No external 32.768 kHz crystal is installed on the test board.

The reference is the original Arduino implementation in
[`netserver.cpp`](../yoRadio/src/core/netserver.cpp), including its `/update`
upload handler and success response, and the existing native ESP8266 receiver
in [`web_upload.c`](../esp8266/rtos-sdk-native/main/web_upload.c).
The C3 uses the same shared `updform.html.gz`, styles and `script.js.gz` as
Arduino/CYD and ESP8266. It advertises application-only OTA, as native ESP8266
does; Arduino/CYD retains both firmware and SPIFFS choices.

The shared JavaScript is also embedded in the C3 application, so OTA installs
the compatible upload logic without replacing the user's SPIFFS files.
`POST /update` accepts `updatetarget=fw` or `firmware`, then one `update` file.
Success is HTTP 200 with plain `OK`. Failures restore the form for another try.

## Host validation

- 164 passing Node tests: C3 regressions, shared WebUI, native ESP8266 WebUI.
- Executed the actual C3 OTA parser and HTTP handler with fault-injected SDK
  calls: stream chunk sizes 1–600 bytes; truncation at every request offset;
  binary payload and boundary lookalikes; wrong chip/project; duplicate file;
  unsupported target; overflow; flash begin/write/end/metadata/activation
  failures; timeout and disconnect; reboot task allocation failure; activity
  lease ownership; response failure after boot selection.
- Tested the shared JavaScript in a DOM/XHR model for Arduino/CYD, native
  ESP8266 and C3: target choices, multipart fields, progress, rejection,
  network error, abort, timeout, retry and C3 keep-awake polling.
- Executed the RTC wake-stub tests. The linked deep-sleep build uses 3,704 of
  8,192 RTC bytes; all nine external dependencies remain RTC/ROM/GPIO accesses.
- Both production application images built successfully and fit the existing
  1,900,544-byte app slots. Neither contains the known board Wi-Fi SSID/password
  values in UTF-8 or UTF-16LE. Private backups are excluded from Git.

Reproduce the host checks from the repository root:

```text
node --test tests/esp32c3-*.test.js tests/webui-*.test.js tests/esp8266-webui-repair.test.js
python3 tests/run-esp32c3-ota.py
python3 tests/run-esp32c3-deep-sleep-clock.py
```

The Python runners require a host C compiler; on Windows run them in WSL.

## Physical board validation

The installed firmware initially lacked an OTA handler. A private 4 MiB backup
was made, then the initial OTA-capable application was written over USB to
`app0` only. NVS, otadata and SPIFFS matched their backups byte for byte before
the application restarted. The watchdog-reset skill verified HTTP startup.

Subsequent application installations used the same multipart `/update`
endpoint as the WebUI. The running partition and application ELF SHA-256 were
checked after each reboot; HTTP 200 alone was not considered success.

| Upload | Result |
| --- | --- |
| Bootstrap → ordinary OTA build | `app0` → `app1`, verified version and full ELF hash; about 17 s including reboot. |
| Ordinary → deep-sleep OTA build | `app1` → `app0`, verified deep-sleep ELF hash; about 18 s including reboot. |
| Slow deep-sleep OTA, screensaver disabled | `app0` → `app1`, about 26 s upload / 33 s including reboot. |
| Slow deep-sleep OTA, clock enabled with 20 s timeout | `app1` → `app0`, about 26 s upload / 32 s including reboot; active upload prevented sleep. |

After these two OTA installations, esptool verified **all NVS and SPIFFS bytes**
against the pre-OTA snapshot. Wi-Fi and playlist contents also matched their
HTTP readback hashes. Bootloader and partition table were not updated.

The following ten negative cases preserved the active application:

| Case | Result |
| --- | --- |
| Wrong chip ID | HTTP 400, board-specific file instruction. |
| Wrong application project | HTTP 400, board-specific file instruction. |
| SPIFFS target | HTTP 400, use Board file importer. |
| Request exceeding slot plus multipart allowance | HTTP 400 before flash writing. |
| Truncated image | HTTP 400, image verification failed. |
| Corrupted image | HTTP 400, image verification failed. |
| Extra byte after valid application | HTTP 400, image length mismatch. |
| Missing final multipart boundary | HTTP 400, incomplete upload. |
| Client disconnect after partial send | No boot selection; next status request succeeded. |
| Sender stalls after partial send | HTTP 400 after the idle deadline, about 11 s. |

An initial early-rejection test exposed a TCP reset hiding the server's error.
The receiver now disables Nagle buffering for the response, sends FIN and
drains incoming data for at most 250 ms before closing. Repeating the tests
confirmed delivery of the specific rejection messages.

The first unpaced slow-send test client encountered `ECONNRESET`, without
changing the active image. A revised client waited for TCP backpressure before
sending the next block. Both subsequent slow tests passed, including with the
clock enabled; the precise cause of that initial reset was not established.

After the final OTA, seven requests to the Update page's `/api/native/ota`
keep-awake endpoint kept the stopped radio reachable for 35.9 seconds, longer
than its 20-second clock timeout. Original screen settings were restored:
screensaver enabled, Clock (not Blank), timeout 20 seconds. The final installed
application is the deep-sleep build in `app0`. No external RTC crystal is used.

## Limits of this validation

- Hardware uploads were made with an HTTP client using the WebUI's exact
  multipart contract. The browser automation runtime failed to start, so
  browser rendering and manual clicking were not visually verified here.
- Automatic first-boot rollback is not enabled; no bootloader migration,
  deliberate power-cut test or recovery from a bootable crashing image was
  performed. The existing USB recovery route remains necessary in that case.
- A downgrade to a firmware predating OTA removes its OTA handler; this was
  not installed during validation.
- This change preserves the approved clock renderer. It does not claim to
  resolve or visually revalidate the previously reported partial OLED screen
  during deep sleep; see the earlier hardware validation report.
