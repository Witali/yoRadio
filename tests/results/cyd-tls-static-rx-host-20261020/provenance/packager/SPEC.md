# Canonical static RX host archive preparation

Status: PREPARED TOOLS ONLY. Default packager mode is PLAN ONLY. Root must review
these exact bytes and authorize writing the new archive separately. No previous
archive, evidence input, canonical source, SDK or Git metadata may be changed.

Proposed destination: `tests/results/cyd-tls-static-rx-host-20261020/`.

## Authoritative completed cohorts

| Cohort | Original directory | Root terminal | Report SHA-256 |
| --- | --- | --- | --- |
| Unit | `.build/rxu01` | session 86428, exit 0 | `9137bdd08bceaf8bb7efcccbc9efa26e7a54457e0f654a9e68c9d96f44c51205` |
| Configure | `.build/rxc01` | session 21895, exit 0 | `f0a5ea8dc76a50e249b02c2815db4a963fa2c7577e6376ff4b6f94fe74d46316` |
| Service | `.build/rxs01` | session 79183, exit 0 | `c53e24335b40df3c93122da1f20b949373fe71cf1fbf78aeb8e954c7c7101897` |

The parent reported terminal status; no wrapper terminal log is invented. All
original reports/child commands/logs are preserved. Tests ran before the later
source commit. Equality with applied canonical bytes is verified separately;
this archive must not claim a clean committed source tree at test execution.

## Payload closure

1. Every existing file from the three completed cohorts, including raw reports,
   frozen inputs, generated SDK overlay/spans/public getters/capacity macros,
   CMake projects/captures/caches/logs, generated host configurations and exact
   semantic controls. Unrelated campaigns and previous prototype runtime cohorts
   are excluded. Executables/objects/tools are identity-only omissions.
2. Every one of the 554 raw payloads named by final source-only prep manifest
   `8690b77ea44e23ab71ad30190ef9cc5764080f5609009adac4519582f5c70606`,
   plus that manifest itself. Its target recipes/freezes are preparation only.
   Its older module history must not replace the final canonical module.
3. Current applied 34 canonical files must match their corresponding final prep
   snapshots byte-for-byte. The final module has normalized LF hash
   `17e98a29cadd0387d9db725d50c12514847426cd9cfa607abf5224884fe17555`.
   Raw module identity and uniform LF/CRLF relation are checked independently.
4. Complete nineteen-source SDK guard manifest and all raw guarded SDK source/
   header payloads, full patcher, source-span and fixture recipes. No installed
   SDK bytes are modified. No SDK build or target ABI proof is inferred.
5. Root's separate filesystem readback report and recipe, with their original
   raw identities; self-contained packager/verifier/templates and pure preparation
   checks. No `.build` historical Python module is imported at runtime.

## Independent offline predicates

`verify.py` and `evidence_rules.py` require only Python stdlib and the archive.
They never open original paths, launch tools, import archived fixture/patcher
code, or execute test recipes. They check manifest file set/raw hashes, deterministic
gzip, original decompressed hashes/lengths, explicit omissions, JSON hash-reference
bindings, all 34 canonical/prep raw equalities and source-only prep status.

Patch replay decodes only literal constants with AST, pins the complete source
and guard-map identities, independently applies all six unique replacements,
checks paired allocation/rollback/final-free/init/free entries, and reproduces
whole generated overlay and seven SDK function spans. SDK public pointer and
numeric userdata setters/getters and all six capacity macro spans are extracted
independently from raw SDK headers, without claiming host types are target ABI.
All nineteen normalized guards require uniform raw LF or CRLF; no raw evidence
is normalized or rewritten in the archive.

Unit predicates: exact8 positive groups,9 named exit-2 semantic controls,14
compile rejections,8 restored groups,52 unique raw command logs; strict
ASan/UBSan compiler flags; ownership allocation/free balance; no sanitizer,
crash/timeout accepted as a semantic control. These include both userdata kinds,
config init/free/cancel/live-config-free/address reuse, full soft registry,
attach failure/nesting, rollback, whole canonical reclaim and host concurrency.
Every actually compiled canonical/control `module.c` and `sdk.c` is compared with
the frozen module/span body or its exact declared literal mutation, decoded by
AST without executing the runner (including config-init/free hook omissions).

Service predicates: exact12 reserve/reclaim option pairs by PDM/DAC/legacy
backends,536 scenario outcomes,2 exact named exit-2 radio binding controls,
554 raw commands. Verify actual per-option compile inclusion, preserved board
stack macros extracted from canonical board_config, whole owner sources with
only platform includes replaced, exact SDK on/off spans, restored mutation bytes
and every generated artifact identity. Host binaries remain explicit omissions.

Config predicates: exact45 real `project(... NONE)` configure cases,19 guard
mutations, original capture/logs, exact module source/substitution/sibling source,
unchanged link options, no compiler detection, complete ordered configure
dependencies, byte-identical canonical overlay, off/zero/early paths avoiding
SDK/Python input access and named rejection categories.
Each per-case copied helper and every present module/header/patcher/guard file
must remain byte-identical to frozen canonical inputs. All nineteen copied SDK
files must be exact, except the one explicitly declared guard mutation.

## Representation and omissions

Content-addressed objects deduplicate equal raw bytes; logs and payloads >=128KiB
use deterministic gzip with mtime 0. Path map retains original path, raw size/SHA,
role and encoded identity. Raw reports are never rewritten. Binaries beginning
ELF/MZ/ar magic or with known executable/object/archive/firmware extensions are
omitted and recorded by original size/SHA/role. Linux compiler identities reported
by original host logs have unknown byte size, explicitly `observed_bytes=false`;
no WSL or tool process is invoked to recover them. Offline verification establishes
the recorded omission identity, not independent reconstruction of omitted bytes.
Local `.gitattributes` marks the complete archive `-text`.

## Unrun/out-of-scope gates

Actual SDK whole-component/application compilation, target ABI/layout,
QEMU/physical target ISR and SMP behavior, true heap exhaustion, network/TLS
handshake/protocol conformance and physical RAM/performance benefit are not
qualified here. Any concurrently running target campaign is separate, and
neither its live report nor future result may be imported into this archive.
No record sizes, pool sizes, cores, stacks or timings are changed. Deferred codec
work and the superseded pointer-userdata target prototype are not qualified by
this archive. Later source commit metadata may be recorded in a separate root
note without rewriting the test reports or backdating Git cleanliness.

## Commands after review

Use the repository Python executable with `-B` and `build_archive.py`, passing
all three exact `--unit-report-sha256`, `--config-report-sha256` and
`--service-report-sha256` values above plus a fresh `--attempt attempt-NN`.
This defaults to plan only and writes preparation reports below this directory.
Only after explicit root approval add `--write-reviewed-archive`. No SDK/test/
compiler commands are part of packaging. The sole child process is the new
archive's filesystem-only offline verifier after a reviewed write.
