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
