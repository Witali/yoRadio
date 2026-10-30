# Original Espressif Ogg/Vorbis baseline

This isolated SDK/QEMU diagnostic uses the unchanged Espressif 2.6.2 archives
from `esp-adf-libs` revision `67b8d0e98f58c774b8652480893037273190e8dc`.
It compiles the canonical CYD decoder registration and calls only supported
public simple-decoder interfaces. It selects no private repair, custom Vorbis
component, linker wrapper or numerical extension.

From the task worktree on Windows with the existing installed dependencies:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B tests/run-espressif-vorbis-qemu.py --target esp32 --output .build/espressif-vorbis-esp32-01
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B tests/run-espressif-vorbis-qemu.py --target esp32c3 --output .build/espressif-vorbis-c3-01
```

Each invocation needs a fresh directory strictly below `.build`. `--preflight-only`
checks installed file/byte pins without creating output or starting any tool.
`--prepare-only` verifies repository revisions and freezes inputs without compiling.

The known valid 48 kHz stereo q10 fixture has 15 Ogg pages, three Vorbis headers,
535 audio packets and final granule 528000. Complete PCM16 stereo output must
therefore contain 2112000 bytes. A full 4096-byte-feed warmup precedes the three
measured schedules: 4096, 257 and 1 byte. Each handle is closed before opening
the next. The diagnostic uses an ample 32768-byte PCM buffer and drains EOF
until no PCM remains. Every output byte enters SHA-256; the complete output
digest must be identical across warmup and all schedules. This full digest is
an observed vendor regression identity, not an independent PCM oracle.

Input fragments are offered at the declared size, including exactly one new
byte per feed in the smallest schedule. A successful call that produces no PCM
and consumes no input preserves its complete suffix through the same public
[`decoder_pending_input.h`](../../../idf/components/native_stream/include/decoder_pending_input.h)
owner used by the CYD task, then appends the next fragment. No bytes are skipped
or assumed consumed. The transcript records feed count, coalescing events and
maximum retained prefix; the one-byte case must exercise real coalescing.
No progress with an unconsumed suffix at EOF is an explicit failure. The shared
header is frozen alongside the diagnostic and checked for input immutability.

The retained [original C3 report](../../results/esp32c3-vorbis-lifecycle-20261004/report.json)
binds this same fixture and unchanged vendor archive, but records only 2107648
PCM bytes with SHA-256
`eb2037928cd89a1922fd9ae9d055c03b587484b7378c55b0f319d79980976144`.
Its [frozen public-API test loop](../../results/esp32c3-vorbis-lifecycle-20261004/sources/idf/esp32c3-oled-native/main/qemu_vorbis_lifecycle.c)
at lines 168 and 195–196 intentionally sends a separate empty EOF, calls it once
and closes the decoder. It does not drain the cached tail. That old result is
1088 stereo frames short of the fixture's final granule and cannot serve as
the complete-output reference for a drain-until-empty test. The new diagnostic
separately hashes exactly the first 2107648 bytes and still requires the exact
historical digest for this prefix. A prefix mismatch remains a failing result.

Warmup reports its before/after heap without assuming that first use releases
all persistent allocations. Each of the three measured streams must restore
the exact post-warmup free heap; their baselines must remain stable. The final
record reports heap before registration, after unregister and the observed
retained difference separately. It does not attribute that difference to
logging, codec ownership or another SDK service without additional evidence,
and it does not claim zero total retention when the difference is nonzero.

Worker core is 1 on ESP32 LX6 and 0 on C3 RV32; coordinator is core 0.
Priority 3 and stack 16384 are diagnostic settings. Assertions, stack canaries,
heap poisoning and idle watchdogs remain enabled. A one-tick delay after every
32 completed process calls lets idle run, including during one-byte header feeds.
No watchdog resets or yields are inserted inside codec arithmetic.

The controller retains frozen harness/registration/public headers/archives,
tool hashes, actual build and emulator logs, image/configuration hashes and
terminal process statuses. These are diagnostic images and must not be flashed
as radio firmware. The check covers valid-stream segmentation, exact PCM
prefix regression, full-output segmentation invariance and normal close/reopen
stability after warmup. It does not qualify malformed
input, allocation failures, small-buffer retries, full Vorbis conformance,
production audio/TLS tasks, real-time performance or physical audio hardware.
