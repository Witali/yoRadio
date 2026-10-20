# Canonical TLS static RX registry: host evidence

Completed scope: whole canonical registry unit host tests, source-only CMake
configuration guards, and whole-owner host service integration. The canonical
implementation has been applied. This archive does not qualify an SDK/target
build, QEMU/physical behavior, real heap exhaustion, TLS protocol conformance,
or runtime RAM/performance benefits.

- Unit: 8 positive groups, 9 exact named controls, 14 invalid compile profiles,
  and 8 restored groups. Report SHA-256: `9137bdd08bceaf8bb7efcccbc9efa26e7a54457e0f654a9e68c9d96f44c51205`.
- Configuration: 45 real configure-only CMake cases, including 19 supporting
  SDK guard mutations. Report SHA-256: `f0a5ea8dc76a50e249b02c2815db4a963fa2c7577e6376ff4b6f94fe74d46316`.
- Host service: 12 reserve/reclaim/backend variants, 536 scenarios and 2 exact
  radio binding controls. Report SHA-256: `c53e24335b40df3c93122da1f20b949373fe71cf1fbf78aeb8e954c7c7101897`.

The module never interprets application pointer or numeric userdata. Unit tests
cover both userdata kinds, actual extracted config init/free bodies, live RX
ownership across config-free and address reuse, full bounded registry fallback,
rollback and host concurrency. These are source-span/host observations with
explicit type, RTOS, allocator, capacity, transport and backend seams.

`HOST.md` describes the limits. `index.json` points to raw reports and every
selected source/log/config. `path-map.json` preserves original names and raw
identities; binary tools/host executables/objects are explicitly omitted. Their
bytes are not available for offline reconstruction. Logs use deterministic gzip.
No report or source snapshot is rewritten. The exact source-only preparation
manifest is `8690b77ea44e23ab71ad30190ef9cc5764080f5609009adac4519582f5c70606`; its target recipes are preparation, not execution.

All 34 applied canonical files were checked byte-equal to final preparation
snapshots. Tests ran before the subsequent source commit; source equality does
not imply the tree was clean/committed when tests ran. Later root commit metadata
belongs in a separate note. Live or subsequent target campaigns are excluded.

Run `python -B verify.py` from this directory or any working directory. The
standalone verifier uses only archived bytes and Python stdlib, recomputes the
SDK overlay/public accessor/function/macro spans and exact original host oracles,
and launches no SDK/compiler/WSL/Git/network/device operation. Its PASS means
archive integrity and the stated historical host gates, without extending scope.
