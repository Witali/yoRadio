# CYD full-record TLS RX reserve tests

Runners read canonical repository sources plus explicitly supplied installed
ESP-IDF6.0.2/tool dependencies. Historical ignored build directories are not
runtime inputs. Every output must be fresh under the checkout's `.build`.
This fixture binds the userdata-free uintptr_t registry source, not the earlier
pointer-marker prototype. The reserve remains default-off in production.

```
python -B -X utf8 tests/run-cyd-tls-static-rx-unit.py --sdk <SDK6.0.2> --output .build/rx-unit
python -B -X utf8 tests/run-cyd-tls-static-rx-service.py --sdk <SDK6.0.2> --output .build/rx-service
python -B -X utf8 tests/run-cyd-tls-static-rx-config.py --sdk <SDK6.0.2> --cmake <cmake.exe> --ninja <ninja.exe> --output .build/rx-config
```

All have `--preflight-only`; unit/service also offer `--prepare-only` to freeze
inputs without invoking a compiler. Host runs use WSL GCC/G++ with Werror,
ASan/UBSan, leak detection and no sanitizer recovery. C++ is only the small
placement-new object-lifetime case; production module and exact SDK spans retain
strict C mode. Host types/layout, crypto callbacks, HTTP/TCP, RTOS locks, timing,
capacity inputs and adaptive metadata are explicit seams, not target ABI or TLS
protocol claims. Whole-service tests retain the complete production audio service
and three owner loops, with existing codec/output/platform seams.

`source_contract.py` checks the normalized-LF pinned module identity while
recording actual raw hashes/line endings. Only uniform LF/CRLF is accepted.
Raw source snapshots/manifests stay exact, and compiled module bytes are not
silently normalized. The separate raw-hashed SDK guard JSON has a scoped
`-text` Git attribute. SDK source newline/hash restrictions remain unchanged.

Coverage includes both userdata kinds, exact config-init/free SDK bodies, actual
ESP-TLS cleanup ordering, stale/new storage reuse, NEW radio registration while
OLD SSL still owns RX, shared/distinct contexts, full-registry soft fallback,
ISR-safe host seam, erase barriers, rollback and ordinary allocator/reclaim
pairing. Named negative controls require exact failures; sanitizer reports,
assertions, panics, timeouts and unrelated failures do not pass.

Expected preparation scope is8 unit groups/9 controls/14 compile rejections;
whole-service12 option/backend variants (expected536 case executions) and2
binding controls; configure45 cases. Actual result reports compute their counts.
These are expectations until run against final checked-in bytes. Actual target
ISR/SMP/OOM/header/ELF qualification is separate; see [target/README.md](target/README.md).
