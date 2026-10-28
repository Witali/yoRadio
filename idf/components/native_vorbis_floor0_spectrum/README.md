# Packet-frame floor0 to a scaled binary64 spectrum

The caller prepares one decoded type0 channel and then materializes its
candidate spectrum for the existing reused Xiph binary64 IMDCT. Exact residue
integers multiply the dyadic53-bit gain factors before a single rounding;
residue is not first narrowed into floating point. Frame/setup/amplitude/LSP
provenance remains borrowed by the plan. Consume it before any front-end reuse.

Absent floors stay silent even for coupled nonzero residue. Active mapping
domains and exact poles are classified before finite zero-residue shortcuts.
Whole-channel precision/wider routes retain source data and remain unfinished
fallback work, rather than new format rejection rules. Ordinary gain evaluation
and Bark mapping are approximate; a candidate is not a universal precision
certificate or a production route selection.

Storage is caller-owned and reused between channels. No allocation, task,
window/overlap/PCM operation or changed core binding is introduced. See
[the design](../../../docs/CYD_VORBIS_FLOOR0_SPECTRUM_DESIGN.md).

[Qualification](../../../tests/results/vorbis-floor0-spectrum-20261028/CHECKPOINT.md)
includes all434 original raw packets plus13 supplements through actual frame
decode, floor0/floor1 spectrum and the unchanged IMDCT. Separate exact integer
product/rounding tests cover all supported widths. Both new C units have clean
Clang diagnostics and source-only C/C++ builds for LX6/RV32IMC. This component
remains unselected by production; full synthesis/PCM, certified gain/wider
fallback and native/resource gates are still open.
