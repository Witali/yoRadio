# Shared network power policy

```text
python tests/run-network-power.py --out .build/network-power-01
```

The runner freezes sources before compilation and executes the complete shared
production component with a real pthread mutex as the portMUX boundary. Public
accept/receive/finish/invalidate/poll/snapshot APIs drive every state change.
Tests never alter the component's private state. Blocking driver callbacks let
new intent and snapshots execute while the real poll is in flight, then verify
recording of stale success, protection of a new retry budget, invalidation of an
old driver result, and convergence to current intent. Exactly one poll owner is
active at a time; concurrent publishers and snapshots run alongside it.

Sixteen cases include full 32-bit generation wrap, same-generation retry/EOF,
known idle with no redundant call, 250 ms failure spacing, three-attempt budgets,
clock saturation, invalid input and concurrent control. Four exact semantic
mutants must fail their intended assertions; compile, sanitizer and timeout
failures do not count as detections.

Integration cases also compile the actual frozen C3 apply_power, rssi_task,
intent wrapper and prepare_sleep function bodies. The real RSSI task runs on a
pthread with its vTaskDelay boundary as a controlled clock barrier. SDK field
models record requested power, RSSI polling and stop results. Tests verify that
only this task calls the power driver, policy reconciles every 100 ms while
RSSI uses 2 s, sleep stops new polls, failed prepare_sleep clears its guard,
and the next owner step repairs an intent changed during a blocked SDK call.
No audio generation, phase or ACK is set by these tests.

ASan/UBSan are mandatory. These host results do not measure real driver power
effects, RF behavior, hardware clocks, target ABI, FreeRTOS scheduling or SMP
safety. C3's unrelated RSSI validity behavior and audio ownership are qualified
separately. `--case` labels a partial campaign; source hashes, raw commands,
stdout/stderr and exact control failures are preserved in the output directory.
