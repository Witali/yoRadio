# ESP32-C3 experimental 200 MHz profile

The ESP32-C3 datasheet specifies a maximum CPU frequency of 160 MHz. Its
documented clock tree exposes only 80 and 160 MHz when the CPU is sourced from
BBPLL. This profile is an isolated diagnostic image and is not part of the
normal radio firmware.

## What the profile does

idf/esp32c3-oled-native/build-overclock.ps1 builds a minimal image without
radio, Wi-Fi, WebUI, SPIFFS, audio, or display tasks. It temporarily:

1. starts from the supported 480 MHz BBPLL / 160 MHz CPU configuration;
2. arms the RTC watchdog for a system reset;
3. moves the CPU to the 40 MHz crystal;
4. programs the BBPLL midpoint parameters for approximately 400 MHz;
5. selects the divider used by the documented 320 MHz / 160 MHz mode, yielding
   an expected CPU clock near 200 MHz;
6. measures CPU cycles for 100 ms against SYSTIMER's crystal-derived 16 MHz
   reference;
7. restores the official 480 MHz BBPLL / 160 MHz CPU configuration before
   printing the result.

The 400 MHz table is not documented for ESP32-C3. The profile derives the
DIV_7_0=6 midpoint from Espressif's 320 MHz (4) and 480 MHz (8) C3 tables and
the 400 MHz table used on related Espressif clock hardware. This is an
experiment, not a supported operating point.

## Build and flash

    cd idf\esp32c3-oled-native
    .\build-overclock.ps1
    .\build-overclock.ps1 -IdfArguments @('-p', 'COM9', 'app-flash')

Use app-flash only. Do not write the partition table or SPIFFS: the profile
does not need them, and leaving them untouched preserves the radio settings and
WebUI. Monitor at 115200 baud after the hard reset.

The image never starts the experiment automatically. Open the serial monitor,
boot the image normally, and only then press and release BOOT to start. If the
CPU hangs, the RTC watchdog requests a full RTC-domain reset. After a normal
boot the retained result is printed; press BOOT again only for an intentional
rerun.

## Result on the tested board

On the tested ESP32-C3 revision 0.4 (40 MHz crystal), the derived 400 MHz BBPLL
configuration did not reach the measurement return path. USB Serial/JTAG
remained enumerated but neither the watchdog nor USB/JTAG reset restored ROM
communication. Recovery required a physical power cycle into the ROM loader,
after which the production app was restored. Therefore 200 MHz is **not a
working operating point on this board with these PLL parameters**, and the
240 MHz selector must not be attempted.

## Limitations

- A successful 100 ms measurement proves only that this individual chip
  executed that short workload. It does not establish long-term stability.
- USB Serial/JTAG can disappear during the 400 MHz BBPLL window. Output is
  printed only after restoring 480/160 MHz.
- Wi-Fi, flash timing, audio, temperature, and supply-voltage margins are not
  validated by this profile.
- Success near 200 MHz does not imply stability at the reserved 240 MHz CPU
  selector.
- Never use this profile as the production radio image.
