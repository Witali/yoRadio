# CYD Vorbis floor1 presence39 recorded evidence

This compact archive preserves the finite valid-input corpus and the actual
recorded reference / emulator measurements. It retains original bytes through
an explicit logical inventory; equal copies share a SHA-addressed payload.
Large text / JSON members use deterministic gzip. Every logical member has its
original path label, byte count, SHA256, encoding and physical storage key.
Original paths are evidence labels, never filesystem read fallbacks.

The corpus has 39 cases (9 mono / 30 stereo), 546 raw packets and 971520 PCM16
bytes. It covers floor1 present/absent, residue0/1/2, coupled and uncoupled
stereo masks, fixed presence schedules and short/long overlap. Separate
constant-all-absent and always-absent-channel witnesses check every guaranteed
silent frame. Active portions require some nonzero output. Residue0/1 scalar
dimension1 does not add multidimensional residue0 placement coverage.

Actual root results retained here include 30 original host controls, 17
canonical controls, complete 78 reference decoder commands, the independent
recorded-reference qualification, the complete 39-case target capture and the
complete 78 target/reference comparisons. The recorded numerical result is
`BOUNDED_CORPUS_PCM_QUALIFIED`: maximum 1 signed-S16 LSB against each reference,
under the unchanged predeclared project bound2. This bound is not a normative
Vorbis tolerance. All original channels/packets/samples and silence witnesses
are retained; no fitting, shift, trim, resampling, padding, swap or duplication
is applied. The report's other false qualification fields remain unchanged.

`verify.py --root <archive> --manifest-sha256 <independently-reviewed-SHA>` reads
only this archive and writes a temporary relocated raw corpus. It verifies the
exact physical/logical SHA closure, full original/canonical corpus, recorded
receipts/logs, full WAV/framemd5 PTS/duration/MD5 and silence witnesses. Ordinary
imports use exact frozen protocol, witness, WAV/MD5 and metric helper bytes.
The original contract model/ID must survive relocation. It replays all1212
target protocol events, checks every persisted target PCM byte, recomputes all78
full comparisons and the original numeric policy/report. It invokes no decoder,
process, compiler, SDK, emulator or device. Source preparation of this verifier
is not a verification pass; root must execute it before canonical publication.

The target uses the inherited nine-command fixture, serial stdio, snapshot
storage and no NIC. It has no QMP lifecycle or full configured dependency walk.
The historical preparation README's broader claims are retained with the
separate factual correction and root execution-scope note. The actual
controller checks its declared tool/variant/build-output identities, while the
independent numerical reader has the narrower scope described in that note.
This portable replay does not claim an independent rehash of omitted live tools,
vendor libraries, firmware/ELF/flash binaries or a complete SDK/build tree.
`omissions.json` preserves their recorded paths/hashes and explicitly excludes
the bodies. Selected frozen text build context is retained without claiming
dependency closure. No production radio source was changed by this floor39
step; canonical test-source promotion was root commit `c252dfeaa`.

See `CHECKPOINT.md` for exact report identities and source limitations. This is
finite recorded evidence, not new target execution, fullG6, complete Vorbis
conformance, physical audio, performance, or production radio qualification.

## Immutable archive successor02

Actual stage01 verification terminated1 (root chunk6015f7) at the advertised
numeric-input closure, before any numerical replay. The required target
`variant/vorbis_repair/setup.c` had no selected logical body/path alias. The
strict guard correctly rejected this archive selection. Actual39 target and
numeric PASS remain unchanged; this is an archive input rejection.

Successor02 keeps verify.py byte-exact (SHA dd6b3364ceba4df6a9972ee4c0fcbaab75be4fd8fa78d21d42fcc180da4fde8b).
It retains all5 actual variant sources, each matched to the recorded source
hash, and117 additional explicit raw snapshot path aliases (39 cases×3 raw
members,7464 bytes). Existing payload bodies are shared by exact SHA; no guard,
helper, codec input, PCM, metric, threshold or omission policy changed.
`input-body-closure.json` records an ordinary bytes/SHA scan of all926 qualifier
and3136 numeric validated-input rows:4058 retained-body rows plus4 preexisting
recorded external-tool omission rows,0 unresolved. This is input-byte accounting,
not verifier or numerical execution.

The exact original stage01 manifest, inventory, verifier, README, checkpoint and
assembly record are retained as logical provenance, without recursively nesting
its full payload. The actual failed receipt/logs, original peer01 review and its
runtime-finding addendum are also retained. The addendum limits the earlier
source review to selected bytes and acknowledges the missing semantic input
closure. Root must review and execute this new stage before promotion.
