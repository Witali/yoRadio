# Small TV comparison checkpoints

The completed full automated run on 2026-10-17 passed all 19 host/machine/QEMU
groups for ordinary application `ef66d557…`, source `81cf614c…`, ELF `8fce7524…`
and QEMU `a74f3324…`. All 184 frozen input fingerprints remained unchanged.
The [published functional evidence](../../src/tests/functional-validation.json)
includes 84 natural calendar transitions, 168 associated completed frames,
and 24 strict scene frames with zero differing pixels against instruction replay.
These are scoped automated results; full equivalence and physical-board
acceptance remain unproven. Subsequent Wi-Fi HTML corrections live in separate
branches and have different application identities.

The separate RSSI-candidate 24-hour runtime test was interrupted after 187 cycles
and 3,096.125371 observed guest seconds. Its VM and controllers were absent at
the process audit; the report had no terminal footer. The
[interruption record](runtime-rssi-interrupted-20261017.json) preserves the
numeric journal and input identities. It is not a completed H10 pass.

The earlier completed-frame checkpoint (2026-10-16) is documented in
[completed-scene checks](completed-scene-checks.md), with exact identities in
[the current results](../completed-scenes-validation.json). All 24 real QEMU
frames match instruction replay. At identical canonical inputs, 33 complete
classic scenes match the unchanged factory renderer; seven dial scenes match
the explicitly corrected factory geometry. Real JPEG/BMP decoders execute in
these checks. [The previous first-frame brightness failure](first-digital-brightness-before.json)
retains its old application hash. Complete program equivalence remains unproven.

The captures and percentage table below are historical; they retain their own
earlier application identities and do not measure the latest completed-frame gate.

This historical QEMU checkpoint was paused at the user's request on 2026-10-13.
Functional reconstruction has since resumed. The reconstruction now uses
the factory fonts, layouts, settings sector, timer thresholds, photo fades and
rounded analog strokes. Complete function/behavior identity is **not established**.

[Country timezone checks](timezone-checks.md) now execute the native conversion
and real Newlib against independent pinned IANA TZif data for all 109 recovered
keys. The implicit factory DST-rule defect is a declared correction; literal
monthly differences remain in [the before observation](timezone-before.json).
The [current result](timezone-validation.json) retains its own app/source hashes.
Later [SNTP checks](time-sync-checks.md) cover validity and retry/fallback transport
separately; the broader calendar/DST transport matrix remains incomplete.

Newer [machine-level renderer checks](machine-checks.md) use identical explicit
inputs and execute both RV32 programs. They restore tick-angle narrowing while
deliberately correcting the vendor's Sunday-label and stroke-geometry bugs at
the user's request. The results below remain the
original captures at their recorded application hashes; they are not updated
measurements of the newer firmware.

[Timer/slideshow checks](control-checks.md) verify executed counter/event
algorithms and real minute rollover, alongside newer QEMU runtime captures.
Those reports retain their own application hashes and explicit limits.

`compare.py` boots both unmodified applications with matching synthetic factory
settings, isolated NTP, a disabled weather-key sentinel and no external Internet.
Its default photo mask enables only the first photo to isolate image rendering
from slideshow phase. It does not patch guest instructions, PC or RAM. All VMs
were stopped. `comparison.json` records build/source hashes and actual captures.

| Scene | Best whole-frame equality | Best fixed-region equality |
|---|---:|---:|
| Setup instructions | 100% | 100% |
| Classic digital/weather | 99.42% | 99.90% |
| Simple digital | 93.42% | 97.76% |
| First selected photo | 100% | 100% |
| Analog dial | 98.91% | 99.02% |

These are measurements, not pass thresholds. Three actual captures from each
guest are retained; min/max values are in JSON. Fixed regions exclude live
digits, animation or hands as defined in the script. Captures occur at different
host/guest clock instants and can interrupt an SPI redraw. The remaining
differences, particularly the simple-clock fixed region, still require analysis;
they are not all attributed to timing.

Both applications ran these scenes without a recorded panic. The current
native image compiled successfully and passed 1249 host checks. Prior full
boot/DHCP/NTP/reset reports belong to their recorded older application hashes.
The immutable factory dump hash remains
`5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4`.

```powershell
& .idf/python-3.12.10/tools/python.exe Small_TV/qemu/parity/compare.py
```

`*-original-*.png` and `*-reconstructed-*.png` are raw SPI framebuffer captures
encoded as metadata-free PNGs. Production firmware is saved under
`firmware/development/small-tv-esp32c2-reconstructed/`.
