# Factory instruction audit checkpoint

AP service lifetime: `application_main_at_42008e56.asm`,
`0x42009032..0x42009052`, checks the initialized AP flag and stays in the setup
loop after AP initialization/display. Native `services_start` uses the actual
initialized network role to keep weather cache access but defer station-only
workers. Factory performs much of this work inline; this does not assert an
identical factory task layout. BC68 scoped AP HTTP/frame and STA controls are
recorded in `../../../qemu/parity/ap-services-validation-20261018.json`.

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
| `0x4200f2c0`, especially `0x4200f380..0x4200f39e` | The complete country/region suffix is copied into a 20-byte slot; the native two-letter restriction is corrected with NVS v1 migration |
| `0x42008e08`, `0x42008e32..0x42008e34` | Theme initialization is followed by duty 0; the next complete digital frame must not retain startup brightness |
| `0x42009ccc`, `0x42009cf4`, `0x4200a156` | Initial and active incremental dial entry points used by read-only completed-frame observations |
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

`initialize_wifi_station_at_4200ca30.asm` sets event-group mask3 and
`portMAX_DELAY` at `0x4200cc0e..0x4200cc22`. `0x4200cc26` gives success-bit1
priority over failure-bit2; the failure branch at `0x4200ce20..0x4200ce3c`
persists mode2 and restarts. The independent 181 display ticks are not a
station/DHCP deadline. An earlier native18-second fallback was incorrect:
actual factory DHCP waiting at30guest seconds retained mode1, while native
had already rebooted into setup. The corrected native waits for the SDK's
retry exhaustion and retires its failure latch on a new lease. Four real
packet/network QEMU cases, source platform tests and the RV32 event oracle
are recorded in `../../../qemu/parity/wifi-fallback-validation-20261017.json`.

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

[Timezone execution](../../../qemu/parity/timezone-checks.md) compares real Newlib
and native country conversion against independent pinned IANA TZif data.
`helper_at_420aa5ce.asm` includes the time/localtime/tzcalc/tzset code through its
final parser branch at `0x420aaf5e`, ending before the next helper at `0x420aaf60`.
The fallback at `0x420aaebe..0x420aaedc` installs M3.2.0/M11.1.0 US defaults when
the recovered country string omits recurrence rules. The factory country table
and `0x42010a06`/`0x42010b70` remain unchanged reference evidence.

The bounded SNTP excerpts distinguish the SDK restart wrapper `0x42017ea0`
from its enabled query `0x4201bec6`. The wrapper schedules callback `0x42017d34`,
which stops and initializes the client. Each excerpt ends immediately after its
actual return/tail jump. The application's `0x42010c3e` calls this restart every
21 invalid-year updates; it is not a passive status query. Historical
`time-cache-observation.json` keeps its old adapter labels with an explicit
correction annotation. `tests/time_state_oracle.py` separately records actual
restart-boundary calls; `tests/time_qemu.py` checks the real packet/fallback path.

`http_advancedset_at_4200e9ea.asm` preserves the full advanced-settings handler.
Its NTP-copy branch sets only the dirty/save deadline at `0x4200eb88..0x4200eb94`;
it does not clear the SNTP init byte. The city handler explicitly clears init
and sync at `0x4200f3d4`/`0x4200f3dc`. The natural calendar transport test uses
that real endpoint for factory re-entry and records the advanced-only observation.

`../../tools/disassemble_factory.py` reproduces exports with an explicit local
objdump path and a list of addresses or bounded IROM ranges.
### Control-flow review tool

`../../tools/assist_c_port.py` reads decoded RV32/RVC objdump text and generates
JSON plus a Markdown review with the original instructions beside C branch
conditions. Run from the repository root with Python 3.10 or newer:

```powershell
python ./Small_TV/src/tools/assist_c_port.py `
  ./Small_TV/src/reference/assembly/read_clock_theme_at_4200dfdc.asm `
  --symbols ./Small_TV/src/symbol-map.json `
  --json ./.build/port-assistant/clock-theme.json `
  --markdown ./.build/port-assistant/clock-theme.md
```

Use `--start 0x4200dfdc --stop 0x4200e074` to bound a larger input; stop is
exclusive and neither boundary may split an instruction. `--name` labels one
selected function. Optional `--symbols` binds exact addresses to established
logical names and native C modules; unmatched calls retain their addresses.
Use `--force` to replace a generated report. Input, symbol map and tool files
are protected against accidental output overwrites. Without output flags JSON
is written to stdout. Every report records source/tool/symbol-map SHA-256.

The CFG uses direct intraprocedural flow and the possible return from calls.
Indirect transfers, traps, gaps, outgoing branches and a call inside the selected
range produce explicit review warnings. A backwards edge is called a natural
loop only when its target dominates its source. The original getclocktype
handler has a backwards jump at `0x4200e072` into its shared completion block;
the report correctly finds no natural loop. Its 50 instructions include a
32-byte frame, one return at `0x4200e068`, and four external calls. The excerpt
ends at `0x4200e074` before the next function, with the original dump unchanged.

Stack allocation/save/restore matches are ABI hints. C conditions refer to a
conceptual `uint32_t r[32]`; the tool leaves instruction implementations,
external-call behavior, indirect control flow and high-level algorithm recovery
to manual work and machine-code comparison. Successful report generation is a
parser/analysis result, not evidence of firmware equivalence.

Run the separate tool tests without changing a firmware test run:

```powershell
python ./Small_TV/src/tools/tests/test_assist_c_port.py `
  --temp-root ./.build/port-assistant-tests
```

The tests cover compressed fallthrough, short targets, canonical/offset returns,
disconnected and irreducible graphs, natural loops, malformed layouts, multiple
ELF sections, bounded CLI output, exact name bindings and the real factory
getclocktype excerpt. Reproducible results are recorded separately in
`../../../qemu/parity/port-assistant-validation-20261017.json`.

`application_main_at_42008e56.asm` preserves the actual active-clock dispatch:
`0x42009054..0x420090c0` gates weather retry by station state, while all four
theme calls and `0x42010b70` remain reachable offline. The station event handler
at `0x4200c602` copies GOT_IP's address at event-data offset 4 into `0x3fcb7b84`
and does not clear it on disconnect. `tests/network_oracle.py` executes the
event/cache code and a bounded active-loop slice; source-based clock tests
separately exercise offline time, DST and photo fade. See
`../../../qemu/parity/offline-clock-checks.md` for the candidate's scope.

`jpeg_quantization_tables_at_4201105c.asm` records the ID alias at 0x420110c4.
`jpeg_header_prepare_at_42011c48.asm` records SOF fields read without checking
precision/component payload length. Actual RV32 tests reproduce literal factory
acceptance; native rejects these malformed headers. Exact before/after evidence
is in `../../../qemu/parity/jpeg-header-checks.md`.

`jpeg_huffman_tables_at_42011100.asm` preserves the complete original builder,
ending before the next function at 0x42011244. The codeword loop at
0x42011194..0x420111c8 trusts length counts and wraps a 16-bit accumulator.
Actual malformed inputs with unused impossible branches are accepted by this
literal code. Native now checks available prefixes first; see
`../../../qemu/parity/huffman-checks.md` for exact before/after results.
