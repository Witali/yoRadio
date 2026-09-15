# ESP32-C3 OLED deep-sleep clock — development firmware

Production build from source commit `66626be7879f8a1002f7ef478a229ce57d223138`, ESP-IDF v6.0.2.
Application version: `v0.9.693-770-g66626be7`.

- Image: `app.bin` (1318576 bytes).
- SHA-256: `05d397215be054c994a8b0bc9e821c6810b624c3ece500bada559d620d5fb462`.
- RTC timer: 500 ms; wake code and data: 3712/8192 bytes including reserved memory.
- Build, host wake-stub tests, 89 C3 regression tests and ELF audit passed.
- Not flashed or measured on the physical board.

Build from the worktree root:

```powershell
.\idf\esp32c3-oled-native\build-production.ps1 -DeepSleepClock -DependencyRoot C:\Work\yoRadio\.idf
```

Enable the stopped-radio **Clock** screensaver in WebUI. Sleep begins after
its timeout once the time is synchronized. Wi-Fi/WebUI/USB are unavailable
asleep. Hold BOOT for over 500 ms to restore the station screen, release,
then press again to play. Short presses may be missed. Blank and playing
screensavers retain their usual behavior.

See [implementation, usage and hardware checks](../../../docs/ESP32C3_DEEP_SLEEP_CLOCK.md).
This is a replaceable development artifact, not a versioned release.
