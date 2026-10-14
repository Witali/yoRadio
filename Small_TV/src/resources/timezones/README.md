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
city or add a regional selector. The longer recovered keys are available to the
timezone helper. The current reconstructed settings field stores two characters
and its HTTP parser rejects regional suffixes. The factory raw country slot is
20 bytes and its recovered table contains keys such as `AU-W` and `US-H`;
restoring those settings/HTTP paths remains part of the parity work. The current
helper tests do not prove that all 109 keys can be selected through the web UI.

`tools/prepare_timezones.py` validates the keys and hashes, reads complete 64-bit
transitions, deduplicates identical offset/DST rules, and generates immutable C
tables. Future recurrence uses the explicit TZif footer, including southern
hemisphere seasons, negative DST, and signed/extended transition times. Current
source footers use month/week/weekday rules. An unsupported future source format
fails generation; it never falls back to implicit libc DST rules.

The data is a pinned snapshot. Future changes to civil-time rules require a
reviewed data update and firmware rebuild. The source manifest hashes generated
tables, so a changed offset table invalidates the previous build/test evidence.

## Checking and reproducing upstream data

The source of timezone rules is [IANA tzdb](https://www.iana.org/time-zones).
The Python Software Foundation's [tzdata](https://github.com/python/tzdata)
distribution supplies ready-made `zic`-compiled TZif files; it is a transport for
IANA data, not a separate source of civil-time rules. The updater verifies the
wheel SHA-256, declared package/IANA versions, every selected TZif structure and
future recurrence before writing any output. It never installs or executes code
from the downloaded archive. Country-to-zone defaults stay in the existing
manifest; a country alone cannot uniquely identify every region's timezone.

Run from the repository root with Python 3. The normal firmware build reads only
the committed snapshot and never downloads timezone data.

```powershell
python Small_TV/src/tools/update_timezones.py --check-latest
python Small_TV/src/tools/update_timezones.py --output .build/timezones-candidate
python Small_TV/src/tools/prepare_timezones.py --source .build/timezones-candidate --output .build/timezones-check
```

`--check-latest` reads the official IANA `tzdb/version` and reports the current
PyPI transport candidate. It does not modify pins or assume that the newest
package already contains the newest IANA release. Without explicit pins the
download command reproduces exactly the currently committed release.

For a different release, supply all three `--iana-version`, `--package-version`
and `--wheel-sha256` arguments together. Verify the upstream release and wheel
digest, inspect the candidate manifest/data changes, then run the same command
with `--output Small_TV/src/resources/timezones` to apply the chosen snapshot.
Rebuild/archive the firmware and run the full test suite before publishing its
new validation evidence. An unsupported future TZif rule stops the update and
requires a parser change; it cannot silently fall back to libc defaults.

Offline reproduction uses an already downloaded wheel:

```powershell
python Small_TV/src/tools/update_timezones.py --wheel path/to/tzdata.whl --output .build/timezones-candidate
python Small_TV/src/tests/timezone_update_test.py --wheel path/to/tzdata.whl --output .build/timezone-update-report.json
```

The optional `--wheel` regression checks all selected raw bytes and the generated
C header against the committed snapshot. `tests/run-all.ps1` always runs the
network-independent `timezone_sources` archive/validation cases and hashes their
inputs. Release discovery and real upstream downloads are separate maintenance
actions. No on-device automatic download, city inference or regional selector
is added by this tool.
