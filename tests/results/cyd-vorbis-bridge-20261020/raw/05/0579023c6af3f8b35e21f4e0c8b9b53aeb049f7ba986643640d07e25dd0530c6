# CYD Xtensa Vorbis/Ogg audit — 2026-10-20

**Audit complete; implementation, full private ABI qualification, target PCM,
golden output, OOM and conformance remain pending.** Stage 14 is open. This
archive contains source and binary-analysis evidence, with no decoder execution,
firmware build or board run. It makes no speed, CPU-load or RAM-savings claim.
Deferred AAC private owner-view investigation, repair and circumvention are
explicitly excluded.

The immutable [raw report](raw/report.json) is the accepted audit, SHA-256
`debd417874bc176f011603ee09875dfcf2c5cade27aee526bcca997ccf82083e`.
Its original JSON, scripts, disassemblies, symbol output, excerpts and source
snapshots are preserved byte for byte. `input_unchanged_final` records the
historical audit completion check; it does not assert that today's working tree
or SDK still matches that snapshot.

Six findings have exact archive/member hashes, section-relative offsets and
line references: failed-open cleanup reads/frees a freed wrapper; unchecked DSP
and setup allocations; unchecked Ogg simple-state allocation; synthesis before
PCM capacity validation; dropping the retained packet on a second undersized
retry; and swallowed Ogg allocation errors. The report separates these observed
binary call/control paths from partially corroborated private-layout fields.
There is no DWARF in the 38 selected objects and no claim that RV32 and Xtensa
private ABIs are interchangeable. Remaining consumer, alignment, signedness,
linker callback and runtime checks are explicit.

The installed package is `esp_audio_codec` 2.6.2. The target is classic ESP32
Xtensa, ELF machine 94; the donor objects are ESP32-C3 RISC-V, machine 243. Four
archive identities, four tool paths, all selected member identities and public
source interfaces are recorded. Binary artifacts are deliberately omitted:
the four complete vendor `.a` archives, 38 extracted ELF objects and four tool
executables. [omitted-binaries.json](omitted-binaries.json) records each original
path, role, byte count and SHA-256, including archive/member relationships.
Disassembly and symbol text are evidence captured from those artifacts; an
offline check cannot independently reconstruct or execute omitted binaries.

[path-map.json](path-map.json) maps every original audit payload and input to
an archived file or explicit omitted-artifact record. It also maps the raw
report's absolute Markdown line links. The raw report has not been rewritten:
use this mapping to resolve its original `.build`/SDK paths. Content-addressed
source files retain their original hashes under `raw/snapshots/`.

G1–G8 in the raw report are **unrun target gates**: actual Xtensa ABI/linking;
target ample-buffer PCM plus an independent golden; retry/EOF behavior; full
allocation-failure ownership; task/core isolation and actual service behavior;
a standards corpus and explicit supported profile; exact semantic controls;
and target measurements plus production integration. Existing C3 numbers and
fixtures are historical test-method inputs, not CYD qualification. Original
DSP dynamic stack use and the inherited long-block restriction remain stated
limits. Authoritative Xiph specification, Ogg RFC and pinned Tremor provenance
links are in `authorities`; this archive is not a standards-conformance pass.

Run the standalone verifier using Python 3.9 or newer, without SDK, packages,
network, Git or hardware:

```text
python -B tests/results/cyd-vorbis-xtensa-audit-20261020/verify.py
```

The verifier reads only this archive. It checks the complete manifest file set,
byte counts and hashes, accepted raw-report identity, source/payload mappings,
all 80 captured command payloads, all 72 bound excerpts, omitted binary metadata,
six selected finding offsets/line instructions, partial-ABI status, G1–G8 and
scope exclusions. It also rejects executable/archive bytes stored as renamed
source snapshots. These are integrity and selected-entry consistency checks,
not a new native disassembly, compilation, decoder test or proof of the
omitted binary bytes. All archive files are covered by `* -text` attributes.
