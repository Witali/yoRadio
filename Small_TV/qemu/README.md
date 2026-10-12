# Small TV QEMU validation

An experimental `esp32c2` machine and its Windows launcher have been added to
`C:\Work\QEMU-ESP32` on branch `codex/esp32c2-small-tv`. See that repository's
`README-small-tv-esp32c2.md` for build, launch, reset, screenshot and GDB commands.
The tested model commit is `2fbfbf8756`; binary and firmware checksums are recorded
in [validation.json](validation.json) and the individual reports.

| Firmware | Verified result |
|---|---|
| Factory 4 MiB dump | Real ROM and IDF v5.5.4 boot; first draws `Connecting to WiFi`, version `0.0.2`, then the `Small_TV / 192.168.43.1` setup instructions |
| Reconstructed firmware | Real ROM and pinned ESP-IDF boot; `app_main` completes, AP DHCP starts, clock and JPEG animation draw |
| Existing C3 production firmware | Its OLED radio UI still renders with the same final QEMU binary |

Both C2 images ran for 30 seconds, displayed content at 240×240, reported no
panic/watchdog failure, and booted again after a QMP reset. The reconstructed
animation changed between captured frames. A separate run of the combined test
wrapper repeated the checks for 10 seconds per variant. Source artifact and base
flash hashes stayed unchanged. The saved UART logs belong to that shorter wrapper
run; the main JSON reports and screenshots belong to the 30-second runs.

The factory firmware reaches its **Wi-Fi setup screen**. The reconstruction is **waiting
for time synchronization**, while its offline UI and animation work. These are
successful boot/display tests, not successful Internet, SNTP, weather or HTTP
tests. C2 Wi-Fi MAC packet DMA is not implemented; there is no simulated AP/NAT
path, and the guest AP's `192.168.43.1` is not reachable from the host. No physical
board was flashed, reset or otherwise accessed during these tests.

| Factory firmware | Reconstructed firmware |
|---|---|
| ![Factory connection screen](original.png) | ![Reconstructed clock and animation](reconstructed.png) |

## Run or control the VM

```powershell
Set-Location C:\Work\QEMU-ESP32
.\run-small-tv-esp32c2.ps1 -Firmware original -Display none
.\run-small-tv-esp32c2.ps1 -Firmware reconstructed -Display none
.\run-small-tv-esp32c2.ps1 -Firmware reconstructed -Action screenshot
.\run-small-tv-esp32c2.ps1 -Firmware reconstructed -Action status
.\run-small-tv-esp32c2.ps1 -Firmware reconstructed -Action reset
.\run-small-tv-esp32c2.ps1 -Firmware reconstructed -Action stop
.\test-small-tv-esp32c2.ps1
```

The default snapshot mode isolates guest flash writes in QEMU. `-Persistent`
retains writes only in a working copy under `.cache/`; the original dump and our
archived binaries are never used as writable drives. Each variant has a separate
state directory and a localhost QMP endpoint. The automated verification used
`-Display none` and framebuffer captures. The Windows setup enables the SDL2
backend for visible LCD windows.

## Differences that the C2 model needs

- C2 ROM is 576 KiB, with the correct DROM alias and ROM data initialization
  templates; it is generated from Espressif's genuine revision-2 ROM ELF.
- SRAM is 272 KiB including the 16 KiB cache; C3's larger RAM and RTC RAM mapping
  are not carried into the C2 machine.
- C2's fixed PMPADDR3–15 regions must exist before ROM/bootloader execution;
  PMP state must also be cleared on reset.
- The MMU has 64 entries and a different invalid bit. Both firmwares configure
  64 KiB pages; the model also reads the C2 page-size configuration register.
- C2 has 43 interrupt sources, different matrix register offsets, one GDMA
  channel pair, and different RTC register offsets.
- With a 26 MHz crystal, SYSTIMER runs at 10.4 MHz and APB at 40 MHz. Reusing a
  fixed 16 MHz SYSTIMER would skew software time and delays.
- ST7789 uses SPI2 FIFO/DMA, GPIO5 D/C and GPIO1 Reset. GPIO18 LEDC duty controls
  average display brightness using the inferred active-low mapping. The virtual
  LCD remains selected because the firmware configures `CS=-1`; this does not
  establish the physical board's CS wiring.
- C2 analog calibration and MAC-reset handshakes need different register
  addresses. Compatibility completion flags allow startup; they do not simulate
  analog measurements or provide Wi-Fi packet transport.

These observations explain emulator compatibility and supplement the existing
firmware analysis. SPI waveforms/GPIO-matrix electrical routing, Bluetooth, SD,
ADC, power consumption, low-power modes, security features and complete machine
snapshots remain outside this validation. Hardware specifications can be checked
against the [Espressif ESP8684 datasheet](https://documentation.espressif.com/esp8684_datasheet_en.html)
and the ESP32-C2 headers of our pinned ESP-IDF source.
