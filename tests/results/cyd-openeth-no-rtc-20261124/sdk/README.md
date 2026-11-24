# RTC workspace off: static SDK qualification

Three diagnostic OpenETH fixtures were built at source
`7595a79958b8a2ef56babb24c43259fcf536b6dd`, preserving application TU bytes
from the shared-scheduler implementation. This package covers builds/static
checks and focused Clang only. It contains no native runtime results and does
not close the HE-AAC/two-client resource gate or claim physical acceptance.

The sole effective change from the matched RTC-on fixtures is
`WS_STATUS_RTC_SLOW=true` becoming `false`. The independent 64-byte RTC access
probe stays ON. RTC usage is 104 bytes, plus the separate 24-byte reservation,
with 8,064 free. DRAM BSS and heap-start each increase exactly 6,560 bytes;
every image is 6,560 bytes smaller. TCP11520/10/5760, TLS16384/4096, original
watchdogs/cores/priorities/stacks, channels2 and vendor codecs stay unchanged.

Image/ELF/OTA/header/frame checks and six whole WS/SDK-driver Clang units pass.
Each profile retains 1 WS and 32 SDK warnings, with zero errors/new warnings.
2,855 objects were compared. PDM changes only WS. Legacy and continuous also
have one specifically reviewed SDK bootloader-descriptor date_time change:
only the 24-byte field of its 80-byte section differs, and the archive member,
section and symbols are absent from both linked applications. Exact bytes,
hashes and map/ELF exclusion bindings are included; no generic metadata
exception is allowed. Actual bootloader/partition/SPIFFS/non-app flash inputs
and all 24 production app/metadata files remain unchanged.

The original legacy controller NONPASS (LF expected, SDK header CRLF) and the
first static continuation NONPASS (unextracted descriptor date rejected) are
retained unchanged. The separately named reviewed continuation passes without
rebuilding that image. Source snapshots and all three logs/statuses preserve
the distinction; no original failure is relabeled.

PROJECT_VER and SOURCE_DATE_EPOCH deliberately preserve original diagnostic
A/B descriptor metadata. These are not newly labeled clean production releases.
`summary.json`, per-profile proofs, `input-bindings.json`, and the artifact
manifest bind selected immutable inputs. Full binaries/ELF/maps/databases and
private credentials stay local; this is not full compiler dependency closure.

`recipes/` contains frozen review copies, including the two earlier helpers.
They document the isolated build rather than instructing execution from this
public folder. The packager defaults to dry-run and performs no compiler,
QEMU, network or Git/index operation. Only public log home-path components
are neutralized; `redactions.json` records exact original/published hashes and
counts. Raw local logs and all qualification outcomes remain unchanged.

Native playback, final post-asset/post-close resource health and any NONPASS
runtime result belong to the separate parent package when available. No
default profile promotion or physical Wi-Fi/audio/RTC timing claim is made.
