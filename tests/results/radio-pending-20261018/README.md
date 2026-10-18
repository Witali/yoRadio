# Preserve accepted Play through HTTP startup

The extended [negative test](negative-stream-start.log) calls the actual CYD
stream task and inspects state inside the HTTP open seam. It exposed a gap in
the newly added pending feature: the task's ordinary stopped-state update
cleared pending before opening the connection.

Both targets now use one atomic per-generation `native_state_set_connecting`
transition from Play and the stream task. It sets pending/playing/format under
one state mutex, without an intermediate stopped state. Old generations cannot
restore connecting after Stop or confirmed PCM. Queue failure and terminal
paths continue to clear pending.

- [CYD HTTP](http/report.json): all existing stream cases now assert pending
  at each HTTP open, including redirects/retry; API/status/health tests pass.
- [CYD lifecycle](lifecycle/report.json): all six queue/codec branches pass.
- [C3 commands](c3-commands/report.json): real Play/Stop/Resume with queue failure
  and 2,000 concurrent commands remains passing.
- [Common controller](controller/report.json): both real state implementations,
  stale connecting rejection after PCM, Toggle/Stop/EOF and 500 concurrent calls.

All campaigns use ASan/UBSan with documented platform seams. This corrects the
software state contract; physical connection timing has not been measured.
