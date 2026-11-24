# RTC-off ordinary diagnostic controls

Source/HEAD/index are fixed at 7595a79958b8a2ef56babb24c43259fcf536b6dd.
Root authorized sequential compilation after bounded preflight, legacy first,
then PDM and continuous. Actual disk unexpectedly fell below the unchanged
2 GiB compiler guard; builds are held until root reports space recovery.
No additional publication or confirmation workflow is introduced.

The sole effective configuration delta is WS_STATUS_RTC_SLOW true to false.
rtc_access.c is independent and keeps its own 64-byte RTC probe ON. Expected
RTC usage is 104 bytes plus a separate 24-byte reservation, leaving 8,064.
All five workspace objects return to ordinary DRAM: BSS and heap-start each
increase 6,560 bytes. Other task/control/DMA objects stay in ordinary DRAM.
TCP, full TLS buffers, watchdogs, cores/priorities/stacks, channels, codecs,
all diagnostic probes and exact-length OpenETH source remain unchanged.

Old copeneth24/cws24r fixture, ELF/map/config/non-app inputs and all 24
production app/metadata files are protected by logical-byte/hash guards.
GCC caches are reused; one fresh shared Clang configuration is used serially,
with per-profile configuration/command bindings frozen before reuse. There
are no cache clones or directory deletions.

The original PROJECT_VER and SOURCE_DATE_EPOCH deliberately preserve A/B
descriptor metadata. They do not identify a clean new production release.
Image/ELF/OTA/header/descriptor/frame and exact configuration comparisons
remain strict. Whole WS and SDK-driver Clang use matching prior catalogs.
Object comparison records raw differences separately and requires allocated
code/data, relocation bytes and relocation symbol semantics unchanged outside
the WebSocket TU. Unexpected differences preserve a NONPASS for review.

The QEMU executable is pinned to 28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4
but is not launched here. Root owns complete HE-AAC/two-client native tests,
including final post-asset/post-close health. No physical acceptance, staging,
commits, pushes or tracked edits are performed by these recipes.
