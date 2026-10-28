# Full-range Wi-Fi keep-alive timer

`app/network/wifi_keep_alive.c` fixes `BSS-TIMER-RANGE`, tagged
`FIXED_FACTORY`. The factory can encode period 32772 as zero. The selected
ESP-IDF driver instead overflows its 32-bit microsecond calculation at period
4197: 760704 us instead of 4295728000 us. The failing producer baseline is
preserved in `factory-wifi-producer-validation-20261028.json`.

The replacement retains the microsecond API for representable intervals and
uses the existing millisecond adapter for longer intervals. Its real backend
promotes the milliseconds to 64 bits before multiplying. Configuration is
snapshotted before disarm; the adapter pointer is read again afterwards. Zero
fallback behavior and the vendor's defined low-word behavior for synthetic
out-of-range adjustments remain unchanged. BSS Max Idle support stays disabled.

The build guard `tools/verify_wifi_keep_alive.py` checks the complete compiled
replacement, all four SDK callers, real OSI wrappers, the SDK cancellation
function and three compiled timer backends. The linker definition redirect
also covers calls originating in the same `pm.o` archive member. Changed SDK
objects, ABI, source or bypassed callers fail qualification.

Validation is recorded in
`Small_TV/qemu/parity/wifi-keep-alive-range-validation-20261028.json`:

- 65836 private CPU executions, including every negotiated period 1..65535;
  all 177 instruction starts / 536 bytes in the selected closure were visited.
  Only public `esp_timer` operations and nonreturning error checks are modeled
  boundaries. Cancellation, rounding, adapter replacement, configuration
  mutation, invalid initialization and backend errors are covered.
- Seven rejection controls include an unchanged old image, mismatched inputs,
  changed source, a real ms-to-us instruction mutation and a bypassed SDK call.
- Native tests: 6298 checks; independent JPEG privacy controls: 3727 checks;
  nothrow allocation: 26 cases; artifact integrity: eight cases.
- Separate network-only QEMU test: initial configuration, reboot/cold boot,
  HTTP, NVS and SNTP in three phases. Separate display test: one cold boot of
  each image, all 57600 RGB pixels matched to the expected setup frame.
- A disposable network-only QEMU VM receives one explicit synthetic two-byte
  peer-period write, after `pm_start` returns and before the producer reads it.
  Actual `esp_timer_start_once` receives 67105840000 us for period 65535. Typed
  backend metadata retains the long alarm; natural station leave cancels it
  to zero. The runtime feature bit was observed off. No registers, executable
  instructions, source images or physical device were changed by the fixture.

The initial long-timer harness injected before `pm_start`, which subsequently
initialized the peer and discarded the fixture value. Those failed attempts
remain in the local build directory. Moving the fixture to the completely
matched period-load instruction fixes the test setup without changing firmware.

`keep_alive_range_test.py --help` documents the required exact app/ELF, local
object, SDK timer object/source, SDK archives and preserved before-image inputs.
It needs `pyelftools` and `unicorn`; the QEMU test additionally needs the frozen
VM helper bundle, ROM and the qualified QEMU executable. Build with
`build.ps1`, run `tests/run.ps1`, then `tests/artifact_test.py --resources` using
that build's resource directory. The validation record hashes the reports and
source files; it is not a standalone independent replay consumer.

This closes the selected timer arithmetic/backend test, not whole-image or
whole-SDK equivalence. No 18-hour expiry, concurrent station lifetime, full
association-input validation, final full suite, 24-hour soak or hardware
acceptance is claimed. Those gates and the rest of the improvement plan remain.
