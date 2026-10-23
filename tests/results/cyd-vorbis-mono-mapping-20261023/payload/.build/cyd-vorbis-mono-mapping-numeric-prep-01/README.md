# Complete mono21 numerical source preparation

No prepared adapter, metric, control, recorded-reference replay, decoder, SDK,
compiler, QEMU, Git or device operation was executed by this agent. Only source
assembly, text/JSON metadata reads, raw source/metadata hashes and AST checks were
performed. Neither actual target PCM nor recorded reference PCM was read here.

The strict criterion was chosen before target measurement and remains byte-pinned:
`policy21.py` SHA256
`219ec8d967e45536cbddf926e932e8647693d3e1320a75d562a1cd913e2e9119`.
Every original zero-lag signed-S16 sample must differ by at most2 LSB from each of
the two existing references. All21 cases/294 packets/464640 bytes and42 complete
target-reference comparisons are required. Real mono/stereo channels, all14 packet
boundaries including the empty primer, and every SS/SL/LS/LL channel output remain
complete. This is a deliberately strict finite project regression criterion,
not a normative Vorbis tolerance or broad conformance qualification.

`pcm_metrics.py` remains exactly the reviewed stereo module
`a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f`.
Stereo calls its original `compare` and `alignment` functions normally.
`mono_metrics.py` imports its generic `errors`/`need` normally and implements only
actual one-channel unpacking, full-packet comparison and diagnostic lag accounting.
No mono samples are duplicated, padded, trimmed, shifted, gained or resampled.
Mono13-frame inputs retain all13 samples, including a final unpaired stereo-sized
half-frame. Python integer error arithmetic retains the full65535 signed-S16
extreme; no16-bit error subtraction is used.

`test_mono_metrics.py` has29 pending host-only known-answer/control methods. These
cover little endian signed extrema, complete odd mono lengths and final-packet
errors,65535/squared-error/histogram answers, primer and packet accounting, wrong
channels and partial samples/lengths/padding, zero/max64 lag shapes and fixed
interior ranges, unchanged stereo module identity, and both-reference bound2/3,
missing cases/reference/channel/transition and geometry rejection. Diagnostic
alignment never changes the primary zero-lag result. No test pass is claimed here.

`capture21.py` requires independently reviewed CLI hashes for the actual target
report, actual direct terminal and actual runtime preparation. The now-available
actual metadata identities are also pinned explicitly in `pins.json`. There is
no invented future hash, fallback to an incomplete capture or relaxed gate.
Before PCM access it requires the complete checked-only target report and actual
direct-exec terminal0/controller identity. It verifies the reviewed phaseB source,
reconstructs the exact sealed controller bytes from its template and actual
runtime facts, verifies caller/protocol/setup/compile context and replays all654
protocol events. Every one of21 persisted PCM files must exactly equal the full
PCM_HEX stream with original packet offsets, channels and expected byte counts.

`compare_capture21.py` binds all21 original raw/header/frame descriptors to the
existing qualification `c31a87de…` and host `ab80560c…`. It checks every actual
child receipt/log, all42 recorded WAV/framemd5 streams, full decoded metadata and
the complete native/Xiph crosscheck using the unchanged recorded qualifier helper.
Both references then measure every target sample and packet separately. There
are no predeclared metamorphic groups in this matrix; none are invented here.
The historical dual-reference success applies only to this existing21 campaign.
All unrelated singleton8, floor0, wide/map2 numerical NONPASS evidence remains
outside replay scope and unchanged.

Root review/execution sequence (not performed here):

1. Review source/diffs/readiness and run the29 host-only metric/policy controls
   with an actual retained wrapper receipt.
2. Review the actual full21 capture/terminal/preparation metadata and then run:

```powershell
& $TaskPython -B -X utf8 .build/cyd-vorbis-mono-mapping-numeric-prep-01/compare_capture21.py `
  --repository . `
  --runtime .build/cyd-vorbis-mono-mapping-runtime-01 `
  --runtime-preparation-sha256 b94c9d6e0a2659e174bf9e8f2de422d9241b99e12297df9aab644fc244f7d5c4 `
  --target .build/cyd-vorbis-mono-mapping-capture-01 `
  --target-report-sha256 06bd8a60cef8d2f49bc4df839630a405e49823061be02f831d36ef5fd0655daf `
  --target-terminal .build/cyd-vorbis-mono-mapping-capture-01-terminal.json `
  --target-terminal-sha256 fa2bfd189ac1b20882c2c31d57ec1b0b866f2141db978cd08a6783bbdc2cec29 `
  --max-abs-error 2 `
  --output .build/cyd-vorbis-mono-mapping-numeric-measurement-01
```

All outputs are create-only in a fresh sibling directory. A completed comparison
that fails the fixed policy returns1 with full metrics retained. Bad or partial
inputs produce an incomplete rejection report; they cannot qualify the corpus.
No tolerance fitting, decoder backend attribution, production radio integration,
physical audio, full-G6/conformance or deferred Ogg/reset/EOF/OOM/AAC scope follows.

`SCHEMA.md` describes the complete measurement fields for standalone archive replay.
