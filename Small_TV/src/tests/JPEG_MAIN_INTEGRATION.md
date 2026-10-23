# JPEG in the actual Small TV application

Checkpoint: 2026-10-23. Development integration; whole firmware acceptance remains
open. The factory dump, shared SDK and frozen QEMU inputs were not changed.

## Actual implementation

`photo_codec` owns the qualified privacy/decoder/cache/NOR APIs. Factory baseline
8-bit photos use `jpeg_baseline`: the same corrected TJpgd IDCT/color conversion,
with at most16 RGB565 rows assembled before cache publication. Other supported
modes use bounded libjpeg; a prepare-only baseline refusal may fall back before
any output row. HTTP and the LCD do not use upstream library types.

`photo_worker` serializes the producer/cache, with an idle-priority8KiB task and
a four-entry queue. Foreground requests cancel background work. Source writes
wait for durable invalidation. Slow processing does not hold `media_mutex`;
ordinary clocks and immutable animation/weather reads remain available. The UI
requests background preparation and only draws physically verified ready frames.

HTTP start/finish use the pinned SDK's supported async request clone. Every
successful begin has exactly one complete, including queue rejection, disconnect
and error. Source length is published only after privacy, one complete producer,
physical frame verification and durable journal publication. Browser cropping,
resizing and metadata removal remain unchanged.

## Defects found by the integrated tests

1. An obsolete queued source length could rebuild a cache after settings changed.
   A deterministic event-controlled test failed on actual program/erase counts.
   Recheck committed length/ownership before work and while publishing results.
2. A physical read failure inside privacy validation permanently suppressed an
   unchanged source. An injected third source-prefix read failure reproduced it.
   Only stable input/fixed-capacity refusals suppress automatic retries; temporary
   allocation/I/O/cancellation/deadline errors remain retryable.
3. Standalone decoder RAM fit did not imply whole-app fit. During a real large
   CMYK12 request, observed SDK heap minima summed to1392bytes and HTTP probes
   timed out. HTTP was waiting in `lwip_select`; settings/media mutexes were free.
   The full decode eventually returned OK, so successful decoding alone was not
   an acceptance criterion. A16KiB service reserve now limits allocations and is
   checked during buffered decode work. Other tasks may allocate after malloc;
   allocation-only checking also failed the workload and is not the final fix.

`heap-headroom` reports the attempted allocation and observed available bytes
after excluding service reserve/contiguous-block limits. `service-heap-reserve`
reports the16KiB service floor and observed free RAM at the cooperative stop.
Neither is reported as damaged JPEG. The floor is a runtime admission policy;
it cannot prevent another task/interrupt from allocating between checks.

## Checks and limits

The ordinary native gate passed6001 assertions plus the direct privacy controls.
It uses actual libjpeg, strict physical NOR, OS SHA and a real host worker/queue.
It checks five packaged baseline photos pixel-for-pixel against the existing
producer, readonly cached redraw with zero program/erase, extended CMYK12 pixels,
precise capacity/pool/memory errors, source/settings preservation, queue saturation,
async begin/send failures, stale jobs and recovery after a temporary read failure.
MSVC host ABI memory requirements are not substituted for RV32 requirements.

The actual application builds and fits its0x177000-byte app partition. Matching
ownership stamp, cache headers and dependency report are archived with the build.
The original source bundle/library remains pinned and is built offline.

`photo_owner_qemu.py` is an HTTP/storage gate. It preserves full flash bytes,
uses two owned cold processes and loopback service fixtures, and requires exact
uploaded bytes after relaunch plus unchanged protected regions/other photo slots.
Resource failures must give numeric required>available and leave source size zero;
a subsequent valid progressive gray image must succeed. Slow work must leave
HTTP responsive, with the same10-second observer timeout and no tolerated errors.
Normal probes reuse one HTTP/1.1 connection; earlier short-connection stress runs
are retained as failed observations, not silently converted into acceptance.

QEMU workflow results and exact app/ELF/source identities are recorded separately
in `Small_TV/qemu/parity/jpeg-main-integration-validation-20261023.json`.

Final C2 HTTP/storage gate passed five workflows: three allocation-headroom
refusals, one later service-reserve abort and successful progressive gray upload.
All46concurrent GET probes passed; maximum observed response was0.657host seconds.
The separate control passed160GETs, maximum0.640seconds. Four owned processes
exited and their handles were reaped. Two persistent full flash images confirm
cold source bytes and unchanged protected regions; this is not a power-cut test.

Development app:1464560bytes,71440app-partition bytes free, DEBUGoff.
App SHA-256:`4b7530cbe033df2e011cc85b6afc16667963819ca976c096a0f7df4eadba496d`.
ELF:`6b233c4f23839ef4c3bca0fe1fece06bc00128398b3da4b49e5e198e8583bf94`.
Source:`c6b9d1ad977943066804277bcec6579bb52c7ee790a2a128207e07987f12fbe4`.
This runtime matrix deliberately does not claim target CMYK12/RGB-progressive
acceptance: those tested files were refused to preserve the rest of the device.

Not yet accepted: automatic safe migration from old unstamped assets without
overwriting user photos/settings; target-wide RAM/stack/format/fault coverage;
reset/power-loss during actual upload/decode/publication; independent complete LCD
frames and clock continuity during decode; network reconnect/multiple-client
lifecycle and connection-churn overload; current-image full suite/24h/hardware.
Cold source persistence alone does not prove a target cold cache hit wrote zero
bytes or skipped decoding. Host qualified formats are not all proven to fit this
C2 application. Weather/RF/electrical behavior is not certified by this gate.

## Reproduction

```powershell
pwsh -File Small_TV/src/tests/run.ps1 -PythonPath SDK_PYTHON
pwsh -File Small_TV/src/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf
python -B Small_TV/src/tests/artifact_test.py --output NEW_ARTIFACT_REPORT
python -B Small_TV/src/tests/photo_owner_qemu.py --qemu-root FROZEN_QEMU --output NEW_HTTP_WORKFLOW
python -B Small_TV/src/tests/photo_owner_qemu.py --qemu-root FROZEN_QEMU --output NEW_CONTROL --control
```

Do not rebuild/change pinned inputs during a VM run. Each output must be fresh;
only the newly owned processes are stopped/reaped. No physical device was flashed
or reset, and no network or LCD check substitutes for the other.
