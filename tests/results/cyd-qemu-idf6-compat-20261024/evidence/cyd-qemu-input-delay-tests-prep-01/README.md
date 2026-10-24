# Classic ESP32 input-delay unit runner: source preparation only

The new canonical candidate test_esp32_spi_input_delay.py imports the same-directory
byte-exact 274-case test_esp32_idf6_compat.py (SHA256 c07cac9b1f980c0a610de1b9487f3d698d08ddd123ad71ccf254d3dbf0eb2f18).
It reuses that controller's StoppedQTest, transfer, fact, need and MODEL_FILES
without rebinding or changing their code. The canonical controller path/hash is
checked before import and the resolved imported path is checked afterwards;
bytecode writes are disabled. This preparation only reads bytes/hashes and AST.
Neither runner was imported, called or executed; no external source was edited.

The CLI retains --qemu, --qemu-sha256, --source-root, --rom-dir and --out, and adds
--input-delay-ns with choices0/25, default25. The owned paused QTest child receives
-global driver=ssi.esp32.spi,property=input-delay-ns,value=<choice>. The underlying
model property default0 and original 274-case runner remain unchanged. Selected
executable, both test sources, six model files, two ROMs and fresh four-MiB synthetic
flash are all recorded before/after. -snapshot, stopped CPUs, stdio QTest, no NIC,
serial, monitor, display or host audio preserve the primary fixture's scope.

Exactly386 saved comparisons are required: initial SPI_CLOCK reset0x80003043,
then five clock cases with77 comparisons each. Each case checks full register R/W,
72 backing-data reads (six modes, three addresses, lengths2/3/16/64), JEDEC ID,
written QE readback, omitted-protocol QIO negative and full-duplex noncompensation.
QE is set by a real06/31 write. Clock values and delay expectations are independent
SDK-based literals, not calls to the model calculation. At25ns the compensation
counts are2/1/0/1/2 for EQU80, DIV40=0x1001, DIV20=0x3043, PRE2/N0=0x40000 and
EQU with nonzero unused PRE/N/H/L fields. At0ns every compensation count is0.
SPI_CLKCNT_N is bits17:12; H11:6 and L5:0 do not define the frequency divider.

Pure-RX reads add the expected compensation to protocol dummy lengths: SDK QIO
uses28 address bits/base5, DIO28/base2, other modes use the canonical defaults.
The missing-QIO negative includes compensation only and must still differ from
the backing sentinel. Full-duplex9F with MOSIff plus8dummy clocks must return
401600 for either property value; compensating RX+MOSI would incorrectly give
C84016 and fail. A precompensation control with recognized clock/property support
but no delay subtraction is expected to fail24 QIO rows at the two80MHz cases.
This is a proposed sensitivity expectation, not an execution result.

The unchanged controller requires real stdout EOF, reader join, no reader/watchdog
errors, bounded owner-only termination/reaping and unchanged inputs. Its MMIO phase
has a60-second deadline, per-command response limit3seconds, and32MiB monitored
log caps with terminal overshoot rejection; bounded cleanup and hashing follow.
The new runner preserves the primary terminal-classification predicates exactly.
It has a strict386-count gate and reports INCOMPLETE on controller/identity failure.

This validates a bounded functional collapse of controller sample compensation
and an explicit fixed80MHz-source input-delay property. It does not qualify bit
waveforms, analog timing, arbitrary APB changes, warm reset, every flash part,
production startup, physical audio, networking or hardware. Root owns source
review, actual model/build pins, negative controls and both0/25ns executions.
