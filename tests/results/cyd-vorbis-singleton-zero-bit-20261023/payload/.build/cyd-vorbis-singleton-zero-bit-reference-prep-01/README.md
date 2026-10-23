# Preferred-zero singleton recorded-reference qualifier: source proposal

This preparation adapts the complete recorded singleton qualifier for the
actual eight-case preferred-zero comparison. It has assembled/read source,
parsed ASTs, hashed raw files and inspected recorded JSON/text metadata only.
It has not imported or executed the qualifier, carrier, construction controls,
generator, witness, reference decoder, compiler, SDK, QEMU, Git or device.
No actual PCM payload has been read or compared by this preparer. Root owns
review and every future qualification run.

The original four map1 cases are preserved byte for byte; four additive
`_wire0` cases use the preferred zero value for each consumed singleton bit.
Each token still consumes one bit. This preparation does not introduce
zero-length codewords or replace the original bit-1 tolerance cases.

## Exact original and current evidence

The current actual host report is
`fab48896b1623c9b0cafbb11fb9d424d4bfbca5bfe79253cb3605926dc59ce3c`.
Its actual outer process returned 1 after completing all 16 decoder children.
All eight Xiph cases succeeded and all four original/preferred-zero PCM equality
pairs passed. The first four native commands preserve the original map1 packet
failures: actual return code 4294967295, zero-byte WAVs, empty framemd5 stdout,
and packet submission/processing diagnostics containing `Operation not permitted`.
Their logs do not contain an unsupported-lookup diagnosis. The last four native
commands returned 0 and produced complete PCM; the original driver reports
maximum signed-S16 error 1 for each versus Xiph.

This finite result supplies no operating-system, security or opaque decoder
cause. The original failing cases and dual-reference NONPASS remain intact.
The predeclared cross-reference bound stays 2 LSB; it is not a standards-wide
accuracy tolerance or target acceptance criterion.

Original construction preparation 02 is pinned at
`8555802913d96b6e4c25599a8cf60e122700783004d74bee52da2e7e23a1cb03`.
Root recorded 28 passing host controls and actual generation/witness exit 0.
The generated manifest is
`c300a312f36abff95e9219479c7d0edd59b47ce09cf6a6dcd6af25f304e45858`;
the independent raw witness is
`445b0e31707b27192cdb32d8f640e7f6b77fefac9970e9a8620860324f953bfd`.
It records 8 cases/112 packets, 112 new zero tokens, 224 comparison tokens and
exactly 56 cleared old one-bits. Non-token fields, offsets, padding, setup,
vectors and carrier fields remain unchanged. Its raw witness remains explicitly
separate from reference/PCM/target qualification.

The predecessor complete eight-case singleton host report remains
`5bc50a664ecc5e5cac92119ff6efc9cd211194ac7f43d9f8471e84cde61f68e6`;
its actual Xiph-qualified/dual-NONPASS qualification is
`a5b5d47dca0d0826cdcff1dac010c78a836fdd44c053f93cf2818fb1877559bc`.
The new qualifier requires every current original map1 case to equal the
corresponding predecessor case 4..7 in all fields and all raw header/setup/
audio/carrier bytes. It independently reads both complete Xiph WAV/framemd5
pairs and requires full PCM byte/hash equality to those earlier qualified
records. It never truncates samples or borrows a successful new result for an
unavailable original native result.

## Proposed independent recorded qualification

`qualify.py --profile zero8` retains the unchanged normal carrier import,
complete WAV reader, per-packet framemd5 and signed-S16 comparison definitions.
It launches no process or decoder. It checks exact original/current reports,
actual receipts/logs/tool pins, construction/witness/control terminal records,
all 16 current child terminals, strict decoder options, actual frozen raw data,
CRC carrier/raw-packet/granule equivalence, full WAVs and packet accounting.

Exactly four native children must be successfully compared and four must remain
the recorded packet failures. Lookup2 refusal count is zero in this comparison.
Every successful native/Xiph comparison must recompute the complete reported
maximum and remain within the unchanged 2-LSB bound. Every Xiph equality pair
must hold. Native original/new pair equality stays unavailable because the
original native outputs do not exist; it is not marked as a successful check.

A future successful qualifier reports `XIPH_QUALIFIED_DUAL_NONPASS`, eight Xiph
cases, four native comparisons, four native packet failures, 112 paired raw
packets and 225,280 Xiph PCM bytes. It retains original failures and all original
metamorphic results. It also records the four complete historical raw/Xiph
preservation checks and the predecessor qualification identity. Cause diagnosis,
target execution, numeric target qualification, full G6, production and physical
acceptance remain false/unqualified.

Full predecessor qualifier/pins/carrier source copies are retained under
`provenance/`; exact source adaptations and hashes are retained. Existing
construction/campaign originals stay at their exact pinned paths and remain
untouched. This is a focused reference qualifier, with no target runtime scope.

After source and readiness review, root may run once to a fresh independent
output, recording its actual terminal and logs:

```powershell
python -B -X utf8 .build/cyd-vorbis-singleton-zero-bit-reference-prep-01/qualify.py --profile zero8 --repository . --campaign .build/cyd-vorbis-singleton-zero-bit-host-01 --outer .build/cyd-vorbis-singleton-zero-bit-host-01-command.json --output .build/cyd-vorbis-singleton-zero-bit-qualified-01
```

Source readiness claims only reviewability. It does not claim this future
qualifier or any PCM comparison has run during source preparation.
