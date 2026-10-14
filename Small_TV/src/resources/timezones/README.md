# Timezone source data

These TZif files contain public-domain IANA timezone data, extracted without
installing or executing the Python package from the pinned `tzdata` wheel.
`manifest.json` records the package version, IANA version, wheel SHA-256, each
file's SHA-256, and the mapping of all 109 recovered country keys.

Sources: [IANA 2026e](https://data.iana.org/time-zones/tzdb-2026e/) and
[tzdata 2026.5](https://pypi.org/project/tzdata/2026.5/).
The IANA regional source files state that the data is in the public domain;
no Python package code or its independent license-covered implementation is copied.
TZif semantics follow [RFC 9636](https://www.rfc-editor.org/rfc/rfc9636.html).

The firmware retains one representative timezone per factory country key and
the unknown-country GB default. It does not infer a timezone from the weather
city or add a regional selector. The longer recovered keys are retained for
analysis; the existing two-character settings field cannot select them.

`tools/prepare_timezones.py` validates the keys and hashes, reads complete 64-bit
transitions, deduplicates identical offset/DST rules, and generates immutable C
tables. Future recurrence uses the explicit TZif footer, including southern
hemisphere seasons, negative DST, and signed/extended transition times. Current
source footers use month/week/weekday rules. An unsupported future source format
fails generation; it never falls back to implicit libc DST rules.

The data is a pinned snapshot. Future changes to civil-time rules require a
reviewed data update and firmware rebuild. The source manifest hashes generated
tables, so a changed offset table invalidates the previous build/test evidence.
