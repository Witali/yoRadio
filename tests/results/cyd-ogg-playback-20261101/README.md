# Actual verified-page Ogg playback wrapper

The actual new application `ogg_playback.h` passes host lifecycle tests and
ESP-IDF 6.0.2 / dual-core LX6 QEMU with unchanged Espressif synthesis. Every page
is fully owned and CRC-verified before any bytes enter the vendor decoder.
Actual Opus playback emits the required 2112000 bytes for both complete fixtures,
while Vorbis retains its complete previous output. This is wrapper qualification;
the production audio-service task does not select it in these diagnostic builds.

| Actual native case | Result |
| --- | --- |
| Opus 20/Opus 120/Vorbis, whole/4096/257/one-byte feeds | All twelve complete runs preserve the original full raw vendor SHA; Opus playback matches the previously retained `[312,528312)` emission-window SHA, Vorbis matches its full original SHA |
| Both Opus fixtures with pre-skip 512 and positive 2^40 initial granule offset | Complete original coded payloads remain unchanged; raw hashes match originals and playback emits 2111200 bytes with a matching separately hashed raw window |
| Opus→Vorbis→Opus chain | Complete next BOS shares the original caller buffer with previous EOS; three actual public decoder drains/closes precede page ACK/reopen, with 6336000 ordered output bytes |
| Long Opus packets | Six real buffer errors report capacity 12288/needed 23040, consumed 0/decoded 0; actual wrapper realloc/retry succeeds |
| Invalid first audio-page CRC | The 54597-byte page is rejected; public process calls stay 2→2, with no audio output |

Native public-call observers forward identical arguments and results. They hash
raw returned PCM before the wrapper clips it, then independently hash actual
output callbacks. They inspect no decoder-private state. Original worker profile
is core 1/priority 3/stack 16384; assertions, stack canaries, heap poisoning and both
idle watchdogs stay enabled. This is not a replacement for the production
stream/decoder/output task profiles or complete radio/TLS/TFT resource margins.

The 108 actual-wrapper host cases pass GCC/ASan/UBSan/leak checks with explicit
public-API seams: retained prefixes; resize consumption 0/partial/full including
an empty nonterminal retry; page/pending/PCM allocation refusal and recovery;
invalid consumption/output sizes; sample-format failures; cancellation before
and after processing and at a real yield; callback failure; chaining and cleanup.
All owned allocations are released. The host seam does not execute Espressif.

Observed stable repeat-case free heap is 282952 bytes, minimum observed heap
104584 bytes, and unused worker stack 3276 bytes. The minimum includes the
CRC-mutation test's separate full-stream copy. These are diagnostic measurements;
actual audio-task and full radio application margins require their own gates.

## Original observations and publication boundaries

Native 01 and native 02 both finish the entire SDK/target gate with zero command
exits and unchanged bound source/artifact identities. Their codec/wrapper/harness
sources are identical. Between runs, only the new controller's runtime-path
serialization changes: the installed PowerShell path is replaced by a public
alias while exact binary hashes and local before/after checks remain active.
The original native 01 execution bundle contains a personal home path and stays
local as a whole, with an explicit hash/size/category omission record. It is not
rewritten or silently presented as the original public-safe native 02 bundle.

All executable/flash/boot/partition/compiler-probe images and flagged installed
headers stay local, with exact original identities and explicit omissions.
Published sources retain their original bytes and licenses. PCM payloads are
never captured or published by this diagnostic; only streaming measurements and
hashes are retained. No semantic scanner suppression or encoded image copy is
used. The archive deduplicates identical saved bytes under `blobs/<sha256>`.

The data-only verifier checks original command/child statuses, all published
bytes, omission identities and actual GCC translation-unit/dependency/object
joins. It also rejects twelve contradictory in-memory native transcripts.
It executes no archived code and does not claim to read omitted payload bytes.

```text
python -B tests/results/cyd-ogg-playback-20261101/verify.py
python -B tests/results/cyd-ogg-playback-20261101/verify.py --require-current
python -B tests/run-ogg-playback-host.py --output .build/ogg-playback-host-new
python -B tests/run-cyd-ogg-playback-qemu.py --output .build/cyd-ogg-playback-new
```

The default verifier checks frozen historical observations. The optional flag
also requires current sources to match final native 02. Production selection,
actual task lifecycle/backpressure qualification, nonzero output-gain behavior,
other packet modes/mappings, independent numerical conformance, complete
radio/TLS/TFT resources and physical acceptance remain separate requirements.
The complete raw/vendor emission-position comparisons here are regression and
sample-placement evidence, not a universal independent codec-quality oracle.
