# Shared station controller and CYD HTTP integration

- [Controller](controller/report.json): actual common implementation, each
  target's actual state functions, real host mutexes/files; indexed Play/Next /
  Previous/wrap, Stop/Toggle while connecting, PCM/EOF/stale transitions,
  SmartStart and saved-station boot restore, invalid saved item, NVS failure,
  coherent controller snapshot and 500 concurrent commands per target.
- [SmartStart negative control](negative-smartstart.log): setting returned an
  NVS error while leaving its runtime value changed. The fix restores the old
  value on failure of the explicit settings operation.
- [C3 index](index-c3/report.json), [CYD index](index-cyd/report.json): actual
  shared parser/build/lookup with storage failures and backup recovery.
- [C3 commands](c3-commands/report.json): actual Play/Stop/Resume ordering,
  pending publication and queue-failure cleanup; 2,000 concurrent operations.
- [C3 metadata](c3-state/report.json): stale callback and contended state
  regression remains passing after adding pending state.
- [CYD lifecycle](lifecycle/report.json): six queue/codec variants, pending /
  Stop/stale/queue-failure cases and existing EOF/drain/resource/output tests.
- [CYD HTTP](http/report.json): actual radio handler and strict station-number
  parser, all seven valid commands, fifteen invalid queries, control errors /
  unavailable service, maximum escaped JSON, and compatible Stop fallback.
  Existing 42 stream cases, actual health handler and status JSON continue.

All executable campaigns use ASan/UBSan. The controller's audio and NVS APIs and
the HTTP request/query APIs are seams; no codec arithmetic, kernel scheduling,
flash power-loss durability or physical playback result is claimed here.
The initial SmartStart setting is disabled. Hardware-specific C3 controls,
display and output driver changes are excluded. SDK firmware/static analysis
follow this host checkpoint. Stale CSV/index pairing remains stage 06 work.
