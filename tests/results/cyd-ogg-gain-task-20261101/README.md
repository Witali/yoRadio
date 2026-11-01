# Actual CYD ordered Opus gain through real PDM rendering

The complete production audio, output, state, health, registration and output
metrics translation units pass **24 actual SDK-task cases** on dual-core LX6 /
ESP-IDF 6.0.2 with unchanged public Espressif decoding. Actual shared settings,
normalizer and its AudioNormalizer implementation are compiled and called.
HTTP transport and public PDM/GPIO hardware functions are explicit seams;
forwarding output observers call the real production functions. No ACK,
control state, decoder internals or generation is injected.

Three fixtures run full EOF, partial Stop/discard/reopen, and partial three-owner
maintenance/token/stale-token/resume. Fourteen additional complete gain/volume
cases and a nine-link same-HTTP chain cover both original 20 ms / 120 ms fixtures at
zero, +/-6 dB, +20/+48 dB and both signed Q7.8 extrema. Mute, final saturation,
pre-skip/end positions, Vorbis bypass and per-link zero reset are covered.
The +48 dB / player-volume 1 case matches its complete independent unsaturated mono
golden; early header saturation would produce a different output.

Every complete logical source remains exactly 2112000 unchanged PCM16 stereo
bytes; every final mono span is 1056000 bytes / 528000 frames. All 32 complete links
match their independent full mono goldens. Nonzero header calibration combines
with the player's cached Q15 coefficients before wide stereo mixing, one final
nearest-away rounding and signed16 saturation. Zero gain retains legacy
per-channel Q15 rounding followed by truncating mono average. Existing adaptive
normalization is disabled through its real settings API for this deterministic
matrix. This does not qualify enabled-normalizer DSP or general codec quality.

The first Vorbis playback captures every unchanged stock integer PCM byte,
requires SHA-256`e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910`,
and only then independently derives complete legacy mono goldens at volumes 1
and 254. The outer controller compares those full driver hashes before PASS.
No production gain/render helper or replacement decoder is used in the oracle.
Opus goldens use the earlier independently positioned complete stock integer
PCM. The separate reference checkpoints retain 56 full mono goldens and 7200
independently recomputed Decimal vectors; omitted PCM is not publicly replayed.

The chain contains nine gain-changing Opus/Vorbis links in one actual HTTP
session and generation, with no intermediate PCM EOF. Its unchanged source is
 19008000 bytes, SHA-256`32ed36a051afe232758c8e506dcfc622fb7228626ec99fc414419cd32ef4325f`.
The final mono output is 9504000 bytes,
SHA-256`0bdd2252ca92483e87e687547cedd3bb66ddc1efb64c26c1b7696ebe4e7fef19`. Genuine event ordering additionally proves
that a later-gain decoder opens while earlier source PCM is still queued for
the output owner. Per-packet metadata and all complete output link hashes hold
across that overlap. Bias/preload/ramp and final zero padding are separate from
logical mono bytes; no padding occurs between logical links.

All 38 public decoders and 30 SDK HTTP clients close. There are
11589 public process calls, 13 genuine growth errors and 13 real
next-call retries; the 120 ms output grows 12288 -> 23040 without replaying consumed
input. All 24 actual final PCM flushes occur at their real EOF. The public PDM
driver witness observes 30305 ordered gain stamps,
33515 writes, 32 preloads, and
4 created / 4 deleted channels.

The original task bindings and observed unused stack are:

| Owner | Core | Priority | Allocated | Observed unused |
| --- | ---: | ---: | ---: | ---: |
| Stream |0|3|6144|3800|
| Decode |1|5|16384|3808|
| Output |1|6|4096|1528|

Final free heap is 227132 bytes, minimum observed 51824, and
largest internal free block 110580. These are real global
observations under stated diagnostic seams, not production HTTP/TLS/TFT
headroom or physical PDM timing qualification. Assertions, canaries, light heap
poisoning, heap integrity and both idle watchdogs remain enabled. Compiler
closure binds 16 complete selected translation units
and 446 actual GCC/Ninja dependencies.

Every partial Stop has a genuine forwarded output-owner discard completion,
request/return timing and a unique sequence. All three owners/input become
quiet, no EOF is emitted, and source/driver counters remain unchanged for 25
real RTOS ticks before reopening. A discard's contemporaneous public generation
is recorded as an observation, never invented as an ACK or event parameter.
Thirty-one contradictory copies of the actual data are rejected. The separate
host metadata wrapper suite passes 136 cases under ASan/UBSan/leak checks.

The first three captures remain exact and non-PASS. Native01 failed sandbox
SDK activation with Windows DLL error 623 before SDK/QEMU. Native02 completed
one full gain case then timed out on a diagnostic Stop observer that assigned
discard a generation from separately published state; that label assumption
was invalid, but the specific timeout cause is unproven. Native03 completed
six lifecycle cases then reached its fixed 30 s first-Vorbis-capture EOF observer
deadline at 7591 stock records, with a live decoder and 5 ready / 1 reading input
slots. UART overhead is a hypothesis consistent with that progress, not an
independently measured root cause. Native04 fixes a 90 s first-capture EOF
observation deadline at wait entry; all other waits remain 30 s and the complete
QEMU bound 600 s. No deadline resets on progress or production edits are involved.

```text
python -B tests/results/cyd-ogg-gain-task-20261101/verify.py
```

The public archive includes exact sources, selected objects/config, original
statuses, dependency joins, runtime identities and genuine non-PCM observations
with original byte offsets/hashes. Full PCM/hex consoles, executable images and
publication-sensitive payloads stay whole/local with explicit size/hash/role
identities. The data-only verifier recounts published records and binds original
omitted identities; it does not read omitted bytes, reparse the complete original
raw console, regenerate full PCM hashes, run an SDK/emulator/decoder or execute
archived code. These publication limits do not replace the original complete
local gate and post-run independent oracle, both of which passed.

The images are diagnostic only and must not be flashed as production firmware.
Physical outputs, enabled normalizer, external network/TLS/TFT resources and
long production playback remain separate qualification tasks.
