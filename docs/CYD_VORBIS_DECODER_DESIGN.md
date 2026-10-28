# Persistent owned raw-packet decoder

The [public interface](../idf/components/native_vorbis_decoder/include/native_vorbis_decoder.h)
provides the persistent lifetime missing between the qualified packet-to-PCM
pipeline and a production adapter. It reuses existing setup, frame, floor,
IMDCT, exact-window, PCM and shared synthesis components. The frozen batch test
pipeline remains an independent diagnostic; its stack-local allocator context,
free-before-grow scratch and post-publication callbacks are not a reusable
streaming decoder contract.

## Packet and timing boundary

Identification/setup bytes configure one exclusively owned handle. The transport
validates the ordered three headers and container framing. The raw public
Espressif2.6.2 `esp_vorbis_dec_cfg_t` likewise takes identification/setup only;
its comment header is not passed to the frame decoder. This does not remove
the comment header requirement from a complete Vorbis stream.

Each raw packet supplies immutable bytes, explicit bit extent, signed64 granule
position, EOS and discontinuity. Its block size comes from the packet prefix.
The existing integer timing model previews the exact S16 output span. It is
not correct to derive EOS from a caller array index, HTTP EOF or an empty drain
call. There is no artificial terminal block. Successful EOS makes the raw link
terminal until explicit hard reset or setup replacement.

The actual SDK raw input structure carries bytes/consumption/recovery but no
granule/EOS fields. Therefore registering an operation table alone cannot supply
the required exact trimming. A later transport/container adapter must preserve
those fields before audio-task integration. CYD currently passes arbitrary
network chunks to its Ogg simple decoder. This component neither changes that
registration nor implements an alternate Ogg controller.

## Failure and ownership contract

Read-only `measure` checks prefix and timing without allocation. It publishes
required interleaved S16 element capacity separately from `process` results.
It does not pretend to validate the rest of the audio packet.

`process` performs that exact output preflight before memory growth or math.
It then decodes into private scratch, prepares every channel's transform and
calls the qualified multi-channel synthesis owner once. All possible errors
precede history/timing/output/result publication. No callback follows commit.
Setup, committed history/position/EOS and caller output/result survive failures;
scratch may change and its borrows never escape. An unchanged packet can be
retried after resource recovery. Dynamic growth allocates a replacement before
releasing its old scratch; allocation refusal cannot destroy reusable storage.

Replacement builds a completely separate owner before publishing it. Its saved
allocator/context remains valid for the entire handle lifetime. Failed replace
preserves the previous live handle and successful replace releases it only after
publication. Hard reset retains setup/lookups/scratch, clears EOS and primes
again without reading old half-history. Clear nulls the caller handle before
releasing all owned allocations. Callers serialize use; no lock/task is added.

## Numerical and resource scope

This component implements persistent lifetime and transactional packet delivery;
it does not resolve incomplete floor0 wider/precision/undefined domains by
changing packet acceptance or switching a single packet to another backend.
Those outcomes remain typed and leave committed state unchanged. Production
selection awaits complete numerical, container, audio-task and resource gates.
The [remaining certified-gain design](CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md)
records a legal finite case whose linear exponent needs at least1572 bits;
changing only the fixed exponent width cannot qualify that domain.

Storage requests use actual setup/block/channel requirements with checked byte
arithmetic. Allocation failure is resource exhaustion, not a new encoded format
limit. A successful isolated stereo2048 corpus does not prove that8192/255 or
the full radio/TLS/TFT environment fits either MCU. CYD stream core0 and
decode/output core1, C3 core0, task priorities/stacks, all audio backends and
board/display configuration retain their existing implementations.

Creator references are [Vorbis I](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
sections1.3,4.3 and appendixA, the pinned Xiph1.3.7 public raw packet API, and
the installed Espressif public headers `esp_audio_dec.h`, `esp_audio_dec_reg.h`
and `esp_vorbis_dec.h`. Qualification must retain all31 original streams,
434 packets,738560 PCM bytes, both references, bound2 and all14 relations,
plus allocation/capacity/retry/reset/EOF/lifetime controls. The old private
bridge and deferred Ogg/DSP/packet/AAC scopes remain unchanged.

## Observed qualification

The [checkpoint](../tests/results/vorbis-decoder-20261028/CHECKPOINT.md) preserves
complete host ASan/UBSan and actual ESP32/C3 SDK/QEMU execution of this owner.
Every original31/434/738560 PCM byte meets the unchanged bound2 against both
references and all14 relations. Actual host and both native outputs match
byte-for-byte, including the previously qualified ordinary pipeline output.

Host exercises every observed allocation ordinal for589 opens,589 midstream
replacements and302 initial/growing packet scratch requests. All1480 refusals
recover with actual PCM equality;4017 recovery spans/4035840 PCM bytes remain
in the capture. It also checks1212 bounded output-capacity refusals,14187
read-only measures, reset, independent handles, gaps, header/packet lifetime,
HTTP EOF separation and all13 retained numerical-route vectors. A legal
255-channel/8192 absent-floor stream produces1044480 zero S16 samples with a
larger supplied host allocator; a1MiB budget refuses the8355840-byte history
request and releases all candidate allocations. This is a resource test, not
a new format cap. Actual peak owner payload there is25345820 bytes on host.

Both native workers retain16384 stack bytes and enabled watchdog/idle checks,
running on ESP32/core1 and C3/core0. Each performs434 capacity/resource refusals,
62 terminal-EOS refusals,31 no-allocation resets,62 warm packet retries and31
balanced clears. Real malloc refuses the same8355840-byte large history request:
seven attempts, six successful allocations and six releases leave no live owner
payload, followed by full original-corpus recovery. Native peak owner payload
for the ordinary corpus is125642 bytes; the caller's two PCM test buffers have
a separate8192-byte peak. Minimum free worker stack is10348/10600 bytes and
cumulative emulator heap minima are150552/186820. These observations exclude
the production radio/TLS/TFT environment and physical real-time performance.

Source-only C/C++ profiles pass LX6/RV32IMC. Own process frames624/576 bytes
exclude callees and whole-task high-water. Clang retains two reviewed ordinary
C void-pointer workspace-array conversions; fixture lint has seven reviewed
warnings and zero errors, with no suppression/configuration changes. The owner
is still unselected by the radio: certified general gain/wider history,
container metadata handoff, actual audio-task resources and physical acceptance
remain separate required work.
