# Xiph DSP initialization candidate, 2026-10-26

**Host PASS; ESP32 QEMU NONPASS.** Host ASan/UBSan completes3584 new DSP
scenarios and all original31 PCM outputs exactly:434 packets,738560 bytes,
maximum error0 at unchanged bound2, all14 original relations. The SDK build
completes, but the unchanged native reader rejects watchdog diagnostics.
Native numerical qualification and post-change Clang remain open. This isolated
candidate is not selected by the radio. The [preceding header checkpoint](../vorbis-xiph-headers-20261026/CHECKPOINT.md)
remains a separate qualified source version.

## Source change and ownership

Seven additional [exact edits](../../../idf/components/native_vorbis_xiph_port/edits.json)
check the shared decoder constructor, MDCT, floor0/floor1 and residue lookups,
and make partial cleanup safe. Fresh DSP state is zeroed before config
validation. Required decoder allocations stop on refusal. Transform/PCM/backend
pointer arrays are zero-initialized; partial residue arrays/rows are guarded.
`pcmret` is freed independently of `pcm`. `vorbis_info` continues to own complete
or partial codebooks and must outlive DSP cleanup. A failed constructor may
have consumed static books: recovery closes the stream and replays all headers.

The [private checked MDCT initializer](../../../idf/components/native_vorbis_xiph_port/edits/mdct-init.after.c)
stops at either allocation refusal, frees partial storage and leaves a zero
lookup. Its original void wrapper, public headers and successful table formulas
remain unchanged. [The documented public synthesis API](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis_init.html)
retains0 on success and1 on error. No alternate transform/synthesis arithmetic
or shared mutable failure flag is introduced.

The port now applies23 exact edits to10 C units and copies two owned private
headers, preserving all116 original baseline files. The generated tree has128
source files plus PORTING.json;22 library C units remain selected.

Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
Port manifest: `33931bdee52616bfcd87b10d9dbe6e872d1648e718ea0b3ff93e460240d2482f`.
Generator: `8e48c251b3df4feda8bc1753db332dae0d9a4d4ed4e7eaca530cfbeff36a1e3d`.

## Qualified host evidence

The [DSP fixture](../../native/vorbis_xiph_dsp.c) fails each observed direct
allocation ordinal during synthesis initialization for all31 original streams.
Each refusal must return1, stop further allocation, leave a clearable zero DSP,
release all tracked ownership after stream close and permit fresh headers/DSP
to reopen successfully. Six synthetic setups cover4channels,3books,2floors,
2residues, classifications2/partvals4 and cascades5/11, exercising later PCM,
book/backend/partbook/decodemap rows. Both floor types and all residue types
are asserted. Failure injection is disabled before packet decoding.

Each original stream has full14packet float-bit fingerprints and exact counts
before/after its entire sweep. Per-ordinal reopen checks constructor state;
full audio is not decoded after every individual refusal. These fingerprints
are recovery identities, not independent numerical oracles. Direct checked
and legacy MDCT controls cover sizes32/64/128/512/8192, both allocation sites,
lookup guards, zero/clear and fresh table fingerprints. Size32 covers table
initialization for half-rate geometry, not full half-rate PCM qualification.
Missing/incomplete-header fresh DSP controls and independent pcmret-only
ownership cleanup are included.

Host builds22 library plus8 fixture units with active assertions and ASan/UBSan.
All34 owned Linux commands terminate with reaped children and vanished owned
groups; execution stderr is empty. Existing11 arena scenarios,200864 book
checks,124754 bit probes,3997 residue and1598 header scenarios pass. The separate
complete retained-reference host S16 comparison is exact for every original
case. Generation16, protocol13 and PCM/binding12 pure tests pass.

The preceding block source, retaining the already qualified arena repair but
reversing only the new DSP init/clear edits, is separately linked in slot02
with the same other host objects/fixture. It reproduces UBSan's null backend
member access at block.c:197 through dsp_sweep. Compile/link exit0; executable
exit1 is expected, before PCM publication. Source/object/binary, traceback
and three nonce-bound owned command receipts are saved.

## Unqualified native attempt and deferral

SDK6.0.2 compiles all30 selected units and both private-header dependencies.
Seven owned commands through QEMU terminate normally. The raw log contains44
resource markers, all31 case completions and final capture markers on worker
core1/priority3/stack16384, coordinator core0. However, it also contains five
task_wdt reports of IDLE1 starvation during the long DSP trial sequence.
The original strict reader rejects the untouched log; the native report and
outer command remain NONPASS/exit1. Complete markers and command exit0 do not
qualify that runtime. Native PCM was not independently numerically qualified.
Final SDK/source-check flags were not reached and remain false; no full
post-run SDK-clean claim is made.

Preparing a fixture-only yield between completed test scenarios was stopped
by automatic review with “This content was flagged for possible cybersecurity
risk.” The [deferred note](../../../docs/CYD_XIPH_DSP_TARGET_DEFERRED_20261026.md)
records the action and remaining gate. No alternate request, replacement
agent, watchdog suppression or native retry followed. Fixture SHA remains
`09dc6f13d7034ba2f26068aac79947756ae4804de8e67aabd756a5799433fde5`,
matching both executed snapshots. The review refusal is not evidence of a
firmware cybersecurity defect. Encoder-only allocation paths, transitive libc
allocations and whole-decoder OOM/stack bounds are outside this result.

## Saved evidence and next work

[captures.zip](captures.zip):955 members /9486659 bytes.
SHA256: `4134d6c23649bddcf21e996b746920625bd94152290f956183082645125afc10`.
Manifest SHA256: `c7a4da5155aafba7daa902d7751c6439bebf60eb39141adc49a1fab4c1e4f830`.
The archive retains host objects/executables/PCM, preceding-source failure,
native sources/generated units/compiler records/images/raw logs and refusal
evidence. Raw QEMU images are test fixtures, not production firmware.

The [offline verifier](../../verify-vorbis-xiph-dsp-checkpoint.py) passes while
explicitly returning host_qualified=true, native_qualified=false and
watchdog_nonpass=true. It verifies every member, exact edits, host PCM/relations,
source-swap witness and diagnostic native resource markers, and confirms the
unchanged strict reader still rejects the unmodified watchdog log. It launches
no decoder/compiler/SDK/process and extracts no files. It does not upgrade the
native result or claim full external tool/SDK binary dependency closure.

Next remain the deferred target scheduling gate and its native PCM/Clang
qualification, packet-arena/floor/residue OOM propagation, allocating comment
utilities, other stack scratch, format/range and radio integration. The other
transfer-plan gates and physical acceptance remain open. Production display,
audio backends, task bindings and decoder selection are unchanged.
