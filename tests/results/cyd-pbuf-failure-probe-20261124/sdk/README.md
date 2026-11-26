# Pbuf observer: three-output SDK qualification

All three diagnostic fixtures pass build/static/link/Clang qualification at
source `f7dee344fb30ce109f2d30a01f0325d353e3b2eb`. This is observer qualification,
not a memory fix, native resource acceptance, or physical Wi-Fi/audio test.
The original allocation gate and every earlier native NONPASS stay intact.

| Backend | Application bytes | Preserved original objects |
| --- | ---: | ---: |
| Legacy DAC | 1,270,768 | 953 |
| PDM | 1,270,512 | 951 |
| Continuous DAC | 1,264,736 | 951 |

Only the existing PCM hook object changes, plus one new pbuf probe object per
profile. Kconfig JSON/header bytes are unchanged from the RTC-off controls.
The sole build-local change enables `CYD_OPENETH_PBUF_FAILURE_PROBE` and its
explicit linker wrapper. Original audio cores, priorities, stacks, channels,
TLS/TCP capacities, timeouts and watchdogs remain in the bound configuration.
Application descriptor date/version intentionally retain the original A/B
metadata; these are not clean new production release images.

The table and lock occupy 128 + 8 bytes in `.dram0.data`. DRAM data grows 136
bytes; heap-start grows 144 including 8 bytes of linker alignment. BSS and IRAM
text are unchanged. RTC remains 104 used +24 reserved, with 8,064 free, because
the independent 64-byte access probe stays enabled while WS RTC placement is
off. Static frames are 48/192/160/48 bytes for wrapper/dump/PCM EOF/PCM write.
Those are not a total call-depth or physical stack-margin proof.

Actual linked code resolves all four pinned external TCP pbuf call sites to
the wrapper. Its one original allocator call dominates exits without a cycle;
the only other reachable calls are the approved critical-section helpers.
The same-object `pbuf_clone` call bypass is explicit. Four ELF mutation controls
reject wrong targets/literals, duplicate original calls and a nonfunction
wrapper symbol. This does not claim complete runtime/global allocator coverage.

Project PCM-before/PCM/probe Tidy checks have zero project warnings/errors.
SDK pbuf/tcp_out frontends also complete cleanly with their preserved command
and configuration equivalence. Separate system-inclusive reports retain 18
existing SDK-header warnings per profile, without new suppression. They cover
intentional address mapping, pinned task/ISR macro aliases and system time
helpers unused by this probe; those helpers still need valid input contracts
when used elsewhere. Raw reports remain available rather than being erased.

The pause occurred after all GCC and ordinary Clang checks had finished.
Only the missing continuous-DAC all-header report was collected on resume.
The completed resume audit rehashed 61 source pins, 303 protected bindings,
2,855 original object members and 2,858 current compiled outputs. This packager
uses that immutable audit and checks small selected text inputs; it deliberately
does not rehash/reinflate large binaries/archives while QEMU is running. Their
hashes are prior audited identities, explicitly labeled in input-bindings.json.
Full caches, executables, ELF/maps, object archives and private TLS material
remain local. This is selected proof, not full compiler dependency closure.

Earlier linked-verifier reports and mutation failures are preserved separately.
The two resumed-audit helper rejections were path/count assumptions: fixtures
contain JSON only (compiled snapshots retain headers), and 2,855 is the combined
object count, not a per-profile count. Original helper bytes, corrections and
outcomes are retained. No artifact mismatch was hidden by either correction.

Public log copies neutralize personal home components only; redactions.json
binds exact original/published hashes and replacement counts. Raw originals
remain local. All outcomes, counters, source and non-log JSON bytes are exact.
Recipe copies are for review; they rely on original private build paths and
are not standalone instructions to execute from this public directory.
