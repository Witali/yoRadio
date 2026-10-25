# PM start/stop bodies and cancellation boundaries

25 October 2026. Continuation of [keep-alive](WIFI_KEEP_ALIVE.md). Factory/native
ELFs remain `8c9fd166…` / `9e4ec88d…`; no firmware or QEMU behavior changed.
The factory comparison remains the user's first priority.

## What executes

`timer_pm_lifecycle.py` requalifies the preceding PM bodies and adds full
22-byte SDK cancellation functions: factory `pm_disable_active_timer` at
`0x42074ad6`, factory `pm_disable_max_idle_timer` at `0x42074aac`, and native
`pm_disable_active_timer` at `0x42079f70`. The active object is at PM **200**,
not 220. The factory max-idle object is at PM 492. Complete object-code matches
and shared PM/OSI anchors are checked before executing either helper.

The pinned rev200 ROM SHA is
`289ce00e79c024d9efeb29a7fbc2d21853a1cbc383a2b9c2ece85c54fa829dd9`.
Its real four-byte entry `0x40001b74` jumps to the complete 30-byte
`pm_disable_sleep_delay_timer` at `0x40043cae`. The test executes both unchanged:
it clears PM byte 440 and requests disarm of PM 260 through OSI slot 228.
ROM global `g_pm_ptr` at `0x3fcdfd7c` is bound to the synthetic PM object in this
private fixture. Its actual runtime binding has not yet been observed here.

The full factory/native start and stop bodies run from entry through return.
Platform, RF, beacon, coexistence and timer-backend calls outside the selected
helpers remain **explicit external stubs**. This proves the selected bodies'
direct effects under their input contracts, not every transitive effect of
the real driver or hardware.

## State, callbacks and repeated calls

The independent model checks all direct PM writes, untouched PM bytes, complete
configuration, globals immediately before PM, callback order and numeric log
arguments. Memcpy and the old output-byte callback have explicit, bounded
fixture effects. The real RV32 clock pair is tested across low-word carry and
64-bit wrap; original timestamp subtraction in the stop log is checked too.

Start accepts seven register inputs in the test. Argument 3 is the interval-like
input stored at PM word 52 (`a3 << 10`, or 102400 for zero); it is **not** the
configuration enable byte at offset 52 or the negotiated BSS Max Idle period.
Large inputs test existing integer truncation, not their protocol validity.
MAC bytes, TBTT pair, byte/halfword narrowing and callback caller-saved poisoning
are all checked. The optional beacon callback receives `a5` containing its own
call target, after the original argument was saved in `s4`; the test records
incoming registers without assuming a seven-argument callback prototype.

Start with PM byte 14 already nonzero and stop with it zero return without
the tested state changes or platform calls. Eight retained-state chains execute
`start, start, stop, stop, start`. Repeated calls are checked for empty direct
effect traces; the final start executes again and clears the investigated PM
pending fields, including native offset 576. The last configuration enable
value remains as actually written by stop; a protocol re-negotiation is outside
these bodies.

## Cancellation difference remains a runtime question

With the platform calls explicitly bounded as above, factory stop requests
disarm of objects **260, 200, 180 and 492**, in that order. Native requests
**260, 200 and 180**. Both clear configuration byte 52. This confirms the
previously identified difference in direct cancellation; it does not prove
that no other real driver path cancels the modern timer.

The shared ROM `pm_update_by_connectionless_status` was inspected separately:
actual body `0x40045d68`, 374 bytes, behind entry `0x40001f70`. It directly
disarms 316/336 and conditionally calls other ROM tables. That body and its
transitive callbacks are still external to this fixture. The native ELF's
size metadata at the ROM entry is not the real ROM-body extent. Coexistence,
beacon and active-timer helpers can also have further effects; they must be
followed or observed before proposing a vendor timer fix.

Next runtime check: observe the real ROM PM pointer and modern timer backend
before/after a natural station disconnection, under an owned disposable VM.
Read only qualified numeric metadata. `esp_timer_is_active` was not found as
a linked native function, so do not invent or call that API through the guest.
The native SDK source defines the timer's `alarm` field at offset zero and
`timer_armed` as `alarm > 0`; derive the actual DWARF/layout before interpreting
any backend handle. The factory layout needs its own qualification.

Follow-up: [real station-loss observations](WIFI_PM_RUNTIME.md) now confirm
the native caller cancels keep-alive immediately after `pm_stop`. No timer
patch is needed for that path. Factory recovery failed in the paired QEMU
scenario and remains explicitly unqualified.

## Tests and evidence

**5224 private RV32 executions** cover 1440 start cases and 1152 stop cases per
image, plus 40 retained-state invocations. Every instruction start in the four
lifecycle bodies and the included SDK/ROM helpers was visited: 319 factory and
309 native fixture addresses, counting the same ROM helper in each fixture.
Stack/callee-saved registers survive all cases; caller-saved registers are
poisoned at each declared boundary. No live SRAM, credentials or packet payload
are used. No production delays were added or removed.

Five static controls reject wrong ROM/factory/native bytes, swapped SDKs and
reading non-executable data as code. Five evidence controls reject lost
cancellation, broken repeated-call behavior, wrong ROM binding, incomplete
coverage and an unjustified platform-equivalence claim. The consumer reexecutes
the original bytes and compares the complete archived result.

`factory-pm-lifecycle-validation-20261025.json` pins 15 source files and one
39281-byte gzip report. Trace SHA:
`c502b3b4d41811c63cb76cb4f0093a10010397a33db168644bd81d7784852e80`.

```powershell
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& $py -B -X utf8 Small_TV/src/tests/verify_pm_lifecycle_evidence.py `
  --proof Small_TV/qemu/parity/factory-pm-lifecycle-validation-20261025.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --old-pp C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libpp.a `
  --new-pp C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libpp.a `
  --rom C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf
```

TIM, remaining null-failure branches, station-object lifetime, negotiated period
validation/overflow, full callback delivery, RF, whole-image audit, independent
final gates and physical-board acceptance remain open. The new full-body scope
does not turn synthetic state coverage into full runtime lifecycle equivalence.
