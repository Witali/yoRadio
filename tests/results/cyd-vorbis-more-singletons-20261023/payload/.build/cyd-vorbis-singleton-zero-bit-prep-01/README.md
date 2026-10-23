# Preferred-zero singleton comparison: source-only preparation

Four additive map1 controls are proposed: map1_dense_single_d16_seq0_wire0,
map1_dense_single_d16_seq1_wire0, map1_sparse_single_d16_seq0_wire0 and
map1_sparse_single_d16_seq1_wire0. Each starts from the corresponding actual
four map1 cases of the frozen original eight-case singleton corpus. Each new
audio singleton token is zero. The comparison output will contain eight cases:
the four original map1 cases copied byte for byte, followed by four new controls.
The original full eight-case corpus, bit1-tolerance cases and failure history
remain preserved and are never replaced or reclassified.

Original generation manifest SHA256:
3ad3a1f9b466d92b2c701c787bdec42ed708cfa9146a3804dcf3d5cc766aeadf.
Original matrix SHA256:
aa6aeb079bf7b810e0aee0e251468eddd3fb6bf2049bad6d2f9ba91aca2a1294.
Actual completed original host report SHA256:
5bc50a664ecc5e5cac92119ff6efc9cd211194ac7f43d9f8471e84cde61f68e6.
It remains NONPASS for dual-reference qualification: Xiph accepted all eight;
native rejected lookup2 for the first four and packet decoding failed for the
last four map1 cases without PCM. The packet error text does not establish an
operating-system/security rejection. The cause is unknown. No new native,
target, PCM or root-cause outcome is assumed by this preparation.

The normative basis remains public Xiph Vorbis I specification section3.2.1,
Errata20150226: https://xiph.org/vorbis/doc/Vorbis_I_spec.html . A singleton
consumes one bit. Encoders are advised to write0; decoder tolerance includes1.
These controls separately exercise the preferred encoder bit. If native zero
controls eventually pass, that may narrow the tolerance question; it will not
erase the original cases or independently prove the cause of their failures.
The unchanged prior preparation/PUBLIC-SOURCES.md retains full primary references.
No additional web download or invented web-byte hash is claimed here.

Each four-case new set has112 singleton tokens: fourteen packets, two channels,
one dimension16 vector token per channel. The eight-case comparison therefore
has224 token observations, sixteen aligned token positions per packet. Exactly
56 old one-bits become zero (four cases times fourteen packets). Identification,
comment, setup, vector values, classwords, packet type/modes/windows, offsets,
packet lengths and padding are unchanged. Each pair has identical public
Fraction lookup vectors, residue0 spectra and intended PCM sizes. Four explicit
Xiph PCM equality pairs are proposed; actual equality requires future decoding.

generate_zero.py performs a bounded raw-bit rewrite using the frozen original
field reports, checking actual original bit values and exact two-token shape.
It uses the normal exact prior generator's unchanged public page helper to
rebuild Ogg with the original serial, sequence, granules and flags. All raw input
bytes and all source identities are checked before and after. No helper/global
is rebound, and no synthetic packet number or metadata is used.

independent_zero_witness.py loads the exact prior independent witness snapshot
normally. The old parse_audio function is invoked only on original alternating
cases, unchanged. A separate parse_zero_audio is adapted from its reviewed
source and explicitly reads each new token with Reader.exact(1,0,...). Ordinary
unchanged Reader, exact Fraction table, original-index, residue0 interleave,
header and CRC helpers are reused. zero-audio-function.diff records that source
adaptation. No parser policy is suppressed or monkeypatched.

The new witness checks all112 packets and224 token observations. It compares all
non-token bits including padding, strict case and field metadata, original entry
indices0/4, unchanged setup/identification/comment, and independently validates
all136 complete-packet Ogg pages. Raw page header and lacing bytes must match
except CRC, which is independently recomputed. The witness receipt can establish
finite bit/spectrum/carrier equality only, never PCM/reference/target success.

test_zero_controls.py contains24 proposed host methods, including all four full
pairs, original preservation, explicit zero-token rejection, unchanged original
policy, classword/mode/window/floor/size/padding controls, metadata offset/bit
checks, non-token bit comparisons and independent Ogg CRC. Negative bytes remain
host-only controls. No new generator, witness, control, reference decoder, SDK,
unit, compiler, QEMU, Git or device operation is executed during this preparation.

Future root-owned sequence, after source review and using actual terminal receipts:

```powershell
# Working directory: this preparation directory.
python -B -X utf8 -m unittest -v test_zero_controls

# Working directory: task worktree. Create a fresh eight-case comparison.
python -B -X utf8 .build/cyd-vorbis-singleton-zero-bit-prep-01/generate_zero.py `
  --readiness-sha256 <reviewed-readiness-sha256> `
  --output .build/cyd-vorbis-singleton-zero-bit-generated-01

# Pin the actual generator-returned manifest hash; receipt stays separate.
python -B -X utf8 .build/cyd-vorbis-singleton-zero-bit-prep-01/independent_zero_witness.py `
  --readiness-sha256 <reviewed-readiness-sha256> `
  --generated .build/cyd-vorbis-singleton-zero-bit-generated-01 `
  --manifest-sha256 <actual-generated-manifest-sha256> `
  --output .build/cyd-vorbis-singleton-zero-bit-witness-01.json
```

Only after those actual gates may root run independent reference comparison.
Failure/interruption remains NONPASS and must be retained. Future target evidence
and full G6/production/physical acceptance remain separate. No original eight-case
failure, policy, source, campaign or archive is changed by this preparation.
