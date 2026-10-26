# Factory reconnect failure: application handlers removed after the first lease

The factory startup routine removes its IP and Wi-Fi application handlers
after the first successful connection. Subsequent `DISCONNECTED` events still
reach the default event queue and its SDK handler. The application callback
that requests reconnect is no longer registered. This explains the factory
recovery failures recorded in [the earlier PM comparison](WIFI_PM_RUNTIME.md).

The reconstructed firmware already retains these callbacks for its entire
network lifetime. A new test on the unchanged production image confirms
disconnect handling, timer cancellation, reconnection and HTTP recovery. The
existing correction is now documented with `FIXED_RECONSTRUCTION` in
`app/network/wifi.c::network_init`. Executable code and firmware binaries were
not changed by this checkpoint.

## Original instructions and live startup

The successful factory startup path at `0x4200cd90` writes station hint two.
It then performs these real calls:

| Call instruction | Unregister arguments | Observed return |
|---|---|---:|
| `0x4200cdae` | IP_EVENT, GOT_IP (0), callback `0x4200c602` | 0 |
| `0x4200cdc0` | WIFI_EVENT, ANY_ID (`0xffffffff`), callback `0x4200c602` | 0 |

Both target the default-loop unregister wrapper at `0x420aeae0`. The subsequent
path deletes the startup event group. The reconstruction uses atomic state
and its fallback worker for ongoing events; retaining a callback that uses
that deleted factory startup group would be unsafe.

Hardware breakpoints observed both calls and their successful returns during
a fresh factory boot. After ordinary HTTP readiness, the external AP was
disabled and restored through QMP. No guest instructions, memory or registers
were patched, and the host called no guest function.

## Delivery continues through the SDK

The driver posted WIFI_EVENT 5 with a 41-byte payload. Only numeric event
identity and size were observed; its payload was never exported.

| Observed boundary | Queue count | Executing task |
|---|---:|---|
| Before `esp_event_post_to` | 0 | Wi-Fi producer |
| Return from queue send, result 1 | 1 | Same producer |
| Return to driver, result 0 | 1 | Same producer |
| Dispatch callback `0x420456ea`, event 5 | 0 | Default loop task |
| Return from that SDK callback | 0 | Same default loop task |
| Final observation | 0 | No handler running on the loop |

The task identities come from the actual current-TCB leaf and the same loop
object's dedicated/running-task fields. Their addresses and the queue's
count/capacity/item-size fields are qualified from factory instructions.
The bounded decoder issues nine exact 32-bit reads, rejects invalid pointers
and dimensions, and reads no queue storage or task stack.

Thus the tested event is successfully enqueued, dequeued and dispatched.
Application callback `0x4200c602` remains absent after its observed removal;
the historical station hint two is not a live connectivity flag. The earlier
absence of the callback did not establish an emulator or SDK fault. No QEMU
change is needed for this diagnosed scenario.

## Independent algorithm and regression checks

`event_lifetime_test.py` executes original RV32 instructions in a private CPU:

- 24 cases exercise the complete 50-byte dispatch helper, visiting all 21
  instruction starts. Data-present/allocated flags, inline versus allocated
  pointer selection, event bases/IDs and callback arguments are checked.
  Payload reads and writes outside the private stack are rejected; preserved
  registers survive a callback that poisons caller-saved registers.
- Nine cases execute the selected 144-byte startup tail with explicit SDK
  unregister/delete/fatal boundaries. They check both unregister calls, their
  order, group deletion on success and error handling. This is a slice test,
  not execution of the complete initializer or real registry implementation.
- Nine native callback events check reconnect attempts, connected-flag clearing
  before the SDK call, retry exhaustion, a new lease and failure-latch reset.
- Six numeric geometry cases and 15 rejection controls cover pointer alignment,
  range/prefix bounds, counts, capacities, item width and truncated reads.

A separate fresh native QEMU run on app `c91294fc…` / ELF `9e4ec88d…` again
observed connected → disconnected → reconnected, including cancellation of the
same keep-alive backend and a working HTTP endpoint after recovery. Factory
and native used the same pinned QEMU `2df90327…` and ROM `289ce00e…`; the
immutable factory ELF is `8c9fd166…`. Both final VMs exited with one ROM boot
and no panic. This result covers one natural station loss, not RF or hardware.

[Evidence](../../qemu/parity/event-lifetime-validation-20261026.json) contains
six compressed raw records, 15223 bytes, with exact source and binary pins.
`verify_event_lifetime_evidence.py` repeats the private instruction tests,
replays both metadata decoders and rejects 11 altered runtime records. Controls
include an incorrect unregister result, wrong callback, a consistent forged
empty queue, wrong task identity, stale native connection state, extra reads,
live owner, reset and an unsupported full-lifecycle claim.

The diagnosed handler-lifetime gap is resolved as an intentional correction.
Other whole-image gaps, TIM/null-completion paths, negotiated BSS ranges,
other lifecycle branches, final duration gates and physical tests remain open.
