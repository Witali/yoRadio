# ESP32-C3 OLED production-rtc32k — development firmware

- Source commit: `63572edf79803f6939a64c466f24ec1c3d79602a`.
- Application version: `v0.9.693-1012-g63572edf`; ESP-IDF v6.0.2.
- Profile: production (USB/logging disabled), `-Rtc32kCrystal`.
- Image: `app.bin`, 1305680 bytes; SHA-256: `088456e451611c896751771adb16d92cd57f142264fa0d146883d49d391b1889`.
- App0 flash offset: `0x10000` for the repository partition table.
- RTC: passive 32 768 Hz crystal between GPIO0/XTAL_32K_P and GPIO1/XTAL_32K_N;
  3000 calibration cycles, ESP-IDF fallback to internal RC on startup failure.
- Deep-sleep clock: disabled.

Build from the worktree root using PowerShell 7:

```powershell
.\idf\esp32c3-oled-native\build-production.ps1 -Rtc32kCrystal -DependencyRoot C:\Work\yoRadio\.idf
```

Validation: both production builds; all four switch combinations on one reused
sdkconfig (including deprecated aliases and generated compiler header);
89 C3 regression tests; 16 compiled GPIO conflict/valid-mapping cases;
actual wake-stub I2C/GPIO tests and two days of half-second RTC ticks at 32768 Hz;
RTC/ROM dependency audit of the combined deep-sleep/crystal image.
No flashing, physical crystal startup, current or accuracy measurements performed.

See [wiring and build instructions](../../../docs/ESP32C3_RTC_32K_CRYSTAL.md).
This is a replaceable development image, not a versioned release.
