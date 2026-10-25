# Wi-Fi event 11: factory/native algorithm comparison

25 October 2026. Continuation of [timer dispatch](WIFI_TIMER_DISPATCH.md).
This checkpoint follows the user's priority: whole factory-firmware comparison
first; CODEC-REPRO, the other JPEG fault cases and long-run investigation remain
open. No firmware, SDK, QEMU or frozen runtime producer was changed here.

## Exact code that was compared

Factory ELF SHA-256: `8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882`.
Native ELF SHA-256: `9e4ec88d6e85ae58fa3e164362f1b10491f9edef0feaa4af8c52c9fa88446e24`
(app `c91294fc…`, including the [invalid-ID guard](WIFI_TIMER_GUARD.md)).
The old/new `libpp.a` identities are enforced by `reverse/timer_event11_match.py`.
They are different SDK versions, not two names for identical implementations.

| Role | Factory start, bytes | Native start, bytes |
| --- | --- | --- |
| Event wrapper | `pp_timer_max_idle`, `0x4207b08c`, 18 | `pp_timer_keep_alive`, `0x42079e4a`, 18 |
| Handler | `pm_max_idle_timeout_process`, `0x4207605a`, 88 | `pm_keep_alive_timeout_process`, `0x4207b594`, 128 |
| Rearm | `pm_enable_max_idle_timer`, `0x42074bb2`, 86 | `pm_enable_keep_alive_timer`, `0x4207a08a`, 92 |
| Parameter setter | `pm_set_bss_max_idle`, `0x42074c12`, 52 | `pm_set_bss_max_idle`, `0x4207a106`, 50 |

Each complete body matches its own SDK object, allowing only declared ELF
relocations and relaxation. Local branches, data anchors and linked native
symbol extents are checked. Event-table cell 11 selects the actual wrapper.
This also distinguishes the setter from the intervening 10-byte getter at
factory `0x42074c08`; the next discovered symbol is not a function boundary.

The associated initialized OSI tables contain 480 bytes: factory `0x3fcb459c`
has ABI version 8, native `0x3fcab93c` has version 9. Slots 224, 228 and 240
and their complete forwarding wrappers were checked against actual bytes.
They forward to legacy timer code linked into IRAM, not to ROM functions.
The factory slot-224 target explicitly multiplies by 1000, keeping both halves
of the product before passing it to the timer backend. Its slot-240 counterpart
passes the microsecond argument directly. Native `ets_timer_legacy.c` and the
linked native targets agree with this distinction. Runtime registration of
this OSI table and the complete timer backend remain outside this checkpoint.

## Confirmed differences

Offset names below refer to the selected SDK structures. Their full field
meanings and which combinations are reachable still require producer analysis.
Factory `g_pm` is 544 bytes; native is 584 bytes. Native offset 576 is therefore
inside its own structure, not an out-of-bounds access inferred from the old size.

Both handlers first invoke their real rearm function. When PM bytes 14/15 are
nonzero and byte 16 is zero, factory sets byte 488 and requests wake, or
optionally dream followed by a null frame, depending on word 36 and byte 1.
Native suppresses that action if byte 488 is already nonzero. Native also sets
bytes 288/488/576 when byte 15 is zero and emits an additional log call after
the wake/null-frame path. These are actual instruction differences; synthetic
states alone do not establish an application regression or an SDK defect.

Factory rearms only if configuration byte 52 is nonzero and PM word 36 is zero,
using slot 224 with `period72 << 9`. Native also supports a nonzero fallback
word 28 when byte 52 is zero, does not gate rearm on word 36, and uses slot 240
with `((period72 << 10) * 1000 - adjustment56) mod 2^32` when enabled.

The input representations differ. For a positive setter argument `n`, factory
stores `n` for `n <= 4`, otherwise `max(n, 2*(n-4)) mod 65536`. Native stores `n`
and an adjustment of 500000 for `n <= 3`, otherwise 2000000. Factory immediately
calls rearm; native's setter only changes configuration. Zero clears the enable
byte in both; factory additionally invokes its disable helper. Both retain the
previous period field on zero input. The disable helper is an explicit external
stub in this test, so its internal effects are not claimed.

The same setter input 10 yields a later arm argument of 6144 to slot 224 in
factory versus 8240000 to slot 240 in native. These correspond to nominal
6.144/8.240 seconds at the legacy adapter boundary; actual scheduling elapsed
time has not been measured. This does not identify the earlier QEMU HTTP delay.
The period multiplication and truncation boundary cases are retained as
observations of the existing code, **not a requirement to reproduce overflow**.
Before correcting or replacing SDK behavior, trace valid protocol input ranges
and the corresponding timer initialization, cancellation and flag transitions.

## Tests and retained evidence

`timer_event11_model.py` contains independent, offset-named algorithm models;
`timer_event11_instructions.py` executes unchanged body bytes in private Unicorn
RV32 fixtures. Only transitive wake/dream/null/log, disable and OSI timer calls
are stubbed. Each stub poisons caller-saved registers. Stack restoration,
callee-saved registers, exact PM/configuration writes, callback arguments/order
and wrapper return value are checked. Reads/writes outside the explicit fixture
regions are rejected. No live SRAM, credentials, stack contents or QMP/RSP
connection is used.

There are 4632 event inputs per image, including the boolean Cartesian product,
noncanonical nonzero bytes, disabled/fallback timers and arithmetic boundaries.
Another 128 setter inputs per image check every configuration write and then
execute an event from the verified resulting fields. Total: **9776 executions**,
covering all 186 instruction starts in the eight selected bodies. Of the 4632
raw-state pairs, 4344 have different observable traces and 288 match. This is
not a percentage of real-world compatibility: the matrix contains synthetic
states and the SDK structures represent different versions.

Eleven static rejection controls cover wrong images/libraries, changed return
value, truncation, neighboring code, wrong PM anchor, wrong ABI/magic and swapped
timer slots. The evidence consumer reruns the actual matrix and rejects five
alterations of counts, coverage, ABI, observed calls and equivalence claims.
`qemu/parity/factory-event11-validation-20261025.json` pins nine sources and a
7630-byte gzip result. Raw ELF, SDK archives and whole disassembly are not copied.

```powershell
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& $py -B -X utf8 Small_TV/src/tests/verify_timer_event11_evidence.py `
  --proof Small_TV/qemu/parity/factory-event11-validation-20261025.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --old-library C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libpp.a `
  --new-library C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libpp.a
```

Use the pinned producer revision if these analysis sources later change. This
is a selected-body static/CPU checkpoint, not whole-image equivalence, a radio
test, H10, or a physical-board acceptance result. Next: verify OSI binding and
timer registration/posting; follow the setters and PM flag producers to determine
which differences affect the clocks. Continue the remaining computed aliases,
undefined function boundaries and SDK/application transitions in the whole-image
inventory. Do not revert modern SDK behavior solely to match synthetic states.

Next checkpoint: [WIFI_TIMER_REGISTRATION.md](WIFI_TIMER_REGISTRATION.md) binds
the OSI registration and actual timer+492/posting chain. Two real QEMU station
boots also confirm the observed OSI pointers and tables. Full backend/RF and
connected/disconnected flag producer analysis remain open.
