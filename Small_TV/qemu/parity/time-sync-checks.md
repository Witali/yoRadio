# SNTP validity, fallback and calendar checks

The reconstructed clock now becomes valid only after the real ESP-IDF SNTP
notification. Initialization, a future RTC year and a successful HTTP settings
request do not establish synchronization. A small atomic latch bridges the
TCP/IP callback and display task. It remains set across a temporary disconnect
or client reconfiguration, and a program reset requires a new notification.

## Confirmed factory behavior

- Notification `0x420109de` sets byte `0x3fcc3ab8`. Update `0x42010b70` ignores
  that flag and rejects `tm_year <= 124` at `0x42010b96`, including synchronized
  leap-day 2024. The startup calendar remains 2025-09-19 17:04:40.
- Its cache updates only when the seconds field changes at `0x42010bb0`.
  A year jump with unchanged seconds can retain the previous calendar.
- Each 21st invalid-year update calls `0x42017ea0` at `0x42010c3e`.
  This is **sntp_restart**, not an enabled query. It calls `sntp_enabled`
  (`0x4201bec6`) and schedules callback `0x42017d34`, which stops and initializes
  the client. These repeated restarts can cancel the 15-second next-server
  timeout. Whether server 2 is reached depends on main-loop timing; server 3
  was starved in the recorded simple-theme fixture.
- After a valid time correction the simple date still waits for the minute
  event. A shorter date overwrites only its new glyph rectangles, leaving the
  previous outer columns. The real UDP test preserves this literal retained
  framebuffer model, including every residue byte. Our date must be clean.

Complete bounded helper excerpts and code hashes are in
`../../src/reference/assembly/manifest.json`. The earlier exploratory
`time-cache-observation.json` retains its historical adapter labels with a
correction annotation; it did not emulate asynchronous restarts.
`native-time-sync.asm` and its manifest preserve the exact final C helper/worker
instructions, including the release/acquire fences and notification guard.

## Executed checks

`tests/time_state_oracle.py` executes the actual factory update/notification,
Newlib conversion and compiled native notification/validity functions. Only
factory `time()`, restart and logging SDK boundaries are adapted. Five literal
cases retain the old cache/year/retry behavior and exact restart-call counts;
eight native checks include notification absence for 2024/2030, successful
pre-2025 conversion, backward/year jumps, epoch zero and post-2038. Invalid
conversion preserves the caller's output. This gate does not replace transport.

Platform cases `clock_sync_classic` and `clock_sync_simple` run the actual time
worker and clock task. They deliver the callback at an unchanged epoch, require
correct 2024 output, retain synchronization during disconnection, and repaint
the advanced calendar on reconnect. The existing station-offline policy holds
the LCD frame; it is not evidence of a continuously repainted offline display.

`tests/time_qemu.py` boots both complete applications in disposable persistent
flash copies. Synthetic settings choose the simple theme and a second NTP
server. The opt-in QEMU service can withhold replies and supply fixed epochs;
it changes external UDP/DNS packets only. Tests do not patch guest registers,
RAM, clocks, callbacks or executable bytes. HTTP legitimately changes only the
disposable settings/NVS area; source images and executable/media regions remain
hash-checked.

The native flow must contact servers 1, 2 and 3 in order after the first two
fail, accept synchronized 2024, reconfigure to server 2, advance to 2026, move
back to leap-day 2024, interpret NTP's era after 2038, reset without a valid-sync
latch, and synchronize again. Every date-band byte is compared with immutable
factory ASCII glyphs. QOM defaults and four rejected inputs are checked too.
The pinned SDK retains its last server index across stop/init; failure masks
force the configured server rather than assuming reconfiguration starts at 0.

The real system-time check reads the RTC boot offset and, for native firmware,
the guest-latched SYSTIMER UNIT0 count plus the identified SDK RTC/HRT offset and
system correction. For the configured 26-MHz C2, `ticks_to_us = ticks*5/52`.
Those components change at reset, so QEMU lifetime time cannot replace SDK
time-since-boot. A sample freezes observation briefly and resumes the guest;
the measured UTC must agree with the delivered NTP timestamp in the same
virtual-time interval within one second. UI pixels alone cannot satisfy it.

## Evidence and limits

The full `sntp-final-20261014` suite passed against the final rebuilt application.
It includes native 3,021 checks, platform 26 scenarios / 742,437 checks, frontend,
integrity, nine offline timezone-source cases, the existing RV32 renderer/control/
weather/calendar/JPEG gates, 36,404 timezone comparisons, time-state and full QEMU.
The native real-SNTP flow recorded six independent UTC observations; the largest
absolute difference was about 33 ms. All required date/reset stages passed.
Published evidence: `time-state-validation.json`, `../time-http-validation.json`,
`../../src/tests/functional-validation.json` and `../ntp-board-validation.json`.

App SHA-256: `2a60eefcc480f96eced3e6318f91995f89b38475f93ce3551da1847c135f672c`;
source: `9402fd83c7cef65222685deff3fbe6a98ad9cb197413da3d6af2b90536ace019`;
native ELF: `ee74d566d3d13a33c5d2ce767d8b7570efc853b6446d390b9d6646dc7793a394`.
App size is 1,115,104 bytes, leaving 420,896 in the application partition. Static
DIRAM is 80,650 bytes; runtime heap/stack headroom was not measured. Earlier failed
experiments are not full validation and remain in the ignored work area.

QEMU main `b90e2131b8` adds these service controls. Fresh CYD boot/MMIO,
ESP32-C3 OLED legacy/modular boot, C2/C3 shared SPI and I2C, dual-host ESP32 SPI,
SD sector/CS isolation and five virtual-network contract tests passed with the
new RISC-V/Xtensa binaries. This is emulator evidence, not physical RF, low-power,
memory-soak or live Internet-service validation. The original dump is unchanged;
no board was flashed. Full functional equivalence remains unproven.
