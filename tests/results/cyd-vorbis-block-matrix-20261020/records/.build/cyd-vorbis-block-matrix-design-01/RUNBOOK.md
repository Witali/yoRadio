# Review/execution entry points (not executed here)

1. Review DESIGN.md, matrix_candidates.py and pins.json. The generator is a pure
   construction/command-plan proposal, not an executable validation assertion.
   It has not generated candidates yet. Retain its pins and fresh source freeze.
2. After review, construct the72 candidates in a fresh child directory:

```powershell
& $hostPython -B .build/cyd-vorbis-block-matrix-design-01/matrix_candidates.py `
  --output .build/cyd-vorbis-block-matrix-host-01 `
  --ffmpeg $pinnedFfmpeg --ffprobe $pinnedFfprobe
```

The two tools must match the actual hashes from frozen
.build/cyd-vorbis-format-prep-01/reference/report.json. Preserve version/decoder
inventory receipts too; construction hashes their files but does not establish
their runtime behavior. Existing files and outputs are never overwritten.

3. candidates.json contains explicit absolute per-case command plans (not run by
   the generator): packet-frame-probe; decode-vorbis; decode-libvorbis (WAV16, no -ar/-ac). Root's
   bounded host reference executor should use each argv/cwd without a shell,
   timeout30s per command, separate raw stdout/stderr and terminal receipt. The
   functions command_plan(path,pcm_dir,ffmpeg,ffprobe) and candidate_audio(audio,
   family) are reusable source entry points, not target/application hooks.
   No encoder command is part of this first proposed execution.
4. Review all six small-long pairs explicitly in BOTH families:

```text
64/64,64/128,128/128,64/256,128/256,256/256
```

No early stop may silently turn their failure into 30/30 success. An interrupted
run retains partial evidence with validity_qualified=false. A reference tool's
zero exit by itself does not complete the gate.
5. Each generated case exposes id, ogg (relative to output), short,long,rate,
   channels,bits,mode_flags,expected_raw_samples,packet_count,raw_pcm_bytes and
   audio_packet_granules; source changes and future reference argv are retained.
   planned-cases.json is the same72-case identity/dimension/accounting list only,
   explicitly not a generated file inventory or executed result.
6. Bind actual hashes/logs/receipts, probe packet count/metadata, and parse each
   WAV's actual rate/channels/bits/samplecount/nonzero data. Require actual samples
   equal expected_raw_samples, first audio granule0 then exact cumulative raw
   granules. Do not hide an unexplained deficit behind the historical final128
   crop. For each transition case require nonzero PCM in output packets1/2/3/4
   (SS/SL/LL/LS) using the exact expected raw sample boundaries.
7. Compare equal-length native/libvorbis WAV samples without alignment shifts,
   resampling or channel rewriting: max absolute PCM16 difference<=2. Record max,
   sum/mean absolute difference and number of differing samples. Larger differences
   remain nonpass pending review. Target vendor-vs-checked is still byte-exact.
8. Record CANDIDATE_CONSTRUCTED separately from HOST_VALIDATED or UNQUALIFIED.
   Only full36/all 4-transition completion qualifies that realistic family. Preserve
   failures; the separately assigned minimal public fixture is supplemental,
   never a replacement for omitted realistic cells. Actual ffprobe/WAV results
   decide whether the proposed one-packet-per-page transport behaves as intended.

Future target implementation should adapt only the reviewed public raw caller,
fixture/case data and strict native protocol validators. It must preserve source/
tool pins, original vendor prerequisites, metadata, canaries and full accounting.
No SDK/compiler/QEMU invocation is authorized or performed by this prep, and
there is no target runner or new general controller here.
