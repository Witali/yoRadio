# CYD public vendor integration: host checkpoint

The current production decoder/output task bodies pass all six lifecycle
variants: Espressif, Helix and minimp3, each with fixed or adaptive input.
GCC 13.3 uses `-Wall -Wextra -Werror`, ASan, UBSan and leak detection.
The explicit codec/platform seams do not run Espressif's binary decoder.

New cases cover:

- 96 consumed header bytes in input packets of 17, 29 and 50 bytes, followed
  by EOF: 97 process calls, three one-tick yields, no PCM, clean close.
- Stop during the 32nd call's yield, while that call produced PCM: no stale
  format/PCM publication, no output write, decoder and workspace released.
- `NOT_SUPPORT` and `MEM_LACK` at Ogg open: distinct terminal reasons,
  unchanged numeric health errors, clean ownership and successful reopen in
  the same decoder task on the next generation.

The frozen control resets the scheduling counter before each input packet.
Its baseline compiles/runs with exit 0; the changed copy compiles with exit 0
and aborts at the intended `97 calls / 3 yields` assertion. The canonical
source was never mutated. This establishes that the regression catches the
cross-packet scheduling defect, rather than accepting any target crash.

Focused esp-clang-tidy 20 analysis of the actual production audio service and
SDK 6.0.2 compilation database finishes with exit 0 and zero errors. Its one
displayed warning is existing `stream_frames.h:47` enum zero initialization;
18 SDK/non-user warnings are suppressed by the configured tool. The changed
lines introduce no displayed warning. This is a focused check, not a new full
repository lint run.

Final run: `.build/cyd-vendor-public-lifecycle-20261030-04/`.
Earlier attempt 01 could not start installed WSL in the sandbox. Attempt 02
reached GCC and exposed a missing test-only `esp_err.h` seam after the existing
health-header include changed. Adding that typedef header fixed the harness;
attempt 03 passed, and attempt 04 strengthens the packet-boundary test.

`host-captures.zip` retains the final six test executables/logs, generated
production task bodies/platform headers, the frozen baseline/control, the
controller, source inputs, lint result and available earlier attempt logs.
`host-manifest.json` hashes every decoded member and the complete archive.
The SDK's existing compilation database is used only for focused static
analysis. These are host artifacts, not production firmware or physical-board
qualification.

The [integration design](../../../docs/CYD_ESPRESSIF_VORBIS_REUSE.md) records the
public contract, hardware differences, remaining native/production gates and
the separate custom decoder deferral.
