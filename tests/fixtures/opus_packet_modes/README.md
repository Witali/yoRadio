# Complete public Opus packet-mode corpus

This separate corpus prepares 49 short, complete Ogg Opus streams from locally
synthesized tones followed by a full encoded silent quarter using the installed
creator libopus public encoder. Real silence is distinct from absent-frame PLC.
The corpus does
not modify production sources or the previous gain/family1 checkpoints.

The ten base profiles cover the legal per-frame duration choices:

| Measured mode | Selected bandwidth | Frame durations |
| --- | --- | --- |
| SILK | Wideband | 10, 20, 40, 60 ms |
| Hybrid | Superwideband | 10, 20 ms |
| CELT | Fullband | 2.5, 5, 10, 20 ms |

TOCs are observed and checked after encoding. Only public application, bitrate,
VBR, bandwidth, voice-signal and lookahead controls are used; no private
force-mode control or structure layout is involved.

Each base profile has a code0 stream. Three representative profiles additionally
exercise codes1/2 and code3 CBR/VBR, maximum 120 ms packets, and 255 trailing
padding bytes requiring multiple padding-length octets. CELT 2.5 ms reaches the
48-frame packet boundary. Twenty-one streams include zero-length coded frames:
all-zero payload frames under codes0–3, mixed absent/present code2 frames and a
code3 missing frame between real coded frames. Real packets warm up the decoder
first. A one-byte TOC-only packet is distinct from an invalid empty Opus packet.

The original complete encoder packets remain in `original.packets`. The RFC
writer only copies complete coded frames and records their source map. CBR
aggregate cases intentionally repeat an intact coded frame, because fixed-rate
SILK output may use Opus packet padding while its actual coded-frame sizes vary.
VBR cases require observed unequal coded lengths. Missing frames are explicitly
mapped to absence, never fabricated entropy-coded bytes. These constructed
streams have their own independently decoded references; they do not claim to
reproduce the original encoder input waveform.

Every resulting stream has complete OpusHead/OpusTags headers, four audio
packets, real BOS/EOS, consecutive CRC-valid pages, measured encoder pre-skip
and an explicit 13-frame terminal trim. Public creator APIs independently check
all packet frame boundaries and durations, repacketize and pad/unpad each full
packet, and perform three complete integer decodes that must match exactly.
Public libogg reconstructs the exact framed packets using whole, 257-byte and
single-byte feeds. Full raw and windowed PCM stay in the fresh local capture.

Run the creator qualification:

```text
python -B tests/run-opus-packet-modes-reference.py --output .build/opus-packet-modes-reference-<fresh>
```

The runner freezes source bytes, records actual subprocess arguments, PIDs,
terminal statuses and both output streams, binds the installed compiler and
creator libraries before/after execution, and preserves failed captures.
The host harnesses use ASan/UBSan with leak detection; installed libopus/libogg
binaries themselves are not sanitizer-instrumented. Parser-only negative and
boundary tests run separately and are not reported as synthesis coverage.

The same report audits the complete framing of 26 existing local Opus fixtures.
Those inventory entries are metadata observations. The previous CYD Ogg
playback campaigns synthesize the CELT 20/120 ms fixtures; the previous all-TOC
duration matrix does not establish SILK/hybrid synthesis coverage.

The new native diagnostic is prepared separately:

```text
python -B tests/run-cyd-opus-packet-modes-qemu.py --reference .build/opus-packet-modes-reference-<capture> --output .build/cyd-opus-packet-modes-<fresh> --preflight-only
```

Its 196 planned cases feed every complete stream to the stock public Espressif
Ogg decoder first and the current wrapper separately, whole and in 257-byte
chunks. Actual public statuses, consumption, capacities, full EOS draining and
complete PCM are retained. Numeric differences from creator output are measured
without inventing a conformance tolerance. SDK compilation/execution requires
the coordinating agent's free build slot. Preflight alone executes no target.

This is bounded coverage: the selected bandwidths, channel layouts and packet
forms do not exhaust every valid Opus bitstream, bandwidth transition, in-band
FEC, multistream mapping or codec conformance vector. See
[RFC 6716 section 3](https://www.rfc-editor.org/rfc/rfc6716.html#section-3),
[RFC 7845 section 4](https://www.rfc-editor.org/rfc/rfc7845.html#section-4), and
the creator's [public repacketizer API](https://opus-codec.org/docs/opus_api-1.5/group__opus__repacketizer.html).
