# Event-11 registration and observed SDK state

25 October 2026. Continuation of [event-11 algorithms](WIFI_TIMER_EVENT11.md).
The previous turn was progress: commit `7d8b50d88` retained the eight-body
comparison. This checkpoint follows the user's factory-comparison priority;
the broader improvement plan and its deferred acceptance gates remain open.

## Static and instruction evidence

The factory/native ELF identities remain `8c9fd166…` / `9e4ec88d…`.
`reverse/timer_event11_registration.py` rechecks the preceding anchors and exact
old/new `libpp.a`, then adds pinned `libnet80211.a` API implementations.
Full bodies are matched with declared relocations and local control flow:

| Function | Factory start, bytes | Native start, bytes |
| --- | --- | --- |
| `esp_wifi_init_internal` | `0x42068a9a`, 290 | `0x4206d278`, 290 |
| `wifi_osi_funcs_register` | `0x4206819e`, 104 | `0x4206c980`, 100 |
| `pm_attach` | `0x42076792`, 486 | `0x4207bcd6`, 486 |
| Event-11 timeout producer | `pm_max_idle_timeout`, `0x42074b4a`, 8 | `pm_keep_alive_timeout`, `0x4207a022`, 8 |
| `pp_timer_process` | `0x4207b16e`, 22 | `0x42079f22`, 22 |
| `pp_timer_register_post_cb` | `0x4207b162`, 12 | `0x42079f16`, 12 |

The actual OSI slot-236 forwarders are also checked: factory 14-byte body at
`0x420962d0` calls `0x4207b3f4`; native 4-byte tail jump at `0x4209378c` targets
the real `ets_timer_setfn` symbol. These adapters are in flash, unlike some
previously checked arm/disarm wrappers. Callback locations must come from each
actual table, not a guessed generic IRAM wrapper address.

The real registration routine accepts only its own ABI version and footer
`0xdeadbeaf`, returning `0x102` for invalid first registration. Once the global
pointer is nonzero, both SDKs return success immediately without replacing it
or validating the new argument. A null outer initialization configuration is
rejected before registration. Tests retain these distinctions explicitly.

There are 48 registration/gateway states per image: existing/unset global,
null/nonnull argument, correct/other/invalid ABI and correct/invalid footer.
The gateway executes the actual initialization entry and real registration,
then an explicitly stubbed API-lock failure returns control before the rest
of Wi-Fi initialization. **Later initialization branches are not covered**:
26/99 factory and 25/98 native entry instruction starts were visited.

In both images all instruction starts of the other five SDK bodies and setfn
forwarder were visited. Real `pm_attach` first passes its full 544/584-byte
object to an explicit memset backend stub. Every direct PM store is compared
with an independent model, including untouched fields and both initial fills.
It registers the same ten timer offsets. Offset 492 selects the exact event-11
producer with a null callback argument. Initial bytes 14/15/16/488 are 0/1/0/0;
word 36 is 1. This does not identify the later connected-state flag writers.

The captured callback is invoked through its stored address. The real
`pp_timer_process` posts outer event 8 with parameters `{11,0}` to the installed
post callback. Absent callback returns `0xffffffff`; installing/removing it and
returning 0, 1 or a negative status are tested. This checks posting, not queue
delivery or RF effects. Timer creation, TX-callback registration, clock, TSF and
logging helpers remain explicit stubs. Stack and callee-saved registers are
checked, with caller-saved registers poisoned at helper boundaries.

## Read-only observations from real firmware VMs

Two fresh owned VMs booted the unmodified factory dump and native C912/9E4E
application on QEMU main `2df90327…`. Only their disposable flash copies were
seeded with synthetic settings. The test waited for the normal station page,
stopped coherently via QMP, read bounded numeric metadata, and resumed before
quitting. Both original process IDs were subsequently absent. UART contains
one ROM boot each and no panic/assertion. Three protected duration/control VMs
were not connected to or modified.

The actual global OSI pointer selects the previously qualified table in each
image; all 480 bytes have the expected SHA. Both post callback slots are
nonzero. The offset-492 timer has initialization marker `0x12121212` and an
SRAM handle; its backend callback structure has not been dereferenced or proven.

| Connected-state observation | Factory | Native |
| --- | ---: | ---: |
| PM bytes 1/14/15/16/488 | 0/1/1/0/0 | 0/1/1/0/0 |
| PM word 36 | 1 | 1 |
| Configuration enable byte 52 | 0 | 0 |
| Stored period word 72 | 60 | 30 |
| Fallback word 28 | 10000000 | 10000000 |
| Adjustment word 56 | 0 | 500000 |

The stored period difference is inactive in these snapshots. It is not proof
of different clock timing. The old SDK separately contains `pm_keep_alive`;
compare that path with the new fallback timer before calling the consolidation
a missing feature. These snapshots do not exercise BSS Max Idle negotiation,
prove radio equivalence or establish all reachable combinations of PM flags.

## Reproduction and next work

`factory-timer-registration-validation-20261025.json` pins 14 source files and
five compressed records (27614 bytes): instruction matrix, runtime report,
numeric owner observation and both UART logs. Runtime records retain only the
decoder's explicit numeric reads, including the pointer table, for offline
reconstruction. No stack, credentials, packet payload or complete RAM is saved.
The consumer reruns all selected instruction checks and replays the raw typed
reads. Four static mutations and six runtime evidence mutations are rejected.

```powershell
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$old='C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8'
$new='C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2'
& $py -B -X utf8 Small_TV/src/tests/verify_timer_registration_evidence.py `
  --proof Small_TV/qemu/parity/factory-timer-registration-validation-20261025.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --old-pp "$old/libpp.a" --new-pp "$new/libpp.a" `
  --old-net "$old/libnet80211.a" --new-net "$new/libnet80211.a"
```

Next: follow `pm_start`/`pm_stop`, writes to the pending flag and the old
`pm_keep_alive`/reset path; compare their reachable behavior with native fallback.
Then trace negotiated period validation and timer cancellation, including
overflow boundaries. Full event delivery, actual backend callback ownership,
all initialization branches, RF, whole-image aliases/function gaps, long-run
acceptance and physical-board gates remain unproven. No firmware behavior was
changed solely to reproduce an older SDK implementation.
