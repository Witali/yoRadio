# Country time conversion checks

`src/tests/timezone_oracle.py` runs the real factory Newlib `tzset` at
`0x420aa9c8` and `localtime_r` at `0x420aa5ce`. The original country strings
come from the recovered table used by `0x42010a06`. The native firmware's
`timezone_local_time`, transition search, Gregorian arithmetic and actual
Newlib `gmtime_r` execute from the compiled RV32 ELF.

The test adapts environment lookup and libc reentrancy/locking, not successful
calendar conversion or rule evaluation. The factory GP is initialized to
`0x3fcb49c0`, as its bootstrap at `0x4038046c` does. Named 64-bit RV32 arguments
occupy successive registers; unlike aligned variadic pairs, the epoch here
starts in `a1`. The compiled entry was disassembled to confirm this ABI.

The independent expected implementation is Python `ZoneInfo.from_file` reading
the pinned, hash-checked TZif sources directly. It does not read generated C
tables. Source provenance is in [the timezone resources](../../src/resources/timezones/README.md).
The historical/default/future semantics follow
[RFC 9636](https://www.rfc-editor.org/rfc/rfc9636.html). Data is pinned to
[IANA 2026e](https://data.iana.org/time-zones/tzdb-2026e/).

The old strings `GMT0BST`, `CET-1CEST`, `AEST-10AEDT` and others omit recurrence
dates. Actual execution confirms that Newlib then uses US defaults, including
for Europe and the southern hemisphere. The before report contains 116 calendar
differences in 12 monthly samples for each of 109 keys in 2026. This is a scoped
negative result, not a percentage of code coverage. Both old factory and old
native libc outputs agreed in those samples. Neither source decoder nor dump
was changed to manufacture the discrepancy.

The native correction retains the country-only representative zones and GB
fallback, while replacing implicit rules with immutable offset/DST data. Explicit
history is binary-searched; after it ends, the TZif footer supplies recurrence.
Adjacent-year event selection handles southern seasons and Ireland's negative
DST. Signed/extended transition hours handle Greenland, Israel, Egypt and Chile.
The display converts each settings snapshot directly without waiting for a
global TZ setter. The time worker also updates a fixed-offset POSIX TZ for other
libc consumers, checking offset changes every second even while offline.

The machine gate requires all 109 keys and compares 36,404 cases: every recorded
transition at -1/0/+1 seconds, monthly samples spanning 1900–2400, independently
discovered future transition edges, 12 unknown/case-sensitive fallback checks,
and five invalid-pointer/epoch checks. The caller's calendar is preserved on
failure. The helper also validates libc results against the original epoch so
an overflowing calendar field cannot silently produce a wrapped date.

Platform cases `time_zone_boundaries`, `clock_timezone_classic` and
`clock_timezone_simple` execute production workers and display loops. They test
offline offset changes, backward corrections, country changes at the same epoch
and DST jumps with unchanged seconds and no minute event. A first test expected
a freshly drawn colon during a jump without its timer event; that expectation
was corrected to retain the independently verified factory timer phase.

These checks do not establish SNTP retry/fallback transport, successful-sync
validity, leap-second transport, physical RTC behavior or runtime memory. The
factory's fixed 2025 validity threshold and same-second cache gate at `0x42010b70`
remain separate work. Civil-time legislation after the pinned snapshot requires
a reviewed data update and firmware rebuild.
