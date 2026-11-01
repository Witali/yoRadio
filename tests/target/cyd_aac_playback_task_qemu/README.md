# Actual CYD public AAC playback task diagnostic

This new sibling qualifies complete original LC, HE and HEv2 fixtures against
the committed 36-case public same-vendor integration oracle. It makes no
independent codec-conformance claim and uses no private layout, compact owner,
reset hook, archive patch or external network.

The build compiles the complete production stream/decoder/output tasks, state,
health, registration, output renderer, settings and shared normalizer. Only HTTP
transport and public PDM/GPIO hardware calls are seams. Forwarding observers call
the actual output functions. Complete source PCM and confirmed geometry are
checked at the real output entry; PDM rendering is observed without claiming a
new independent resampling oracle. AAC packets retain legacy speaker layout
and zero Opus gain; both ordered public setter calls remain real.

All six complete fixtures run mixed EOF, partial Stop/reopen, maintenance/resume,
and one-byte/257/4096-byte HTTP schedules. Independently counted early ADTS
boundaries hold short streams before HTTP EOF. Genuine held reads plus actual
PCM must precede cancellation. Stop uses real output-owner discard completion,
sequence/timing and a quiet interval; task ACKs, state and generations are never
injected. Original core/priority/stack profiles remain stream 0/3/6144, decoder
1/5/16384 and output 1/6/4096. Assertions, canaries, heap poisoning/integrity and
both idle watchdogs remain enabled, with bounded 30-second observation waits
and a 600-second whole-QEMU deadline.

An isolated public reference phase first decodes all six bases and four
continuous ADTS rate/layout/late-SBR/PS observations. It owns genuine public
handles and normal registration cleanup, without the production parser/pending
helper or any reset hook. Base full hashes must match the committed checkpoint.
Continuous observations use their actual continuous reference hashes and
metadata runs; separate PCM hashes are never concatenated. Unchanged-ADTS stock
limitations remain observations, with no nominal HE/PS conformance claim.

The actual application then runs 36 base/lifecycle cases and 12 continuous
observations, using real SDK tasks/queues/ownership and confirmed-PCM state
publication. Public status can be ahead of queued PCM; state/formatter behavior
is checked separately from actual configure/write arguments.

The controller authenticates the root-authorized twelve-file release before
freezing full source/SDK/compiler identities. Preparation and preflight do not
execute native code or freeze production. A native result is qualified only by
its complete terminal capture and separate data-only witness/evidence checks.

```text
python -B tests/run-cyd-aac-playback-task-qemu.py --prepare-only --output .build/<fresh-preparation>
python -B tests/run-cyd-aac-playback-task-qemu.py --preflight-only --output .build/<fresh-native-campaign>
python -B tests/run-cyd-aac-playback-task-qemu.py --output .build/<fresh-native-campaign>
```

The image is diagnostic only and must not be flashed as production firmware.
Physical outputs, enabled normalization, real network/TLS/TFT margins, OOM and
backpressure remain separate requirements. Earlier frozen gates are unchanged.
