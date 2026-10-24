# Current31 publication verification, 2026-10-24

The [final archive](../vorbis-current-format31-20261024/CHECKPOINT.md) passes its
offline integrity and independently recomputed numerical checks. This confirms
the complete measured **BOUNDED_CORPUS_PCM_REJECTED** result at the unchanged
bound of 2 S16 units, not codec qualification. All 31 cases / 434 raw packets /
738560 PCM bytes, 14 relations per decoder, 37 retained qualified Xiph WAVs,
74 historical reference children and 30 native lookup2 refusals are checked.
All 31 old/current target PCM vectors remain byte-equal.

Final manifest SHA256:
`503bfcf4eeac998b703040abf9c99a86c1b98af72ae97b2214e2755e5ca0e913`.
It contains 3595 logical aliases, 660 content-addressed objects and 885 explicit
identity-only omissions. The actual collector02 command completes with exit0
(terminal chunk `47ea84`); offline-verification02 completes from the parent
checkout with exit0 (chunk `ca0226`). Their original owned-process receipts and
stdout/stderr are saved here. Neither command runs an SDK, QEMU or decoder.

## Initial checker failure

The first collection completed with exit0. Its first offline verification
terminated with exit1 (chunk `1413d4`): the host-input branch demanded a saved
body for the deliberately omitted host `python.exe`. The initial manifest,
collector/verifier sources and both original command receipts/logs are retained
under `attempt01-*`. The initial complete archive is also preserved locally at
`.build/vorbis-current-format31-archive-attempt-01`; it is not claimed to pass.
Initial manifest SHA256:
`047fc56d902fbf26330226507c0c9f073d66e092de3dcacc6407218a498810bc`.

The exact correction is saved as `successor02.diff`. The final verifier permits
identity-only evidence only for the recorded host Python/CMake executables with
an explicit omission, and still checks their recorded SHA256 and size. Other
source bodies remain required. The collector changes only its verifier-template
filename. Original target, corpus, reference and numerical inputs are unchanged;
no target or reference campaign is repeated for this correction.

Final collector SHA256:
`7964c166e19a52323632451bb4f903616b3e3bca34bd99916a04cdd79075aa53`.
Final verifier SHA256:
`1111dbac1c80379d4845d0032c2d67214aa142953c4e53b5c6480ed55aa491b0`.

The first manifest is a record of that failed-checker publication, not a claim
that every omitted binary is reproducible. Both archives explicitly omit
replaceable binaries/tools by identity, do not provide full SDK dependency
closure, and distinguish the observed Ninja recipe from independently observed
linker execution. Full codec conformance, production radio integration and
physical acceptance remain open.
