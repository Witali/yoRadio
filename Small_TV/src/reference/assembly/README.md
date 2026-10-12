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
| `0x42009644`, `0x420a74e6` | Float narrowing of atan2 and rounded stroke offsets rather than truncation |
| `0x4200a5be`, `0x4200aa1e`, `0x4200acae` | Original glyph pointers, padded rows, LSB-first pixels, spacing and decorative dimensions |
| `0x4200afcc`, `0x4200b738`, `0x4200bd8c` | Conditional field updates instead of full-screen repainting |
| `0x4200bc36` | Six fade levels and photo replacement at duty 1000 |
| `0x4200fd94`–`0x4200fda0` | Kelvin subtraction followed by ROM `__fixdfsi`, truncating Celsius toward zero |
| `0x4200fe82`–`0x4201082c` | Half-open compass sectors and double comparisons |

Other exported functions remain reference material; exporting them is not a
claim that every execution path has been checked. The corresponding production
C comments retain verified addresses. Safety/privacy fixes and the ESP-IDF SDK
version difference are documented in `../../README.md`.

`../../tools/disassemble_factory.py` reproduces exports with an explicit local
objdump path and a list of addresses or bounded IROM ranges.
`../../tools/assist_c_port.py` is an unfinished library draft for the next stage:
instruction parsing, basic blocks, dominators/natural loops, ABI stack hints and
C branch conditions exist; a complete C-draft emitter, CLI and tests are pending.
