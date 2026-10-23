# Complete mono21 public raw target source preparation

This is a separate source-only preparation. Existing generators, corpora,
reference campaigns, callers, protocols, production sources and captures remain
unchanged. No prepared code, controls, recorded-reference replay, SDK, compiler,
QEMU, decoder, Git or physical device was executed by this agent.

`AUDIT.md` records the exact existing21 raw fixtures and actual dual-reference
qualification. `source-inputs.json` pins the complete canonical corpus and source
origins. All21 original descriptors and raw bytes retain original order and exact
fields. No fixture is relabelled or regenerated.

`protocol.py` and `target/cyd_vorbis_mono21_qemu/main/main.c` are focused successors
of reviewed protocol5476/caller37ea. They accept channels1/2, count only real PCM16
channels and require exact public decoder metadata. Mono `nz_r` is always0. Stereo
still requires both actual channels nonzero. All packet sizes/full consumption,
overlap frames, PCM byte counts, rate/16-bit info, canaries, four transition types,
event order and complete final masks remain strict. Caller capacity is ample16KiB,
input512B. Worker remains core1/priority3/stack16384 and coordinator core0.

`test_protocol.py` contains30 meaningful host-only controls, including mixed21
acceptance, mono odd-frame stride, stereo interleaving, metadata relabelling in
both directions, wrong mono stride, phantom right, silent actual channels, primer,
partial frames/consumption, canaries/rate/core, truncated PCM, missing/duplicate
events, transition/case totals, metadata PCM/frame tampering and20-case rejection.
Synthetic transcript samples exist only inside these tests; they are never a
codec/reference result. These controls await root execution and retain no claimed
test pass in this source preparation.

`prepare_runtime.py` is the only materialization entry point. It verifies frozen
source identities and the exact actual mono21 qualifier report, actual wrapper
terminal0/profile/operands/logs before creating output. It then copies all109
canonical corpus files without changing any bytes, builds a strict21 contract,
and uses `materialize.py` to render/recover all105 C arrays/21 descriptors through
an independent bounded C reader. Its five header corruption controls remain.
Normal SHA-pinned imports reuse reviewed formatting helpers; no monkeypatching.

`reference_binding.py` binds each of21 unchanged cases to its actual host input,
qualification, child receipt and complete recorded WAV/framemd5 for each decoder.
The unchanged recorded qualifier helper/carrier are copied normally as
`recorded_qualification.py`/`carrier.py`; no decoder runs. Full recorded reference
PCM lengths and per-packet MD5/PTS are replayed, every channel/transition is checked,
and the complete native/Xiph error is recomputed under the unchanged bound2.
Only this existing21 campaign has `dual_reference_passed=True`. The previous
unrelated singleton8/map2 and other numerical NONPASS reports are not reinterpreted.

Derived full-model counts must be21 cases/294 packets/464640 PCM bytes,
654 protocol events,mask2097151,105 arrays/63 full raw arrays. Those finite expected
values are crosschecked against independently parsed descriptors. The controller
is first published only after actual qualifier gating, full reference binding and
header readback. `controller.template.py` contains unresolved placeholders and is
not a runnable target controller. Its final output will use QEMU snapshot/no NIC,
public raw open/decode/close only and retain all full PCM outputs separately.

Root review/execution order (none performed here):

1. Review source/diffs/readiness, then run host-only controls with the actual
   command wrapper, recording all output and a real terminal result.
2. After passing controls, run create-only materialization:

```powershell
& $TaskPython -B -X utf8 .build/cyd-vorbis-mono-mapping-runtime-prep-01/prepare_runtime.py `
  --output .build/cyd-vorbis-mono-mapping-runtime-01 `
  --qualification-sha256 c31a87de53327cb0e43215f92339b07fd64c48ba57dbde8778328f298b9f5684
```

3. Review the actual preparation/contract/header/controller hashes and binding21,
   then root may run that sealed controller with the independently reviewed
   contract/header SHA arguments into a separate fresh capture directory.
4. Preserve any actual NONPASS. Numerical target comparison requires a separate
   reviewed adapter and actual successful complete target terminal/report.

Source-only closure does not substitute for those actual operations. There is no
target result, numerical qualification, production change, hardware experiment,
full-G6/conformance claim, Ogg API, reset/EOF/OOM extension, private handle query,
vendor behavior diagnosis or AAC work in this preparation.
