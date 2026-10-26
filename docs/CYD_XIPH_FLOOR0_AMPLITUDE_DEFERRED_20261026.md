# Deferred Xiph floor0 amplitude range tests

A read-only audit compared the pinned Xiph floor0 implementation with the
[Vorbis I specification, section 6.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
The six-bit setup field permits amplitude widths 0–63. The current implementation
uses `oggpack_read(...,ampbits)` and signed `1 << ampbits` arithmetic:

- Widths 0–30 have defined ordinary amplitude arithmetic.
- Width 31 reaches a signed shift outside the representable positive int range.
- Width 32 also exceeds the signed shift width and loses unsigned int values.
- Widths 33–63 exceed libogg's single-read limit and become unused floors.

The audit identified a possible complete implementation using at most 31 bits
per read and an unsigned 64-bit accumulator/denominator. This would avoid confusing
a valid 32-bit all-ones value with EOP on ILP32. A zero-width read must still call
libogg: exact-end zero reads succeed, but a previously established EOP remains
sticky. Exact truncation tests must end the available prefix at a byte boundary;
readable final-byte padding is not an implicit packet end. These are design
findings, not an implemented or runtime-qualified change.

The test-preparation agent `/root/floor0_amp_tests` failed automatic review with:

> This content was flagged for possible cybersecurity risk.

The response also suggested rephrasing or applying for Daybreak access. No
rephrasing, replacement agent, alternate tool route or implementation followed
that stop. Root read-only checks confirmed that neither proposed C fixture
(`vorbis_xiph_floor0_amplitude.c` or `_host.c`) exists. No new amplitude oracle,
compiler test, host decoder run or native run was created for these wide fields.
The existing floor0 amplitude implementation remains unchanged.

This review response is a tooling restriction, not confirmation of a firmware
cybersecurity defect. The agent failed before supplying a raw tool receipt;
the statement above records its returned error without inventing a tool action.

Resume the complete width 0–63 regressions and implementation through the normal
approved workflow later. Preserve ordinary-width PCM, every alignment/truncation,
unsigned chunk boundaries, selector/VQ alignment, nominal EOP and required OOM
classification. Existing ordinary-width corpus results do not qualify this gap.

The same read-only audit also confirmed a separate unsigned sample-rate API
issue: valid bitstream rates are unsigned 32-bit values, while the
[public `vorbis_info.rate` member](https://xiph.org/vorbis/doc/libvorbis/vorbis_info.html)
is signed `long`. ILP32 cannot represent the upper half positively through that
member. Removing the positive-rate check or passing LP64 tests alone is not a
complete fix; the API/representation decision and time-conversion consumers
remain open. No rate value is silently clamped or newly rejected here.

The independent channel-scratch placement change affects mapping/residue
storage only. It neither implements nor qualifies this deferred amplitude work,
the packet target preparation or the older DSP target gate.
