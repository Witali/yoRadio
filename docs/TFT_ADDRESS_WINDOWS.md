# Pixel address windows on ST7789 and ILI9341

Both controllers can receive a rectangular block of pixels as one continuous
stream. Set the window once, start memory write, and send its pixels; the
controller advances the address and moves to the next row automatically.
No command is needed at each row boundary.

| Command | ST7789 | ILI9341 | Parameters |
| --- | --- | --- | --- |
| `0x2A` | CASET | CASET | Start and end column, two bytes each |
| `0x2B` | RASET | PASET | Start and end row/page, two bytes each |
| `0x2C` | RAMWR | RAMWR | Pixel data follows |

For example, with ordinary horizontal addressing, a 3×2 window at `(10,20)`
has inclusive bounds `x=10..12`, `y=20..21`:

```text
command 2A; data 00 0A 00 0C
command 2B; data 00 14 00 15
command 2C; data P0 P1 P2 P3 P4 P5
```

The first three pixels fill the first row; the next three fill the second.
In RGB565 each `P` is two bytes, so this rectangle needs 12 pixel-data bytes.
The MCU still supplies every pixel, including repeated colors for a solid fill.
`MADCTL` rotation/mirroring determines the physical traversal; module offsets,
color format and byte order must match the selected panel configuration.
Send exactly `width × height` complete pixels for the intended rectangle.

This behavior is specified in the manufacturer datasheets:
[Sitronix ST7789V, §8.12 and §9.1.20–22](https://files.seeedstudio.com/wiki/Grove-1.2inch-ips-display/ST7789V_SPEC_V1.2.pdf)
and [ILI Technology ILI9341, §8.2.20–22](https://www.olimex.com/Products/ARM/ST/STM32-LCD/resources/ILI9341.pdf).
These are manufacturer documents hosted by display/board suppliers.

## Current native CYD implementation

[cyd_display_draw_bitmap()](../idf/esp32-cyd2usb-native/main/cyd_display.c)
already uses this facility through `esp_lcd_panel_draw_bitmap()`. The pinned
ESP-IDF 6.0.2 ST7789 driver sends CASET, RASET and RAMWR, then submits the whole
rectangle to SPI DMA. The SDK API uses exclusive end coordinates; the wrapper
passes `(x, y, x + width, y + height)`, and the SDK subtracts one for the
controller's inclusive end registers.

`cyd_display_clear()` submits multirow strips using the available DMA buffers.
The strip size controls RAM usage; it does not require per-row commands.
Pixel storage must remain valid until its DMA transfer completes; use the
display buffer acquisition/completion API and flush before releasing storage.

The native CYD firmware selects ST7789. The shared window-command mechanism
also applies to ILI9341 hardware, but its initialization, color/byte-order
settings and exact board wiring require its own driver configuration.
