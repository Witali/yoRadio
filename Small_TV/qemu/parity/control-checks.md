# Timer slideshow and backlight machine checks

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
The former `photo1_size` alias is now corrected to `slideshow_photo_mask` in
the reference export, symbol map and organizer. Actual photo lengths start
at `0x1a8`, runtime `0x3fcb7d44`, and the five size aliases are corrected.
Native code also rejects absent/
corrupt slots instead of reading invalid JPEGs.

## Backlight driver traces

`backlight_oracle.py`, included in the control gate, executes initialization
`0x42008d62`, forced duty `0x42008bd2` and schedule `0x42008c4c` against the
compiled native functions. Only the four successful LEDC SDK boundaries are
captured. Native configuration/settings offsets come from ELF DWARF; original
configuration offsets and actual SDK call targets are verified in disassembly.

The **144,246 comparisons** cover two forced calls for each of the 1001 duty
levels, all 1440 minutes for each of 48 night-hour pairs with both time-validity
inputs, and enabled/disabled night mode with repeated settings at every level.
Exact set/update calls and final duty agree. Initialization now configures duty
zero and then explicitly sets/latches level 100 (duty 819), as the factory does.
The scheduled path skips unchanged levels; the forced path still performs
repeated writes for fade steps. One common native setter applies both paths.

The earlier native initialization omitted set/update and configured duty 819
directly. Its schedule also wrote the same duty on every main-loop iteration;
the initial trace comparison failed despite equal final PWM values. The repair
restores the call sequence and conditional behavior. Host driver-failure tests
also require that failed timer/channel setup performs no subsequent duty write.
Three native-only checks retain clamping above the accepted 0..1000 range.

The original schedule cache does not reflect forced photo-fade writes. Five
independent restoration cases record the literal original duty after a forced
zero and require the configured native duty, including level zero. This is the
declared photo-brightness correction, rather than an unexplained parity failure.
Physical PWM waveforms, driver locking and electrical behavior remain outside
this executed-call comparison.

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

These control tests do not prove complete SDK scheduling, all web contracts,
pixel decoding or physical-board operation. Weather retry requests use completed
main-loop steps and the global periodic flag. Real synthetic-weather HTTP and
LCD checks are recorded separately in
[weather-http-validation.json](../weather-http-validation.json).

```powershell
& .\Small_TV\src\build.ps1
& .\Small_TV\src\tests\run-machine-oracle.ps1 -Control
```
