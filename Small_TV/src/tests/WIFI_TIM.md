# Complete TIM handler comparison

26 October 2026. Continuation of [keep-alive](WIFI_KEEP_ALIVE.md),
[PM lifecycle](WIFI_PM_LIFECYCLE.md) and [event lifetime](WIFI_EVENT_LIFETIME.md).
This checkpoint closes the previously unexecuted TIM bodies, not the remaining
null-completion, station lifetime or full radio requirements.

## Exact linked inputs

Factory ELF remains `8c9fd166…`. Native TIM is independently rebound to the saved
production app `8758bd09…` / ELF `da1ed0ce…`, after the Storage fixes. The historical
ELF `9e4ec88d…` remains a separately required reference; its old identity guards
are unchanged. `reverse/timer_tim.py` verifies the new app/ELF descriptor pair,
matches nine complete native SDK bodies, checks direct calls, shared object-local
anchors, PM/configuration sizes, event-11 table entry and OSI forwarding wrappers.
The old and new `libpp.a` hashes are still checked before reading objects.

The complete matched TIM bodies are 488 bytes at factory `0x4039061c` and 356 bytes
in the current native image. No binary, shared SDK, QEMU or production source was
patched. The test uses fresh private RV32 state for each call.

## Observed behavior

Both versions give the first nonzero argument priority. In PM state byte 1 equal
to one, that path checks the 5000 threshold, records activity at byte 20, requests
wake and increments counter 8. A rejected slice writes byte 27 instead. With only
the second argument set, they check 1000, enable the dream timer and increment
counter 12. Counters wrap at 32 bits. Where a future PM timestamp at offset 112
requests OSI slot 408, the first path passes the low word of the difference;
the second caps the full 64-bit difference at PM word 60. This is arithmetic,
not a software wait.

The factory TIM first calls the actual `pm_keep_alive` predicate, even when its
later PM state branch returns immediately. With neither argument set, it may
request a null frame instead of sleep. In the other eligible branch it can
request a null frame with argument zero. Enabled BSS mode also sets pending
byte 488. Modern TIM has none of those predicate/null requests; the separate
event-11 keep-alive mechanism was examined in the previous checkpoints. These
differences do not by themselves establish a missing native feature.

Synthetic fixtures cover state bytes 0/1/2/255, both argument priorities,
slice acceptance/rejection, activity flags, active-timer state, BSS/fallback
predicates, exact elapsed-time equality, wrapped clocks, signed threshold
extension, future/past deadlines and differences spanning multiple clock words.
This does not assert that all synthetic combinations are reachable through RF.
Negotiated BSS range/overflow producers still need their own qualification.

## Test and evidence

`tim_test.py` performs **2404 cases per image / 4808 executions**, comparing every
PM write, both counter words, ordered external calls, untouched configuration,
stack restoration and callee-saved registers against a separate model. Every
TIM instruction start is visited: **168/168 factory and 128/128 native**. The real
factory predicate executes as part of the call, not as an expected-result stub.
Full instruction coverage is not full path or protocol coverage.

The slice decision, RF null request, scheduler, sleep/dream/wake and OSI platform
operations are explicitly external boundaries. Their caller-saved registers are
poisoned on return; the clock returns its actual RV32 `a0/a1` pair. Reads outside
the declared PM/configuration, two counter words, OSI cells and private stack
fail. The test proves selected handler effects, not those helpers' transitive
semantics or hardware timing. No production defect was found in these cases.

Nine static controls reject a historical image in place of the current one,
changed app/ELF, swapped SDKs, truncated reference and four actual body mutations
(PM byte-20 store, 5000 constant, OSI 408 slot and counter increment). Those last
four exercise object matching below the whole-image hash guard. Six evidence
mutations reject changed execution counts, counter wrapping, capped intervals,
pending writes, coverage and current-image identity.

The [proof](../../qemu/parity/factory-tim-validation-20261026.json) archives the
full qualified bodies and deterministic observations. Its consumer rehashes all
inputs and source pins and reruns all 4808 instruction executions.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
& $py -B -X utf8 Small_TV/src/tests/verify_tim_evidence.py `
  --proof Small_TV/qemu/parity/factory-tim-validation-20261026.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --reference C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --native .build/nvs-storage-fixed-20261026/small_tv_reconstructed.elf `
  --app firmware/development/small-tv-esp32c2-reconstructed/app.bin `
  --old-pp C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libpp.a `
  --new-pp C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libpp.a
```

Next: remaining null/failure completions, actual station and peer-object
lifetimes including field 820, negotiated BSS setters/ranges, computed aliases
and whole-image reachability. Deferred points 1–3, full regression, 24-hour
acceptance and physical hardware remain open. No live VM is pending.

Continuation 28 October: [WIFI_NULL_COMPLETION.md](WIFI_NULL_COMPLETION.md) covers
the previously missing null-completion branches and real quick-wake/state helpers
on this same saved native pair. Actual station lifetime and producer contracts
remain separate requirements.
