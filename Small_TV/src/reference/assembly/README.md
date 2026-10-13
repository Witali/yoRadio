# Factory instruction audit checkpoint

`manifest.json` records addressed disassembly and hashes of executable bytes
from the immutable factory dump. Exports end at the next known symbol and can
include alignment bytes; `helper_at_420a74e6.asm` is an excerpt of the rounding
helper. Only IROM is exported. Settings-sector contents and DROM credential
strings are excluded.

Direct instruction checks during the current work confirmed:

| Original address | C behavior checked or corrected |
|---|---|
| `0x4200826a` | Unsigned timer thresholds: 181 startup ticks, 11 ticks per timer second, 3 description seconds and 1801 weather seconds |
| `0x42008a34`, `0x42008a96` | RGB565 bit replication and RGB888 truncation/masks |
| `0x42008c4c` | Strict unsigned minute comparisons for night brightness; no SNTP-validity gate |
| `0x42008d62`, `0x42008bd2`, `0x42008c4c` | Zero-duty channel setup followed by explicit set/update, integer PWM mapping and no writes for unchanged scheduled brightness |
| `0x42009644`, `0x42009b32`, `0x420a74e6` | Float narrowing of atan2/tick angles and rounded offsets restored; the vendor's swapped sin/cos stroke pair deliberately corrected |
| `0x4200a5be`, `0x4200aa1e`, `0x4200acae` | Original glyph pointers, padded rows, LSB-first pixels, spacing and decorative dimensions |
| `0x4200afcc`, `0x4200b738`, `0x4200bd8c` | Conditional field updates instead of full-screen repainting |
| `0x4200b850`, `0x4200b0b2`, `0x4200bd8c` | Calendar changes ignored when time/event gates do not change; omitted simple date-band erase deliberately corrected |
| `0x4200b5cc`, `0x42008e08`, `0x4200aebe` | Byte GIF cursor, terminator restart and persistence across selection/theme changes |
| `0x4200950e` | Whole-glyph rejection at the panel edge; visible-column/row clipping deliberately corrected |
| `0x4200aefc`, `0x4200abee`, `0x4200b340` | Incomplete city clear, panel-only text bounds and uncleared weather-title margins deliberately corrected |
| `0x42010eca`–`0x42011040` | Both BMP decoders executed for all 18 icons; actual flash/allocation/release call targets and row conversion checked |
| `0x4200c33e`–`0x4200c578`, `0x42011040`–`0x42012092` | Real JPEG input/output, prepare/decomp and IDCT executed; byte clipping restored and ignored flash errors deliberately corrected |
| `0x4200bf9c` | The simple clock handles weekday 1..7 and repeats its date buffer for standard Sunday 0; this confirmed bug is corrected at the user's request |
| `0x4200bc36` | Six fade levels and photo replacement at duty 1000 |
| `0x4200fd94`–`0x4200fda0` | Kelvin subtraction followed by ROM `__fixdfsi`, truncating Celsius toward zero |
| `0x4200fe82`–`0x4201082c` | Half-open compass sectors and double comparisons |

Other exported functions remain reference material; exporting them is not a
claim that every execution path has been checked. The corresponding production
C comments retain verified addresses. Safety/privacy fixes and the ESP-IDF SDK
version difference are documented in `../../README.md`.

[Executable checks](../../../qemu/parity/machine-checks.md) now exercise
the simple and analog renderer instructions against the compiled C. The report
retains literal factory pixel differences and separately verifies the deliberate
Sunday and stroke-geometry corrections. It does not claim complete program or
timing equivalence.

[Classic execution](../../../qemu/parity/classic-checks.md) compares 261 field/media
cases and 1,545 animation transitions. Media output is a recorded boundary;
the partial-glyph correction retains the literal difference and has four
independent visible-bitmap checks.

[Control execution](../../../qemu/parity/control-checks.md) verifies every
counter/flag in four traces spanning 79,296 calls to `0x4200826a`, plus 13,440
fade/selection transitions at `0x4200bc36`/`0x4200bb4c`. `0x4200bd8c` relies only
on the minute flag; stale digits are deliberately corrected by real rollover.

[Weather/field execution](../../../qemu/parity/weather-checks.md) adds retained
frames, explicit field corrections, real BMP read errors and independently checked
scroll pixels. `helper_at_42010eca.asm` uses an explicitly bounded excerpt ending
after the decoder's final branch, rather than the much later next known symbol.

[Calendar execution](../../../qemu/parity/calendar-checks.md) compares 96 retained
frames against clean native and explicitly corrected factory output, including
unchanged-second year jumps and leap-year day-number collisions.

[JPEG execution](../../../qemu/parity/jpeg-checks.md) compares all 107 public
images, errors and clipped placement. The bounded helper excerpt ends after
the actual `jd_decomp` return at `0x42012090`; the next helper starts at `0x42012092`.

`../../tools/disassemble_factory.py` reproduces exports with an explicit local
objdump path and a list of addresses or bounded IROM ranges.
`../../tools/assist_c_port.py` is an unfinished library draft for the next stage:
instruction parsing, basic blocks, dominators/natural loops, ABI stack hints and
C branch conditions exist; a complete C-draft emitter, CLI and tests are pending.
