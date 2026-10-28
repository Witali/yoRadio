# Old keep-alive predicate, TX completion and pending state

25 October 2026. Continuation of [registration](WIFI_TIMER_REGISTRATION.md).
The factory comparison remains the current priority. This checkpoint identifies
the old predicate/reset path and tests the changed TX logic before interpreting
the modern event-11 fallback as a missing factory feature.

## Bound bodies and callers

The original factory ELF `8c9fd166…`, current native ELF `9e4ec88d…` and exact
old/new `libpp.a` are unchanged. `reverse/timer_keep_alive.py` matches twelve
complete SDK bodies (4502 linked bytes), their local branches and shared calls.
Local anchors are scoped to the same `pm.o` and checked against preceding PM
state/configuration anchors; local names are not equated across SDK versions.

| Function | Factory start, bytes | Native start, bytes |
| --- | --- | --- |
| `pm_keep_alive` | `0x40390590`, 140 | Absent |
| `pm_reset_keep_alive` | `0x42074c5c`, 82 | Absent |
| `pm_tx_data_done_process` | `0x42075896`, 196 | `0x4207ad48`, 218 |
| `pm_process_tim` | `0x4039061c`, 488 | `0x420d1b6a`, 356 |
| `pm_start` | `0x420763d8`, 580 | `0x4207b93e`, 568 |
| `pm_stop` | `0x4207661c`, 374 | `0x4207bb76`, 352 |
| `pm_tx_null_data_done_process` | `0x420759cc`, 514 | `0x4207ae8c`, 634 |

The old `pm_process_tim` calls the real `pm_keep_alive` predicate. Old data/null
TX-completion bodies call `pm_reset_keep_alive`; modern counterparts invoke the
new rearm path directly. All these edges are checked against full matched bodies,
not inferred from similar names. Factory instructions `0x4207a020/24` also
materialize/store the predicate pointer in another table; its full initializer
and indirect caller lifecycle are still open.

## Time and TX behavior

The old predicate returns a boolean, not a transmitted frame. With PM word 36
zero it returns false without reading the clock. Otherwise it compares unsigned
64-bit elapsed time with either fallback configuration word 28 (timestamp at PM
88), or the enabled BSS interval (timestamp at PM 480). In the BSS branch the
existing code sign-extends the wrapped 32-bit `(period72 << 9) * 1000` product
before comparing. Boundary tests preserve this observation; they do not make
overflow a required feature of our firmware. Valid negotiated period ranges and
their setters must be traced before selecting a correction.

The old reset body, when PM byte 14 is nonzero, records the clock at PM 88/92.
With word 36 zero it also queries OSI slot 400 and may call the active-timer
helper. That backend's full semantics are external to this test.

For data completion with first argument nonzero, old code resets its timestamp
and beacon timeout. With nonzero third argument and enabled BSS mode it rearms
when appropriate and records PM 480/484. Modern code resets the beacon timeout,
then with nonzero third argument measures elapsed time from PM 480. It rearms
and updates the timestamp only when that elapsed time is **greater than 100000
microseconds**, including when BSS mode is disabled but the fallback is enabled.
Exactly 100000 does not rearm; 100001 does. The selected body compares time and
returns; it does not wait for 100 ms. This is not the earlier QEMU HTTP delay.

The two implementations have the same tested remainder concerning TX-idle,
sleep/disconnected-delay selection, state check, coexistence increment, byte 27
and active-timer selection. Real reset/rearm bodies are executed, with only
their explicitly declared platform helpers stubbed. The 64-bit clock is returned
in the real RV32 `a0/a1` pair; caller-saved registers are poisoned on helper return.

## Pending clear: selected completed-null-frame branches

Both complete null-completion bodies are matched. Tests execute 96 states per
image from the real function entry through return, with first argument zero,
second argument one, PM bytes 1/14/15/16/9/21/22 set to 0/1/1/0/0/0/1. These are
explicit synthetic branch fixtures, not a claim that every combination is
reachable in the clock's real RF state.

Factory clears byte 488 in this branch family only when it is set and BSS mode
is enabled. The word-36-zero path calls rearm; the other path records PM 480/484.
Modern code can clear it with fallback mode too, after checking the station
object at `g_ic+16` and its pointer at offset 228. With that second object present,
its byte 820 allows the clear when zero, or when the third callback argument is
nonzero. The timestamp/rearm and clear are verified together. Missing first
object logs and returns without the clear; missing second object skips it. Field
820's protocol meaning and those objects' lifetime are not yet proven here.

The matched start bodies contain a byte-488 clear and later byte-14 enable;
the stop bodies contain a byte-14 clear. Their complete dynamic control flow,
cancellation and all state transitions still need tests. Neither a single clear
instruction nor a passing selected null-completion family proves full lifecycle.

## Coverage and evidence

Private Unicorn RV32 tests perform **12108 executions**: 2664 old predicate
cases, 36 old reset cases, 4608 data-completion cases per image and 96 selected
null-completion cases per image. All 213 instruction starts in the predicate,
reset and both data-completion bodies were visited. Partial null coverage is
explicit: factory 61/174, native 92/213. TIM/start/stop were statically matched
only and have zero dynamic visits in this checkpoint. Complete PM object writes,
configuration preservation, callback order, stack and callee-saved registers are
checked against separate models.

Six static controls reject swapped SDKs, truncation, neighboring code, changed
PM/configuration anchors and a changed 100-ms constant. Five evidence controls
reject altered counts, boundary effects, pending clear, coverage and function
bindings. The archive `factory-keep-alive-validation-20261025.json` pins twelve
sources and one 33297-byte gzip report. Deterministic case traces have SHA-256
`580afa03dd10ac51fd0d3aa5d0dd0506e9894e66a4547ce120248b6931904bd5`.

```powershell
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& $py -B -X utf8 Small_TV/src/tests/verify_keep_alive_evidence.py `
  --proof Small_TV/qemu/parity/factory-keep-alive-validation-20261025.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --old-pp C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libpp.a `
  --new-pp C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libpp.a
```

No production firmware, QEMU, frozen producer or physical device was changed.
Next: complete TIM/start/stop and null-failure transitions, identify the actual
station object/flag lifetime and negotiated BSS period validation. The observed
changes are consistent with a refactored SDK keep-alive mechanism; this is an
inference, not proof of full radio or clock equivalence. Whole-image aliases,
undefined-function gaps, independent final gates and hardware remain open.

Continuation: [WIFI_PM_LIFECYCLE.md](WIFI_PM_LIFECYCLE.md) now executes the full
start/stop bodies and selected real cancellation helpers, including the ROM
sleep-delay entry. 5224 cases cover repeated calls and retained-state restarts.
Transitive cancellation of modern timer 492 and actual ROM binding still need
runtime evidence; TIM and other null-completion branches remain open.

Continuation 26 October: [WIFI_TIM.md](WIFI_TIM.md) executes both complete TIM
bodies, 4808 cases with all 168/128 instruction starts, against the saved current
app8758BD09/ELFDA1ED0CE. The historical reference and its guards remain intact.
Other null-completion branches, station/peer lifetime and BSS producer ranges
remain open; external scheduler/RF/slice helpers are not a full protocol proof.

Continuation 28 October: [WIFI_NULL_COMPLETION.md](WIFI_NULL_COMPLETION.md) now
executes the complete null-completion parents, real quick-wake and state setters:
16662 executions, all 174/213 parent starts and all 40/38 + 27/27 helper starts.
The station/peer pointer gates are checked, but actual concurrent lifetime,
callback producer contracts and negotiated BSS ranges remain open.
