# C3 AP timeout execution

The runner first retrieves the exact pre-fix `1256de595` C3 network and settings
sources from Git. Actual startup/AP setup captures the real timer callback;
three named safety assertions must fail after OTA reservation, late GOT_IP or
a successfully persisted zero. These are old-behavior negative controls.

Current production AP facts/helpers, RSSI owner loop, event callback, startup,
manual retry and sleep preparation execute as exact frozen source spans. The
complete current runtime_settings.c translation unit executes with controlled
NVS results. The active credential loader supplies at most one startup profile;
it is explicitly a loader seam, not storage parsing evidence. No test writes
AP facts, phases, ACKs or owner deadlines. A pthread parks at actual vTaskDelay
and SDK barriers; virtual clocks, negative/saturated inputs and concurrent real
setting saves/events drive decisions. SDK layouts/observations, activity CAS
and reboot reservation are explicit field-model seams. Actual C3 reboot lease
internals and shared power policy have separate suites. This is not a complete
firmware reconstruction or proof of RF, RTOS/ABI, flash power loss, heap/HWM or
physical deep-sleep timing. The final eligibility check is the application
arbitration boundary; later asynchronous RF/config events cannot be atomically
excluded by the SDK restart operation. No board is accessed.

Forty-two positive cases cover exact one/30-minute deadlines, actual settings
save/revision and NVS failures, two concurrent writers, online/disable/manual
changes, activity/OTA arbitration, live association/netif/IP errors, blocked SDK
queries and cancellation, and invalid clocks. Submitted connects have a 20-second
grace period. Expiry of that grace never proves SDK completion: an expired AP
interval first checks live disconnection and explicitly cancels the old intent.
Only an unchanged intent with ESP_OK acknowledgement is cleared, and a new full
interval plus fresh live proof is required before restart. New events/intents
cannot be cleared by an old cancel return; asynchronous SDK/RF cancellation is
not claimed atomic. Failed cancellation/admission conservatively rearms.

Eight exact current-source semantic controls must fail their named assertion:
missing final check, ignored arming/final settings revisions, bypassed reboot
reservation, restarting without pending-intent cancellation, clearing a newer
intent with an old cancellation, rearming from a stale pre-SDK timestamp, and
ignoring revision exhaustion. A separate actual-settings TU variant seeds only
the static boot-local packed revision at its maximum for exhaustion admission;
this is explicitly a test initialization seam, not an attainable NVS restore
state or an owner/private-phase write. Actual normal initialization also loads
valid/invalid raw persisted delays without rewriting the NVS record.
Compile failures, sanitizer crashes and timeouts never count as detection. All
frozen current inputs are checked again after the complete run.
