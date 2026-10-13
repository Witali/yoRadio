# Timer and slideshow machine checks

`src/app/display/factory_timer.c` implements the transition at `0x4200826a`;
`factory_photo.c` implements the fade/selection at `0x4200bc36`/`0x4200bb4c`.
Both run in the production application. Hardware GPTimer starts after display/
settings initialization and before networking: 1 MHz resolution, 100,000-count
alarm, reload zero and auto-reload. Recovered alarm words are read from the
immutable DROM table at `0x3c0d6290`.

`control-validation.json` executes both RV32 programs. Factory ELF load payloads
are checked against the immutable image. The archived native image must equal
the built binary and contain the tested ELF digest. Output adapters capture
startup redraw, backlight duty, JPEG selection, clear and footer calls; counters,
comparisons, flag latching, fade and round-robin algorithms execute unmodified.
Native timer/photo transitions use no adapters.

Four traces compare **79,296 individual ticks** through startup, minute,
181-second and 1801-second rollovers. Photo intervals are 3, 5, 60 and 10, with
an in-place interval change to 7 retaining its counter. Seeded consumption
clears different flag subsets every 37 ticks, checking coalescing and preservation
through main-loop pauses. Every counter, flag, consumed mask and startup request
matches; startup requests exactly 181 redraws.

**13,440 slideshow transitions** cover all 32 masks, six initial fade positions,
five next-slot indices, blocked steps, repeated events and mid-sequence mask
changes. Duty, JPEG/clear/footer requests, slot/fade state and completion match
for valid factory photos. The mask is at offset `0x1a4`, runtime `0x3fcb7d40`;
an earlier decompiler alias incorrectly names it `photo1_size`. Actual photo
lengths start at `0x1a8`, runtime `0x3fcb7d44`. Native code also rejects absent/
corrupt slots instead of reading invalid JPEGs.

## Deliberate corrections

`0x4200bd8c` checks only second/minute flags, with no real hour/minute change
detection. Its minute flag arrives every 60 recovered timer seconds, or 66 real
seconds, allowing stale clock digits. Native code retains the colon flag but
updates digits on real rollover, following the user's instruction to fix bugs.

**60 full frames** exercise three date formats and both hour modes with
independent second/minute flags. Literal factory pixel differences are retained.
A separate unchanged factory renderer raises its minute flag on real rollover
as the corrected reference; all 57,600 pixels match in every frame. No pixels
are masked. Sunday/stroke corrections remain in `machine-checks.md`.

Factory SPI drawing inside GPTimer ISR is deferred to the sole native display
task. Counters advance independently and flags latch while tasks are blocked.
After the photo fade's final zero duty, configured day/night brightness is
restored, correcting the vendor's full-brightness override in photo mode.
These corrections do not imply literal implementation identity.

## Runtime evidence and limits

`timer-runtime/comparison.json` and 30 metadata-free captures record five QEMU
scenes. Factory/native setup, classic, simple, photo and dial ran without a
recorded panic. Both guests received NTP replies in every station scene;
setup instead runs the AP. All setup frames and some captured first-photo frames
match exactly; the original also has a captured blank/intermediate photo frame.
Other ratios depend on capture time, redraws and declared corrections; no
equality percentage is a pass threshold.

`final-timer-runtime/comparison.json` rechecks the final archived image's
classic scene, boot and NTP after a source-comment correction/rebuild. Every
report preserves its own exact application/source hashes.

These tests do not prove complete SDK scheduling, successful weather HTTP,
all web contracts, pixel decoding or physical-board operation. Weather retry
requests now use completed main-loop steps and the global periodic flag;
successful weather/server checks remain pending.

```powershell
& .\Small_TV\src\build.ps1
& .\Small_TV\src\tests\run-machine-oracle.ps1 -Control
```
