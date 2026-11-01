# Public Opus packet-mode and raw-frame observations, 2026-11-01

All 49 complete creator streams were accepted by the stock public Espressif
Ogg decoder and the unchanged playback wrapper, whole and in 257-byte feeds:
196 complete native cases, no reported refusals, no geometry gaps. All 196 raw
outputs match each fixture's stock-whole output exactly; all 98 wrapper outputs
match the independently selected stock PCM playback window exactly. Twenty
genuine buffer retries include 12,288 to 23,040 bytes for 120 ms stereo packets.
This is framing, lifecycle and output-geometry evidence. **Full standard numeric
qualification remains false. No new tolerance or production workaround is used.**

The bounded corpus covers SILK wideband 10/20/40/60 ms, hybrid superwideband
10/20 ms and CELT fullband 2.5/5/10/20 ms frames. Representative streams exercise
packet codes 0–3, CBR/VBR, maximum 120 ms, 48-frame CELT packets, multioctet padding
lengths and 255 trailing padding bytes. Twenty-one cases include legal absent
coded frames after real warm-up packets. The final creator source also encodes
a full silent quarter, distinct from absent-frame PLC. Empty Opus packets are
refused by separate parser-only negative tests. Bandwidth transitions, all other
bandwidth/channel combinations, FEC and official conformance vectors are not
exhaustively covered.

Every original complete encoder packet is retained. RFC framing copies whole
coded frames, with explicit source maps recording repetition/reordering and
absence. Public libopus 1.4 independently parses and synthesizes every packet,
repacketizes and pads/unpads it, and performs three complete integer decodes
that must match. Public libogg reconstructs every complete encoded body at
whole/257/1-byte input splits, checking actual CRCs, packet numbers, BOS/EOS and
granules. The final 49 streams contain 514,080 raw frames and 501,419 playback
frames; 84 coded frames are genuinely absent. The three creator captures
remain byte-identical, including the first two before the explicit silent tail.

The numeric observations deliberately separate these classes:

| Input class | Streams | Largest observed raw difference | Clipping |
| --- | ---: | ---: | --- |
| Unaltered consecutive, fully coded | 18 | 34 S16 LSB; maximum per-stream RMS 2.499 | None on either side |
| Repeated/reordered, fully coded | 10 | 65,535 LSB | Both creator and native can clip heavily |
| Explicit absent coded-frame/PLC variants | 21 | 65,535 LSB | Assessed separately from normal coded synthesis |

These numbers are measurements, not acceptance limits. SILK observations are
byte-identical throughout this corpus. Hybrid and CELT include implementation
differences. The two fully coded large-error cases repeat a complete CELT
2.5 ms coded frame 48 times per 120 ms packet to force equal-length CBR framing.
For these cases the entire first packet differs by at most 1 LSB. The first
difference above 1 occurs at global elementary frame 50; frame 51 is the first
large difference and also the first time both decoders clip. The independent
creator float output subsequently reaches a peak of 1,105,064.25 in normalized
float units. This constructed repeated-frame stream is distinct from the
original unmodified encoder progression. All 49 first-packet prefixes select
zero lag and unchanged channel order in the explicitly bounded [-8,+8]-frame
alignment search; full per-packet/per-frame measurements are preserved.

A new public-only creator control splits exactly the same coded frames into
code 0 packets and decodes them serially through persistent opaque handles.
Aggregate and elementary **float** output are byte-identical. On the clipped
repeated-frame cases creator **integer** output itself depends on cadence:
63 scalar samples differ, with a maximum 6,820 LSB. Public soft-clipping and
explicit hard-conversion observations are retained separately; elementary
integer output is not promoted to an exact arbitrary-input oracle.

A separate 24-case native control compares stock Ogg with persistent public raw
Opus handles, identical aggregated/code 0 bytes, documented matching 2.5/120 ms
durations, separately labeled `INVALID` output sizing and presized/retry output
buffers. Every native result is byte-identical to stock Ogg and its own
presized raw aggregate, with zero refusals/geometry gaps and three real retries.
No empty raw packet or PLC recovery request is inserted. These controls do not
implicate the tested Ogg parser, wrapper, multiframe grouping or retry path as
the source of the creator difference. No private state/layout or codec math is
inspected or replaced, and no production change follows from these observations.

The original raw-control report retains an unused three-fixture catalog inherited
from its command/closure helper. Its actual four inputs are authenticated by the
encoded table, source manifest and all 24 case records. The terminal report is
not rewritten. A subsequent controller-only metadata correction records the
four real control fixtures for future runs; constructor/preflight checks cover
that correction, and no new MCU execution is claimed for it.

RFC 6716 section 6 defines formal conformance using the official test-vector
procedure, final ranges and `opus_compare`; an arbitrary max-LSB rule does not
replace it. Those official tests were not performed through the Espressif public
surface here. See [RFC 6716 section 6](https://www.rfc-editor.org/rfc/rfc6716.html#section-6),
the creator's [test-vector guidance](https://opus-codec.org/testvectors/), and
the documented [public decoder APIs](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html).

The mode diagnostic uses classic ESP32/LX6, SDK 6.0.2, dual cores, a core 1
priority 3 worker with a 16,384-byte stack, assertions, heap poisoning, stack canaries
and both idle watchdogs. Each native target has five actual compiler translation
units with the recorded dependency closure. No full audio_service task pipeline,
physical output, radio timing or universal codec conformance is claimed. The
first mode-native attempt is preserved as a terminal activation-only failure:
un-escalated Windows execution returned DLL error 623 before any SDK child or
QEMU existed. Unchanged sources then passed through normal reviewed escalation.

`captures.zip` preserves original reports, logs, source snapshots, synthetic
encoded packets/streams and numeric observations. Compiled binaries, decoded
integer/float PCM, complete UART logs containing PCM and whole raw-scan-flagged
payloads remain local; exact omissions are listed by identity and size. No
flagged bytes are redacted in place or declared safe by a semantic override.

Run `python tests/results/opus-packet-modes-20261101/verify.py` for frozen
data-only authentication and contradiction controls. `--require-current` also
checks the current canonical source bindings. Historical verification does not
require evolving production files to remain equal to these original snapshots.
