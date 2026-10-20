# Exact public raw corpus materialization

`materialize.py` writes a fresh `data.h` from all 17 cases in the frozen contract,
in its original books/floor0 order. This is pure standard-library source
generation and recovery checking. It invokes no SDK, compiler, codec, emulator,
reference, Git or device operation and produces no synthesized PCM.

The contract file must have SHA256
`6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391`;
its model identity must be
`847022a7835de03c0f820b3f8e418e7e8b89b6125d2dba8bdf09712d33d3a65a`.
The frozen target-prep01 protocol, caller and descriptor header are separately
pinned before import/read. Importing that protocol loads only stdlib definitions.
Its contract loader rechecks both exact source matrices and every raw payload.
No frozen source is modified or relabelled as newly qualified.

The emitted header stores 51 full raw payload arrays (identification/setup/audio),
17 uint32 offset arrays, 17 uint8 mode arrays and the exact ordered 17 descriptors.
Identifiers use an ordinal prefix rather than transforming case names. Full
30-byte identification and prefixed setup remain intact. Only the existing
public caller strips their first seven bytes at the config boundary. Header
macros bind model identity, contract-file identity and the total 398080 PCM bytes.
That total is expected accounting, not newly decoded audio.

After writing, a separate restricted-C reader recovers every array/declaration
and descriptor from the actual header text. It compares bytes, types, counts,
ordered identifiers, sizeof expressions, offsets/modes and metadata against the
actual source inputs. It independently reads public identification fields and
recomputes overlap PCM counts. Five named in-memory controls require exact
rejections for a changed ID byte, offset, rate, descriptor order and model hash.
They do not change the saved header. This reader is deliberately not a general
C parser or a compiler; actual declarations/ABI/linking remain target gates.

```powershell
& $python -B .build/cyd-vorbis-format-corpus-materialize-prep-01/materialize.py `
  --contract .build/cyd-vorbis-format-corpus-target-prep-01/contract.json `
  --output .build/cyd-vorbis-format-corpus-materialize-prep-01/generated01
```

Output must be a fresh direct child of this preparation directory. Failures keep
the generated header and nonpassing report. Source identities are captured
before/after; existing caller prep, source matrices/raw files, campaigns and
canonical files remain read-only. Root must review materialization, then bind
this actual header plus corpus_case.h/main/protocol/contract to its SDK source,
compile/link/ELF closure and real capture. The source check provides no target,
numerical-reference, ABI, physical-audio or broad-format qualification.
