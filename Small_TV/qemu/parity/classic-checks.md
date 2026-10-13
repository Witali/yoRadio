# Classic clock and animation checks

`src/tests/classic_oracle.py` executes the factory RV32 instructions and the
current compiled C ELF. The [saved report](classic-validation.json) identifies
both executables, the archived application and its source manifest by SHA-256.
Inputs are synthetic; the original flash dump remains unchanged.

The comparison covers 261 classic-clock field/media cases: positive and negative
temperatures, independent Fahrenheit and wind-unit switches, all ten description
steps, valid/missing weather, weekdays, date formats, 12/24-hour boundaries,
label lengths, calendar rollovers and incremental updates with retained pixels.
Every framebuffer pixel produced by the text/window algorithms is compared.
JPEG/BMP output calls are recorded by asset identity and coordinates; this check
does not decode media pixels. Decoder tests and whole-firmware QEMU captures
cover that separate boundary.

## Persistent animation cursor

Factory `0x4200b5cc` reads the selected GIF's real 1024-byte header and uses the
byte cursor at `0x3fcc3a24`. It advances after a frame and returns to zero at the
container terminator. Theme initialization at `0x42008e08`/`0x4200aebe` and GIF
selection at `0x4200d8b8` retain that cursor.

The earlier reconstruction used an unbounded render count modulo the frame
count and reset it on theme switches. For example, selecting a 15-frame GIF
after cursor 21 of a 25-frame GIF incorrectly selected frame 6; the factory
selects frame 0. `factory_animation_next` restores the factory cursor rule.

The machine test compares 1,545 transitions across all 25 pairs of the five
containers, every reachable cursor including the terminator, and three subsequent
frames. Three additional checks reject invalid native frame counts without
changing the cursor. The production clock-task test `clock_animation_selection`
also checks a shorter GIF and a simple-theme round trip; it failed before the
repair and passes with the restored cursor.

The flash adapter uses SDK entry `0x40392326`, confirmed by the executed
AUIPC/JALR pair at `0x4200b632`/`0x4200b636`. The ROM symbol with the same
`esp_flash_read` name is not the target of that call.

## Glyph clipping correction

Factory blitter `0x4200950e` rejects an entire rectangle if its right/bottom end
exceeds 239. In `Thunderstorm`, the last `r` begins at x=236: the literal factory
frame loses 17 visible pixels. Our `display_bitmap` retains those visible columns.

The report preserves this literal difference and separately compares a reference
that clips only this partially visible rectangle, using the bitmap already
computed by factory instructions. Fully visible blits still execute unchanged.
Four independent checks require the exact visible bits of the original `r`
bitmap at right/bottom boundaries. No comparison region is masked.

These checks establish the tested field, cursor and clipping behavior. They do
not establish every scheduling path, physical timing or whole-program equivalence.
