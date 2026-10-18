# Playlist index fault regressions

The [negative control](negative-rename-loss.log) runs the original C3 builder
and injects a failure of the final rename: the old index disappears. The fix
uses the shared recoverable file publication helper and restores a retained
backup on boot. Missing CSV leaves the old index/count untouched.

The [executable report](report.json) compiles actual parser/index/lookup
functions with ASan/UBSan and real host stdio. It covers exact Arduino-compatible
uint32 offsets, indexed lookup, rename/write/flush/close failure, backup recovery,
missing CSV, overlong row continuation, empty playlist, final line without a
newline, and malformed index size. Long input is drained to its row boundary;
a trailing chunk can no longer become a phantom station.

The existing JavaScript upload contract referenced handlers removed by the
earlier streaming upload refactor. It now checks the current shared streamed
publication path. This structural check supplements executable index tests.
SPIFFS persistence under actual power loss and stale CSV/index matching remain
separate checks before completing transfer stage 06.
