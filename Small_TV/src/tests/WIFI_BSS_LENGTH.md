# BSS Max Idle IE length correction — 3 November 2026

Continued from `smart-tv` / `9124ecbe6` and the two unfinished association
qualification files in `.worktree/smart-tv-integration`. The original files
and frozen before-image remain intact. Current work is on
`codex/small-tv-parity-20261103` in `.worktree/small-tv-parity-20261103`.

The device remains the ESP32-C2 / ESP8684H Small TV: 4 MiB flash, 272 KiB
on-chip SRAM including 16 KiB cache, 26 MHz crystal and a 240×240 ST7789-family
display. These are recovered identification results, not a new hardware probe.

## Confirmed defect and correction

The factory setter at `0x4206d90e` and the pinned native SDK setter read
three payload bytes without checking the BSS Max Idle IE length. With the
feature enabled, lengths 0, 1 and 2 reach this body through the real
association and reassociation management paths. Tests observe reads beyond
the selected element, including beyond the packet when it is last.

`app/network/wifi_bss.c` ignores short optional elements, retaining the
previous peer period and options as for an absent element. Valid periods,
option-bit masking and log arguments remain unchanged. Overlong declared
extents still take the original caller rejection path; a trailing single
header byte is ignored. The original last-complete-duplicate selection is
preserved. The setter relies on the qualified containing-frame validation;
it is not a general buffer parser accepting an unchecked pointer.

A definition redirect covers the same-object vendor call. Ordinary
`--wrap` cannot establish that path. The build now refuses to archive without
`verify_wifi_bss.py` binding the replacement, the full association/getter,
management ingress, function-pointer registration and OSI backend. The
archived proof and its digest are included with the production bundle.
The shared SDK installation is unchanged.

## Verification

- **15,435 RV32 executions:** factory, unchanged before-image and corrected
  production ELF; all 256 lengths, all 256 option bytes, period boundaries,
  enabled/disabled state, association/reassociation, absent/duplicate/truncated
  inputs and elements followed by an unrelated complete element.
- The 24/24 original setter instruction starts and 22/22 corrected starts
  execute. Packet/peer/station writes, log arguments and ABI are checked.
  Stale build, wrong app descriptor and changed guard opcode are rejected.
- Existing native suite: **6,304 checks**, independent JPEG privacy:
  **3,727 assertions**, nothrow allocation: **26 cases**, artifact integrity:
  **9 tests**, correspondence inventory controls: **17 tests**.
- Final production app `564ea463fc98…`, ELF `e01db928f75f…`, 1,476,176 bytes;
  the final archived pair is identical to the RV32 test inputs. Its source
  manifest includes the new guard and its qualification tools.

The reproducible test is `tests/bss_assoc_test.py`; its CLI requires factory
ELF, frozen before ELF/app, current ELF/app/object, original net80211 library
and the current SDK library directory. The compressed report is bound by
[`wifi-bss-length-validation-20261103.json`](../../qemu/parity/wifi-bss-length-validation-20261103.json).
Production firmware is saved in
`firmware/development/small-tv-esp32c2-reconstructed/` in this task worktree.

BSS support remains disabled by default. This is a verified conditional
defect correction, not evidence that default operation was crashing.
Complete association/RF behavior, concurrent peer lifetime, final full-suite,
24-hour soak and physical-board acceptance remain open. This change did not
flash, reset or transmit to a physical device.
