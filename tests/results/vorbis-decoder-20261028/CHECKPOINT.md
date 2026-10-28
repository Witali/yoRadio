# Persistent public raw Vorbis decoder qualification

The [owner](../../../idf/components/native_vorbis_decoder/include/native_vorbis_decoder.h)
and [design](../../../docs/CYD_VORBIS_DECODER_DESIGN.md) add persistent
replace/measure/process/info/reset/clear above the already qualified public
packet/frame/floor/IMDCT/synthesis components. The batch fixture is not compiled
or linked into either native target. No private codec handle, new Ogg controller,
production registration or task/core/backend change is introduced.

Exact output capacity is checked before allocation/math. All channels finish
preparation before one synthesis commit; no fallible callback follows it.
Refusal preserves committed setup/history/timing/EOS and caller output/result,
while private scratch may change. Growth allocates before releasing old scratch.
Replacement publishes a separate successful candidate before old allocations
are released. No caller header/packet/allocator-descriptor borrow escapes.

## Complete PCM contract and host ownership

Host03 GCC13.3 ASan/UBSan executes all31 original streams,434 packets and738560
PCM bytes at zero lag. Maximum S16 error2 against both the original FFmpeg8.1.1
libvorbis bitexact references and saved Xiph output meets the unchanged bound2.
All14 relations pass. Complete PCM is byte-identical to the prior ordinary
pipeline and both native targets; SHA256 is
`b9df479b6cb6ac07b2aff2049f05bb8ba98ef9ce4fdc72acf40a333f47e01d75`.
Input retains7376 identification/setup/audio bytes and1798 comment bytes. Raw
configuration uses identification/setup only; container ordering/comments remain
an explicit separate responsibility. No saved gain/spectrum/IMDCT is decoder input.

The host derives refusal sweeps from every actual allocation ordinal of each
baseline:589 open,589 midstream replacement and302 initial/growing packet
scratch failures. All1480 recover with actual next-packet PCM equality.
The control capture preserves1515 events/4017 recovery spans/4035840 PCM bytes,
not just digests. Failed replacement also snapshots every old allocation payload;
callbacks observe publication/nulling without reentering any owner API.

All1212 bounded capacity controls,14187 read-only measures and265 other
refusals pass, including null/truncated metadata, reset, independent owners,
cross-stream replacement, discontinuity and HTTP-EOF separation. Caller headers,
allocator descriptor and completed packet storage are poisoned/freed. All13
retained floor0 supplements keep typed numerical outcomes; failed EOS requests
leave history/position/terminal state unchanged and recover through valid packets.
Eight damaged captures are rejected. Final guard count17082734 includes the
15 assertions after the binary summary's17082719 snapshot. All owned children
are terminal/reaped/groups gone; sanitizer stderr is empty.

A separately model-validated uncoupled255-channel/8192 absent-floor stream
tests real legal dimensions. A1MiB supplied allocator refuses the8355840-byte
history request with complete cleanup and NO_MEMORY, without adding a format
cap. A64MiB host budget permits1044480 actual zero S16 samples, reset and clear;
its peak tracked owner payload is25345820 bytes. This does not claim MCU fit.

## Actual native execution

SDK6.0.2/LX6 and SDK6.1.0/RV32IMC execute the persistent public API directly in
QEMU. Each directly compares every PCM sample against both saved references,
with maximum2/all14 relations. Read-only byte checking also confirms every
packet/per-case/aggregate output equals host and the other ISA. Literal
`transport.json`/C arrays preserve the existing raw fixture's granules, octet
extents, EOS and gap flags. They are fixture metadata, not recovered Ogg pages
or EOS inferred by the target from HTTP/array order.

Each target retains4536 strictly parsed protocol lines,434 resource/capacity
refusals,62 terminal-EOS refusals,31 no-allocation resets,62 warm retries and31
balanced clears. The zero-output primer cannot be undersized: its refusal tests
the addressability RANGE check with SIZE_MAX; nonzero packets use required-1.
Warm output is compared by full C memcmp with the captured original packets;
its supplementary FNV is bound to those actual primary bytes, not claimed as
retransmission of the warm PCM. Twenty-four malformed transcripts are rejected.

Before the full corpus, actual native malloc refuses the legal8355840-byte
history request: seven attempts/six successful allocations/six releases leave
zero live owner payload; the subsequent complete corpus proves recovery.
The resource recipe retains exact233-bit ID/404-bit setup/builder provenance.
No allocator budget is used for this MCU failure.

The coordinator stays on core0; priority3/16384-byte worker runs on ESP32/core1
or C3/core0. Watchdogs and both applicable idle checks remain enabled. Native
owner peak payload125642 bytes is separate from8192 caller PCM bytes and
32/48 bytes of tracking overhead per allocation. Minimum free worker stack is
10348/10600 bytes; cumulative emulator heap minima150552/186820 bytes and
minimum post-cleanup heap292800/329324 bytes are distinct observations. These
exclude production radio/TLS/TFT allocations, physical timing and transient
total-heap peak claims. Six command receipts and the SDK child terminate0;
all22 own compile rows/ELF32 objects, flags, stack records, images, ELF/map,
configuration, UART and per-case PCM remain bound to their source bytes.

## Source analysis and preserved history

Source-only GCC15.2 C/C++ profiles pass seven commands/four ELF32 objects across
LX6/RV32IMC. Own process624/576-byte and measure240/224-byte frames exclude
callees/whole-task high-water. Owner Clang retains two reviewed standard-C
void-pointer workspace-array conversions and zero errors. Fixture lint retains
seven warnings: five deliberate unchanged-object byte snapshots, one analyzer
path losing `buffer(bytes).bytes==bytes` at a guarded zero-byte NULL input,
and one bounded2*opening-count widening (actual count19). No suppression or
weaker configuration is added; the diagnosed NULL copy path cannot occur.

Pure preflight01 retains all input/typed/resource data without C execution.
Host01 stops at sandbox WSL activation; host02 stops at strict fixture
misleading-indentation compilation. Only a serialization-loop newline changes
before passing host03; production source and input bytes stay unchanged.
Both native01 attempts stop at installed SDK activation before compiler-child
dispatch/QEMU; unchanged native02 passes after ordinary runtime execution.
Protocol24 is separately preserved. No prior deferred controller is resumed.

## Archive and remaining work

`captures.zip` SHA256:
`c01692d4e32e7f477cec7e6b650e4b184c64045ba2573926554af5f0eae15517`.
ZIP bytes8233329. `manifest.json` SHA256:
`9388aa1cd6c9dab21cd9ebd41fddfb46636c229aa1901270bcc4378b57f6cf67`.
All1359 logical files/76529126 logical bytes use326 shared physical SHA256
blobs/58141929 decoded bytes. Explicit identities account for1809 omitted
rebuildable executable/SDK-scratch files/158778501 bytes. Every reported output
is retained or bound to an omission; diagnostic images are not production builds.
The host and native final seals and their scripts remain in receipts/tools.

The [pure public verifier](../../verify-vorbis-decoder-checkpoint.py) checks
physical/logical bytes, all attempts, source/receipts/builds, complete PCM and
actual recovery data through pinned live readers. It extracts/executes no
archived code and starts no C/compiler/SDK/QEMU processes. `replay.json` records
that campaign; `verification.json` separately binds final artifacts/receipts
without a repeated numerical campaign.

Two initial pure-reader attempts are preserved alongside the archive as exact
reader snapshots, terminal logs and failure receipts. The first mismatched
Python tuple rows with JSON lists; the second compared a62-file extension filter
with the native seal's66 non-Markdown artifacts. The final reader preserves
every allocator value/row while normalizing its JSON representation, strengthens
live checking to include three COPYING files plus partitions.csv, and explicitly
maps the seal's c3 label to the SDK's esp32c3 target. No target/ELF/config check
is relaxed. C, SDK and QEMU are not repeated for these reader-only repairs.

This qualifies persistent raw ownership/lifetime and the complete finite PCM
contract. [Certified general gain and wider synthesis/history](../../../docs/CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md),
Ogg/container metadata handoff, actual audio-task integration, full production
resource/performance and physical acceptance remain required. Basic production
Ogg/Vorbis already works; this candidate remains unselected. The full transfer
objective and all old deferred records remain open where explicitly recorded.
