# Controlled renderer execution

`machine-validation.json` records a differential execution of the immutable
factory RV32 instructions and the rebuilt ESP32-C2 ELF in Unicorn 2.1.4.
The prepared factory ELF's five load payloads are checked byte-for-byte against
`Small_TV/full-flash.bin`, whose SHA-256 is verified before execution.
The rebuilt binary must match the archived development `app.bin` and its manifest.
Each report identifies the tested ELF, firmware and source hashes.

The test uses the genuine ESP32-C2 revision-2 ROM code/data for software
floating point and libc, and each program's linked libm. For the literal
programs, the only host adapters are LCD transport and integer/string formatting. Unsupported
format conversions fail explicitly. The shared ST7789 panel model applies the
actual address windows and RGB565 payloads; it does not draw glyphs or hands.

## Cases and intended corrections

The full run checks 150 initial states per theme and eight successive updates
per theme: **316 cases**, with all 57,600 pixels compared in each case.
Inputs are synthetic hour, minute, second, weekday, date-format and 12-hour
mode, listed in that order in JSON. The fixed synthetic date is 2026-10-13.
Cases include every weekday 0..7, all three date formats, both hour modes,
cardinal hand angles, blinking colons and minute/hour transitions.
Sequential cases retain renderer RAM and the existing panel pixels to exercise
hand erasure and conditional field updates.

The Sunday bug at `0x4200bf9c` is deliberately corrected following the user's
instruction to fix obvious vendor errors. Factory simple-clock weekday 0
leaves its date string in the weekday buffer; weekday 7 correctly draws `Sun`.
For each Sunday-0 test the report retains the literal original-versus-C pixel
difference, then executes the original's supported Sunday-7 path as a separate
expected reference and compares the complete frame again. No pixels are masked.
The second confirmed vendor bug is the reversed `sin/cos` stroke offset pair
in `0x42009644`. With angle `atan2(dy,dx)+pi/2`, perpendicular offsets must
use `cos/sin`; the original `sin/cos` collapses axis-aligned thick lines into
overlapping thin lines. This defect is corrected rather than reproduced.
A separate expected-reference machine redirects only the JAL at `0x420097fa`
from `sin` to `cos`, and the JAL at `0x4200982c` from `cos` to `sin`.
The genuine floating-point, rounding, line rasterization and remaining renderer
instructions still execute. No executable bytes are modified; the literal
factory machine has neither redirection. Four independent geometric checks
also require compiled-C width-five horizontal/vertical strokes to occupy
exactly five complete rows/columns, in both endpoint orders.

`equal` describes literal factory equality; `passed` requires every frame to
match the original or a specifically declared corrected reference, and all
four geometric checks to pass. Thus a passing run is not
misrepresented as byte/pixel identity where a bug was intentionally fixed.

The current run passes all 316 frame cases and four geometric checks.
There are 139 literal factory matches, 19 Sunday-reference matches and
158 corrected analog-reference matches. Instruction execution also exposed
float narrowing of tick angles; that detail is restored without copying the
incorrect stroke geometry.

## Reproduction

From the repository root, build with `Small_TV/src/build.ps1`, then run:

```powershell
# One-time setup; dependencies stay in the ignored .build directory.
& .\Small_TV\src\tests\run-machine-oracle.ps1 -InstallDependencies
# Full matrix using the current successful build.
& .\Small_TV\src\tests\run-machine-oracle.ps1
```

The runner prepares the analysis ELF from the hash-checked local dump. It uses
the installed SDK Python environment and revision-2 ROM ELF under `.idf`.
`-PythonPath` accepts another Python 3.12+ installation; install the pinned
`src/tests/oracle-requirements.txt` dependencies there or use the setup switch.
`-Quick` selects six boundary cases and eight sequential updates per theme.
`-OutputDirectory` overrides the ignored default
`.build/small-tv-parity/oracle`. Unapproved differences, machine faults and
instruction deadlines return failure. Failure PNGs have no identifying metadata.

This verifies the selected renderer paths only. It does not emulate interrupt
timing, task scheduling, network services, HTTP handlers, photo decoding or the
whole board. Full functional equivalence remains unfinished; existing
whole-board capture reports retain their separate source/build identities.
