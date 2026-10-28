# Complete null-completion and quick-wake comparison

28 October 2026. Continuation of [keep-alive](WIFI_KEEP_ALIVE.md) and
[TIM](WIFI_TIM.md). The previous selected null-completion family covered only
61/174 factory and 92/213 native instruction starts. This checkpoint executes
the previously missing parent branches and two real helper algorithms.

## Exact code and coverage

Factory remains ELF `8c9fd166…`. Current native remains production app
`8758bd09…` / ELF `da1ed0ce…`; historical reference `9e4ec88d…` is checked
separately. Existing identity guards and proof inputs are unchanged. The new
`reverse/tx_null.py` extends the strict TIM qualification, matches four complete
helper bodies against their own SDK's `pm.o`, verifies actual parent targets,
shared/local data anchors, public/absolute native symbols and counter binding.
The quick-wake helper is object-local; its identity is checked through the
matched callers, not an assumed global-symbol namespace.

| Function | Factory address / bytes / starts | Native address / bytes / starts |
| --- | --- | --- |
| `pm_tx_null_data_done_process` | `0x420759cc` / 514 / 174 | `0x4207afd2` / 634 / 213 |
| `pm_tx_null_data_done_quick_wake_process` | `0x4207595a` / 114 / 40 | `0x4207af68` / 106 / 38 |
| `pm_set_state` | `0x42074aec` / 78 / 27 | `0x4207a10a` / 78 / 27 |

All **519 instruction starts / 1524 linked bytes** in these six bodies are
visited. Tests perform **8331 cases per image / 16662 executions**:

- 4608 parent decision combinations;
- 1024 parent-to-quick-wake cases;
- 864 sleep/deadline cases;
- 864 pending/station/peer gate cases;
- 720 retry-boundary cases;
- 216 direct quick-wake cases and 35 direct state-setter cases.

Every ordered PM write, counter store, named boundary call and guarded station
read is compared against a separate model. Whole remaining PM/configuration
buffers, stack restoration and callee-saved registers are checked. External
helpers poison caller-saved registers; the clock returns the full `a0/a1` pair.
Real reset/rearm, quick-wake and state-setting algorithms execute unchanged.

## Confirmed differences and retained behavior

The second callback argument equal to one controls the local completion flag.
Its full driver-level status meaning and the other arguments' producer contract
are not inferred from a function name. The tests retain neutral argument names.
Old code also calls the timestamp reset on this equality; native does not.

Factory forces its local ready branch when PM byte 15 is zero or byte 16 is
nonzero. Native additionally considers pending byte 488. With pending set,
those states can take the retry branch when the second argument is not one;
the first argument and retry byte 9 can override this choice. The difference
affects ordered writes, retry requests, counters and the off-channel callback
argument. It is preserved as an observed SDK difference, not declared a new
firmware defect or copied from factory into native code.

In the ready branch, native reads `g_ic+16` only when pending is set. A null
station pointer logs and returns before reading the peer pointer. A null peer
pointer skips field 820. A present peer's byte 820 and the third argument gate
rearm/timestamp/pending clear. Tests assert those exact read sequences, including
no station dereference on the other branches. This verifies pointer gates, not
whether a nonnull object can be freed concurrently; actual lifetime remains open.

The ready branch also clears activity/retry flags and can call quick-wake. Both
quick-wake versions share the tested decision algorithm: inactive timer returns
one, completion can reset beacon timeout, byte 19 clears with OSI 412 / RX PTI
operations, byte 20 or an idle TX queue permits progress; otherwise a null request
may be issued. A synthetic noncanonical byte 19 can be returned unchanged, so
the test does not silently normalize this helper's result to boolean one.
Both state setters emit GPIO boundary calls only on a state change and always
store the low byte of the requested state.

For sleep selection, native adds PM byte 543 and the 64-bit deadline at 568/572.
When eligible, a time before that deadline requests the sleep-delay timer;
at or after the deadline it requests sleep. Factory lacks this deadline branch.
Before/equality/after, low-word rollover and high-word differences are tested.
These are comparisons and timer requests, not a software spin delay. Both
versions' 32-bit counters wrap; the second retry byte also wraps at 255. The
first retry byte's threshold is tested at 15 and 16, with no assumption that
every synthetic state is reachable by RF.

## Evidence and limits

Nine static controls reject swapped SDKs, a historical image passed as current,
truncated/neighboring quick-wake code, a changed active flag and four literal
native parent mutations (pending byte, deadline high word, deadline flag and
retry threshold). The last four test matching below the full-image hash guard.
Eight evidence controls reject altered counts, ready effects, station reads,
deadline choice, wrapping counters, helper return value, coverage and an
unsupported claim that pointer lifetime has been proved.

The [proof](../../qemu/parity/factory-null-completion-validation-20261028.json)
pins the source files and archives the complete qualification and observations.
Its independent consumer rehashes every input and reruns all 16662 executions.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
& $py -B -X utf8 Small_TV/src/tests/verify_tx_null_evidence.py `
  --proof Small_TV/qemu/parity/factory-null-completion-validation-20261028.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --reference C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --native .build/nvs-storage-fixed-20261026/small_tv_reconstructed.elf `
  --app firmware/development/small-tv-esp32c2-reconstructed/app.bin `
  --old-pp C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libpp.a `
  --new-pp C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libpp.a
```

No production bug was established in these fixtures. No production source,
shared SDK, QEMU, physical device or firmware image changed. Scheduler, RF/null
transmission, slice acceptance, sleep/dream/wake, beacon/hardware operations,
GPIO and off-channel callbacks remain explicit external boundaries. Full
instruction coverage is not all protocol paths or concurrent lifetime proof.
No new VM or physical test was started.

Next: actual callback producer/status contracts and station/peer lifetime,
including field 820; negotiated BSS setters/ranges/overflow; computed aliases and
whole-image reachability. Deferred points 1–3 and full/24-hour/hardware acceptance
remain open. This checkpoint does not replace any of those requirements.

Continuation: [WIFI_PRODUCERS.md](WIFI_PRODUCERS.md) now executes both callback
adapters into this exact parent closure and identifies field 820's IE producer.
It preserves a conditional BSS timer-range failure; concurrent lifetime, full
association validation and runtime enablement remain open.
