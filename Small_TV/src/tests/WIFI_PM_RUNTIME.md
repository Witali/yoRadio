# Real station loss: PM ownership and keep-alive cancellation

The current native image cancels its keep-alive timer during a real station
disconnect. The missing direct call in `pm_stop` is **not a cancellation defect
in this observed path**. `cnx_sta_leave` calls `pm_stop` at `0x42070acc`, then
`pm_disable_keep_alive_timer` at `0x42070ad0`. The helper tail-calls the actual
legacy disarm backend and returns to `0x42070ad4`. Hardware breakpoints observed
the timer still armed on helper entry and disarmed on return.

This follows the [private start/stop instruction tests](WIFI_PM_LIFECYCLE.md).
Factory cancellation is inside `pm_stop`; the newer SDK places this cancellation
at the station-leave call site. No SDK or application patch was justified here.

## Qualification before live reads

`tools/reverse/pm_runtime_layout.py` first requalifies the preceding complete
PM bodies against the exact original ELF, native ELF, SDK libraries and ROM.
It derives native `esp_timer` and `_ETSTIMER_` fields from the actual linked
DWARF compilation units. The backend `alarm` is an eight-byte field at offset
zero; the native allocation is 32 bytes. The legacy marker is at offset four
and its backend handle at offset 16.

The factory backend is qualified independently, using its literal 14-byte
alarm predicate, 18-byte initialization predicate and actual disarm handle
load. Only the eight-byte prefix is claimed for the old backend; the native
allocation size is not projected onto it. The private RV32 test executes both
whole factory predicates, including high-word-only nonzero alarms, without
stubs, writes or stack accesses.

The decoder permits at most 32 numeric reads / 256 requested bytes. It rejects
short responses, invalid station states and unaligned/out-of-SRAM backend
pointers. It follows a handle only when the initialization marker is valid
and the real ROM `g_pm_ptr` equals the qualified SDK PM object. Uninitialized
or unbound objects give an unknown timer state, not a fabricated inactive one.
No callback payload, stack, settings or credentials are read.

## Observed results

Owned disposable VMs used factory ELF `8c9fd166…`, native ELF `9e4ec88d…` /
app `c91294fc…`, ROM `289ce00e…` and QEMU `2df90327…`. Original flash and archived
production artifacts were unchanged. Each VM ran a seeded flash copy, real
HTTP requests and a natural station deauthentication when QMP disabled the
external AP. RSP changed only hardware breakpoints and normal run/pause state;
no guest memory, registers, PC or instructions were written.

| Native observation | PM active | Backend alarm | Application connected |
|---|---:|---:|---:|
| Connected after three HTTP 200 responses | 1 | 17535664 | 1 |
| Actual `pm_stop` epilogue | 0 | 17535664 | 1 |
| Keep-alive cancel helper entry | 0 | 17535664 | 1 |
| Return to `cnx_sta_leave` | 0 | 0 | 1 |
| Disconnect callback processed | 0 | 0 | 0 |
| Reconnected and HTTP available again | 1 | 20137076 | 1 |

The cancellation return was observed before the original alarm deadline, so
ordinary timer expiry does not explain this zero. The real ROM PM pointer,
OSI table pointer and initialized backend handle stayed bound to the same
object throughout. These instrumented virtual timestamps are not a physical
latency measurement.

The factory timer was already inactive at baseline and stayed inactive at its
real stop epilogue. That baseline cannot prove cancellation of an armed factory
timer. More importantly, factory HTTP did **not** recover within the bounded
30-second host wait after the AP returned. The PM active byte stayed zero;
the application station hint remained two. The combined runtime report
therefore retains `passed: false`. Native recovery does not waive that result.

Factory assembly at `0x4200c652..0x4200c66a` calls `esp_wifi_connect` before
incrementing retries and storing state one. Its GOT_IP callback does not itself
store state two. Consequently this application hint cannot be used as a live
link bit or as proof of recovery. The current native callback already clears
its atomic connected flag before reconnecting and sets it on GOT_IP. The
factory stall's exact cause and whether it depends on QEMU remain open; the
observed idle-task PC does not identify a blocked callback's stack.

## Regression evidence and remaining scope

[Saved evidence](../../qemu/parity/factory-pm-runtime-validation-20261025.json)
contains five compressed raw records (9956 bytes): host qualification, mixed
runtime report, actual owner-absence observations and both UART logs. All
inputs are hashed. Both short VMs exited, with one ROM boot and no panic.
Earlier prototypes remain in ignored scratch and do not count as acceptance.

`verify_pm_runtime_evidence.py` replays both factory predicates and all numeric
reads, checks the native caller instructions directly in the ELF and preserves
the factory failure. Nine altered-evidence controls reject a fabricated factory
pass, missing cancellation, wrong caller, changed alarm, unbound ROM, extra
read, live owner, reset and unsupported full-lifecycle claim. The host decoder
also passes eight alarm cases, ten rejection cases and four uninitialized /
ROM-unbound cases.

This is one observed disconnect/reconnect path. Other callers of `pm_stop`,
TIM and null-completion branches, station object lifetime, negotiated BSS
period validation, full-image equivalence, RF and physical hardware remain
separate work. The existing long-run VMs were neither attached nor restarted.
