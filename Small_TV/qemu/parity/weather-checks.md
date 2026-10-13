# Weather decoding, field boundaries and scrolling

`src/tests/weather_render_oracle.py` executes the immutable factory BMP decoder
at `0x42010eca` and the current compiled `media_draw_weather`. Flash reads,
allocation and mutex calls are adapted; the actual header parsing, row selection,
RGB conversion, LCD windows and SPI pixel streams execute. All 18 public weather
icons are compared over the complete framebuffer, including each 60×60 icon.
JPEG calls remain recorded boundaries in this test.

The addressed BMP excerpt is
[`helper_at_42010eca.asm`](../../src/reference/assembly/helper_at_42010eca.asm).
Its range ends at `0x42011040`, after the final backward branch to the shared
epilogue. Instructions confirm flash entry `0x40392326`, allocation
`0x4038e4be`, release `0x4038e4da` and pixel blitter `0x4200950e`.

## Confirmed factory errors and field corrections

Factory `0x4200aefc` clears the city only through y=23, although its glyphs occupy
y=10…33. `0x4200b340` omits clearing the weather-title margins. `/updateCity`
invalidates the weather flag at `0x3fcc39d7` but retains the icon pointer at
`0x3fcc3aa8`; the renderer can consequently draw the obsolete icon.

The original centering limits affect the starting coordinate, rather than the
number of rendered characters. Long labels can enter neighboring fields. City
width is also narrowed to eight bits before centering. These behaviors are
deliberately corrected, with `FIXED_FACTORY` entry comments.

| Field | Clear/drawing bounds, exclusive right/bottom |
|---|---|
| City | Clear x=0…179, y=0…33; text window x=0…179, y=10…33 |
| Rotating description | x=0…179, y=40…63 |
| Weather title | x=160…239, y=83…106 |
| Weather icon | x=180…239, y=10…69 |
| Temperature/humidity | x=80…151, y=180…203 / 210…233 |

Missing weather clears the icon and title. A native BMP read failure clears the
entire icon, including partially decoded rows; successful retry restores it.
The test injects errors at the header, first, middle and last row reads of the
actual compiled decoder. Host tests additionally place guard pixels immediately
outside the clearing rectangles.

A pre-fix run on application
`3c60563a3d759d3973dd92b52d4a8f5fedd70ca00346214ed54ec8e61b7f2c78`
found 91, 182, 730 and 106 retained pixels in successive native frames compared
with a clean rendering. All 18 decoded BMPs already matched. That negative
report is retained as [negative evidence](weather-render-before.json), with its
own application and ELF hashes.

The current [machine report](weather-render-validation.json) retains literal
factory differences separately. An explicitly corrected factory reference extends
the city clear, clears title/invalid-icon bands, adjusts field centering and clips
already computed glyph pixels to the field. It does not modify the dump or mask
any comparison region. Native incremental frames must match both that corrected
reference and an independently initialized native rendering.

## Requested scrolling

Long city, description and weather-title fields scroll left and back independently.
Short strings remain centered. Each active display-loop step moves two pixels;
15 steps pause at each endpoint. The loop's nominal delay is 100 ms, so motion
is approximately 20 pixels/s with 1.5-second pauses, subject to decoding and task
execution time. Uploads and blocking weather work suspend this UI loop.

Content changes and theme re-entry reset the offset. Periodic status refreshes
preserve it. A long rotating description retains the pending description event
until its first complete outward/return trip; fitting descriptions retain the
factory cadence. This extension is marked `REQUESTED_CHANGE`, and is not claimed
to exist in the original firmware. Existing weather-parser length limits remain.

The oracle checks 191 actual RV32 scroll frames against independent phase
expectations and the original LSB-first font bytes, including all pixels outside
the three fields. Host tests cover sub-character clipping, opaque background,
unsplit temperature-unit pairs, invalid widths, panel-edge intersection, phase
reset, and the real production task during upload suspension/theme changes.

These checks model explicit status events and active scroll steps. Physical SPI
timing, concurrent scheduling, live weather service, JPEG decoder equivalence,
long-run memory and whole-program identity remain outside their scope.

## Real HTTP field transitions

`src/tests/field_qemu.py` boots both complete images and changes the city through
the actual `/updateCity` handler. A loopback service sends known weather bodies;
the original program and native worker parse those bodies themselves. The native
flow checks long city/title motion in both directions, endpoints and pauses,
shortened labels, unavailable weather, a successful retry and an unknown icon code.

Each accepted native city/title/icon frame matches independently decoded factory
fonts and BMP pixels, including four adjacent guard strips. The RGB565-to-RGB888
conversion follows the installed QEMU ST7789 surface's integer scaling. Transient
captures during SPI repaint are retried; complete expected fields are required.
QMP observations briefly stop/resume execution to read coherent state and pixels,
without modifying guest memory, registers or instructions.

A deliberately delayed service response must hold the complete framebuffer and
scroll state. After publication, the test waits until the renderer acknowledges
the new weather generation and checks that the existing scroll phase continues.
Switching to the simple theme and back must reset the phase to its initial pause.

The literal factory observations distinguish its different behavior: a city POST
can reinitialize the screen, so short-label ghosts seen in direct incremental
renderer calls are not assumed to appear in every HTTP flow. Failed weather still
redraws the obsolete icon when its retained pointer is nonzero. Unknown icon
selection and later recovery are recorded separately. The
[HTTP field report](../field-http-validation.json) contains source identities,
exact pixel differences and observed phases; scroll extensions are native checks.
