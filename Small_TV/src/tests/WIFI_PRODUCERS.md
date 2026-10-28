# Null-frame producers and a conditional BSS timer defect

28 October 2026. Continuation of [null completion](WIFI_NULL_COMPLETION.md).
The complete callback adapters and peer-to-PM BSS producer chain now execute in
private RV32 tests. This exposed timer-range defects when BSS Max Idle is enabled;
it is a **failing-before baseline**, not acceptance of those defects.

## What is now identified

Both callback adapters load a descriptor pointer from packet offset 36 and its
status byte at offset 19. Sleep forwards first argument one; wake forwards zero.
Factory leaves the third argument untouched and its parent does not use it.
Native additionally forwards descriptor word zero masked with one. Thus the
earlier synthetic parent arguments have real producer bindings. The status
byte's driver-level enum and the descriptor flag's name still need tracing;
equality to one is proved, but a semantic name is not guessed from that equality.

`ieee80211_set_bss_max_idle_period` copies little-endian IE bytes 2/3 to peer
halfword 818 and IE byte 4 bit zero to peer byte 820, with no period clamp.
`sta_recv_assoc` calls it for the BSS Max Idle IE when support is enabled.
`cnx_sta_pm.part.0` subsequently reads peer 818, calls the real PM setter, and in
native explicitly rearms the timer. Field 820 can now be described as the BSS
Max Idle options bit, rather than an unidentified general station flag.

The pinned SDK header `esp_wifi_types_generic.h` defines the BSS period unit as
1.024 seconds and names the corresponding option `protected_keep_alive`.
That supports interpreting the bit as requiring protected keep-alive frames;
the exact store/consumer relation comes from the matched machine code.
The earlier null-completion tests show how byte 820 and the forwarded flag gate
pending clear. They do not establish object ownership or concurrent lifetime.

The PM initializer materializes both callback pointers. `wifi_hmac_init` binds
the transmit producer. The actual transmit producer reads the same station/peer
chain and may choose `ieee80211_encap_keep_alive_data` instead of ordinary null
encapsulation. `pm_go_to_wake` also calls completion directly with `(0,1,0)` in
two branches. These larger bodies are fully matched here, but not all dynamically
executed. Runtime registration and the additional wdev function-table alias
remain separate requirements.

## Conditional timer failures

Native stores the full peer period, but its microsecond rearm arithmetic is
32-bit. With IE period **4197**, real IE → peer → connection → setter → rearm
instructions pass **760704 microseconds** to OSI slot 240 instead of the intended
**4295728000 microseconds**. Period 4196 is still representable. The arithmetic
inventory finds wrapping for 61339 of the 65535 nonzero 16-bit periods. That
inventory is mathematical; it is not an assertion of 65535 CPU executions.

Factory uses a different representation. Its setter doubles `(period-4)` and
narrows to 16 bits for larger periods. At raw period **32772**, the actual setter
stores encoded period zero while leaving BSS mode enabled; OSI slot 224 then
receives a zero interval. Both failures are preserved in explicit machine-code
witnesses and the evidence consumer rejects a claim that the safety gate passed.

The saved production `sdkconfig` has `CONFIG_ESP_WIFI_BSS_MAX_IDLE_SUPPORT` off.
The actual SDK getter tests bit 8 of menuconfig word 64; tests cover that getter
with controlled values. This checkpoint does **not** observe the running board's
or VM's menuconfig word and does not claim ordinary Small TV traffic triggered
either failure. It also does not establish all validation preceding the
association call. Full association receive code is matched, not executed here.
The feature stays disabled; enabling it is not an implicit part of this task.

Next correction should preserve the full valid period rather than truncate or
clip the negotiated value. A millisecond timer can represent the complete
16-bit BSS interval. Preserve existing microsecond/fallback behavior where it
fits; verify exact units, rounding, cancellation and all internal callers.
An isolated GNU RV32 `--defsym` experiment confirms that a local function can
replace a symbol even for calls from the SDK's same object. The SDK PM objects
are global symbols, so no hard-coded data addresses or shared-SDK edit is
required. This is feasibility evidence only; no production correction is yet
implemented. Preserve this worktree's current app/ELF/source proof inputs and
perform the correction in a separate task worktree.

## Qualified code and instruction evidence

The original factory ELF `8c9fd166…`, historical reference `9e4ec88d…` and current
app `8758bd09…` / ELF `da1ed0ce…` remain pinned. Old/new `libpp.a` and `libnet80211.a`
are checked before their objects are read. `reverse/wifi_producers.py` matches
twenty complete bodies / 5322 linked bytes against the proper SDK objects:
the two adapters, `pm_go_to_wake`, `pm_attach`, transmit producer,
`wifi_hmac_init`, connection producer, complete association receiver, IE setter
and enablement getter in each image. Global/absolute targets and object-scoped
local anchors must agree with the previously qualified PM closure.

**25266 CPU executions** compare 7424 callback cases, 5200 BSS chain cases and
nine feature-getter cases per image. Every status byte and every IE option byte
is exercised; representative independent descriptor bits, period boundaries,
absent IE retention, PM context and fallback are covered. Callback adapters run
into the complete real completion/quick-wake/state closure. IE stores remain in
the same private peer memory when connection/PM setter/rearm execute.
All 119 instruction starts / 344 bytes in the ten small producer bodies are
visited. This does not make the larger matched initialization/receive bodies
dynamically covered or prove protocol-wide reachability.

The PM-start call is an explicit boundary with all seven arguments checked;
full PM start/stop behavior was tested separately. Timer platform operations,
RF/slice/scheduler, off-channel callbacks and logging remain external. Packet,
descriptor, IE and untouched PM/configuration/peer bytes are read-only or changed
only by their declared writes. Stack and callee-saved registers are checked,
and external calls poison caller-saved registers. Log tests record the fixed
prefix, not constant format-string/vararg addresses.

Five static controls reject swapped network libraries, truncated callback,
changed status offset, peer-period offset and option mask. Eight evidence
controls reject changed arguments/options/delay, a false safety claim, changed
build feature state, body extent or a false lifetime claim.
The [baseline proof](../../qemu/parity/factory-wifi-producer-validation-20261028.json)
pins sources and a bounded compressed report. Replay preserves the failing gate:

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
& $py -B -X utf8 Small_TV/src/tests/verify_wifi_producer_evidence.py `
  --proof Small_TV/qemu/parity/factory-wifi-producer-validation-20261028.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --reference C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --native .build/nvs-storage-fixed-20261026/small_tv_reconstructed.elf `
  --app firmware/development/small-tv-esp32c2-reconstructed/app.bin `
  --old-pp C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libpp.a `
  --new-pp C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libpp.a `
  --old-net C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8/libnet80211.a `
  --new-net C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2/libnet80211.a `
  --sdkconfig firmware/development/small-tv-esp32c2-reconstructed/sdkconfig
```

Production code, SDK, QEMU and physical devices are unchanged. No VM was started.
Correction, runtime feature state, caller status/flag enums, actual object
lifetime, association input bounds, wdev/computed aliases and whole-image gaps
remain open, along with deferred points 1–3 and final full/24-hour/hardware gates.
