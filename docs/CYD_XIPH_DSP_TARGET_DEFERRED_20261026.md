# Deferred Xiph DSP target qualification

The source-built Xiph DSP initialization candidate passes3584 focused host
scenarios under ASan/UBSan, alongside every original31 PCM byte and the existing
resource suites. It checks decoder constructor allocations, partial lookup/PCM
ownership and fresh-header recovery. This is an isolated candidate; the radio's
selected Espressif path and production task affinities are unchanged.

The first ESP32 SDK6.0.2 build completed. Its QEMU run emitted every resource
completion marker and all31 stream completions, but the unchanged strict reader
rejected it because task_wdt reported IDLE1 starvation five times during the
long series of DSP allocation/reopen tests. Command exit0 and complete capture
markers do not qualify a run with watchdog diagnostics. The report remains
NONPASS, with native numerical comparison unqualified.

Preparing a fixture-only scheduler yield between completed test scenarios was
stopped by an automatic review. The subagent returned:

> This content was flagged for possible cybersecurity risk.

This is a tooling restriction, not a confirmed cybersecurity defect in the
firmware. No alternate phrasing, replacement agent or execution route was used
to bypass it. The fixture remains byte-identical to the host/native snapshots,
SHA256 `09dc6f13d7034ba2f26068aac79947756ae4804de8e67aabd756a5799433fde5`.
No scheduler change or new decoder/SDK run of this DSP fixture followed that refusal. The watchdog
and original reader checks remain enabled.

The later independent [comment API qualification](../tests/results/vorbis-xiph-comments-20261026/CHECKPOINT.md)
executes only metadata utilities in its own project; decoder/DSP symbols are
absent from that ELF. It neither changes this fixture nor qualifies its gate.

The [saved checkpoint](../tests/results/vorbis-xiph-dsp-20261026/CHECKPOINT.md)
retains the host PASS and native NONPASS separately, including the preceding
constructor's sanitizer failure and the automatic-review response. Offline
evidence verification must preserve this distinction; it cannot upgrade the
native result by removing diagnostic lines.

Resume the fixture scheduling work through the normal approved workflow later.
Then repeat the complete native gate, independent PCM comparison, post-change
Clang analysis and final publication. Packet-arena/floor/residue OOM propagation,
allocating comment utilities, format/range and radio integration remain in the
[transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md). Hardware acceptance is also open.
