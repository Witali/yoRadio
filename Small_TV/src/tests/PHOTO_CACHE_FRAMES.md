# Current main: cache-backed photo LCD

Historical image checkpoint below. The measured startup delay is fixed and
qualified by the newer [next-photo prefetch checkpoint](PHOTO_PREFETCH.md).

Checkpoint 2026-10-23, app `034287C7`, production source unchanged from
`f2909c553`. This is an independent LCD gate. Local station/weather/SNTP fixtures
permit normal boot; their availability is not a network or RF acceptance claim.

`photo_cache_frames_qemu.py` observes the actual application with hardware
breakpoints at `factory_photo_step` and the final coordinator yield located in
its exact ELF. It never writes guest RAM, registers, instructions, PC or time.
The old pre-worker observer fails because it expects two coordinator delay
calls; the current application has one ordinary final yield. Its unconditional
`present == 31` assumption also does not describe masked asynchronous preparation.
The historical observer is retained for its original application checkpoints.

Readiness is observed through the real function arguments. Blocked/idle calls
must leave the slideshow state unchanged. At a photo-selection phase all enabled
valid fixture slots must be ready: the test refuses silently skipping an
uncached photo. The waiting samples are retained, not discarded from timing
evidence. At most 2,000 waiting observations/300 guest seconds are permitted.

The expected picture is produced by executing the literal factory photo,
selection, TJpgd, footer glyph and LEDC instructions in `PhotoMachine('factory')`.
Only its documented SDK/LCD/allocator boundaries are adapted. The real QEMU
LCD is compared over all 57,600 pixels. No crop, tolerance or difference mask.
The known factory brightness-restoration error is corrected explicitly: at fade
phase five the expected duty uses the actual calendar passed by the application
to `backlight_update` and the configured day/night level. Other fade duties
retain the factory arithmetic.

## Results

Three owned cold native processes passed and were stopped/reaped by retained
Win32 process handles:

| Profile | Complete frames | Photos / purpose |
| --- | --- | --- |
| All photos, day level 0 | 28 | Slots 0, 1, 2, 3, 4 in order; all fade phases |
| Mask 10, day 100/night 500 | 22 | Slots 1 and 3; four cycles, including actual night sync |
| Mask 0, day 1000 | 4 | Empty-photo footer and dark configured restoration |

All 54 frames / 3,110,400 pixels match exactly. Thirteen negative report controls
reject missing phases/photos/pixels, unready selection, changed code/protected
flash, wrong brightness, missing night sync or process reap and false network
labeling. Early night-profile frames are genuinely unsynchronized. External NTP
responses are released after two complete cycles; the later night restoration
uses the actual synchronized calendar, without substituting a preset.

Actual post-stop flash comparison preserves boot/application, immutable media,
all source photo slots, stamp and protected gaps. Only NVS, the preferences
sector and generated candidate cache/scratch extents may differ. Before images
can be reconstructed from archived firmware and the declared synthetic seed;
their SHA must equal the actual `prepared.json` preboot SHA. The evidence stores
these images and actual after images losslessly as deduplicated sector deltas.

App SHA: `034287c7102784fdf2fb44f374d5ef6408dabb370a7276637381a94059b3f304`.
ELF: `bb7fd7a180a5536b031531653fa84d29b4cdaa3e22439d7c11fd84680f6f0da6`.
Source: `1d1f52ce1499c15e6a1fefdf1b2f412c69fcf2f1d7af1606dbb0702b243a8202`.
QEMU: `d64f3013739f22b986e07aed39395b25bde474f52ef813b8ffaeedb0991edecc`.
Exact source/raw frame evidence:
`Small_TV/qemu/parity/photo-cache-frames-validation-20261023.json`.
An independent archive verifier decodes all captured PNGs, checks every RGB
surface hash, reconstructs all six physical images and repeats protected-byte
comparisons. New compressed payloads occupy about 1.8 MB; the earlier common
flash base is referenced rather than copied.

## Timing finding and remaining acceptance

Visual equivalence does not imply identical startup timing. In the matching
all-photo profile the first complete native photo took 23.389901 guest seconds;
the literal stock application in a separate owned process took 20.565822.
An earlier native repeat took 23.559866. These are guest timer observations,
not host CPU durations or hardware timing promises.

Readiness samples show slot 0 available around 5.3 seconds, while the slideshow
remains blocked as the worker processes the other slots. Preparing all five
caches before allowing the first display delays a usable picture. The startup
latency comparison therefore **fails** and is recorded as an open optimization;
the pixel gate passes. Do not hide this by starting the timing after warm-up.

Still open: reduce that startup/prefetch delay without skipping valid or corrupt
slots, preserve fade timing and cancellation/retry semantics, test durable cold
cache hits with zero writes, classic/simple/dial clock continuity during slow
foreground decode, complete JPEG target memory/stack/format/fault matrix,
upload/decode publication power cuts, network lifecycle/churn, whole-image
audit/full/24h/hardware. No physical board operation was performed.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
python -B Small_TV/src/tests/photo_cache_frames_qemu.py --qemu-root FROZEN_QEMU --dependency-root C:/Work/yoRadio --output NEW_RUN
python -B Small_TV/src/tests/verify_photo_cache_evidence.py --proof Small_TV/qemu/parity/photo-cache-frames-validation-20261023.json
```
