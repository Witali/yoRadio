# Bounded Ogg/Opus timeline observer: host checkpoint

The new application-owned metadata observer in
[`ogg_opus_timeline.h`](../../../idf/components/native_stream/include/ogg_opus_timeline.h)
passes the saved native host campaign **03** with GCC 13.3.0, ASan, UBSan and
leak detection. Its state occupies **512 bytes** on this x86-64 host. The
production audio service does not use it yet; it neither synthesizes PCM nor
implements pre-skip/end trimming. Espressif decoding remains unchanged.

The observer consumes each original encoded byte once, retaining a fixed page
header/lacing table and at most 19 identification bytes or two audio TOC bytes.
It retains no input pointers, encoded packet bodies or PCM. All timing counts
48 kHz frames per channel, with checked 64-bit arithmetic. Reset preserves the
monotonic event token even when a caller reuses the same generation.

## Actual qualification

The compiler runs with `-Werror`, `-fsanitize=address,undefined` and frame
pointers. The process runs with `detect_leaks=1` and both sanitizer halt options.
All native command exits are zero; test stderr is empty.

| Test group | Actual result |
| --- | --- |
| Synthetic cases | 525, including 159 negative duration/container/header cases |
| Reset positions | 403 distinct prefixes, covering partial headers, lacing, payload and continuation states |
| Real 20 ms fixture | 706319 bytes, 15 pages, 528960 raw frames, pre-skip 312, raw end 528312 |
| Real 120 ms fixture | 707097 bytes, 14 pages, 529920 raw frames, pre-skip 312, raw end 528312 |
| Byte partitions | Whole, 4096, 257, one byte and seeded partitions for each complete fixture; identical event digest for every partition |
| Independent duration reference | 219 successful duration comparisons to installed **libopus 1.4**, using its public `opus_packet_get_nb_samples` API without audio synthesis |

Synthetic streams have independently constructed page CRCs. Coverage includes
all 32 TOC configurations, packet codes 0–3, 120 ms duration, zero-length coded
PLC frames, invalid count/duration combinations, packet continuation, the zero
lace after an exact multiple of 255 bytes, and a 70000-byte streamed comment
packet. Timeline cases include positive 64-bit initial offsets, first-audio-page
EOS, pre-skip 0/1/312/65535, empty playable output, unknown granules, nil pages,
and end trimming longer than one packet. The latter remains accepted because
RFC 7845 specifies a SHOULD bound, rather than MUST.

Known mapping families 0, 1, 2, 3 and 255 are exercised, including the family 3
matrix extent, a self-delimited first multistream packet, compatible header
version 15, and Opus-to-non-Opus-to-Opus sequential chaining. This is metadata
coverage, not evidence of synthesis/downmixing support for those mappings in
Espressif's decoder. Delayed event acknowledgement, forged/stale tokens,
same-generation reset, borrowed-input poisoning, every compact-stream
truncation and checked counter/token limits are tested.

Campaign **01** remains a nonpassing, pre-compilation record: sandboxed WSL
returned `E_ACCESSDENIED`. A separately authorized local WSL run, **02**, then
passed before the independent reference comparison was added. Campaign **03**
recompiled the updated frozen sources and passed all tests plus the libopus
comparisons. Neither earlier report, source snapshot nor native log was changed.

## Contract and limits

`oopt_feed` stops at one pending event and reports the number of original input
bytes consumed. The caller must acknowledge the event's generation and token
before feeding the suffix. An acknowledged link-end event only releases this
observer's old metadata; the caller remains responsible for draining/reopening
the actual decoder and output owners in order.

An EOS header can yield **PROVISIONAL_END before the complete page is read**.
It is explicitly not CRC-verified. Only a subsequent PAGE event authenticates
the entire page's CRC and validates its timeline; any later error invalidates
the provisional metadata. This API does not establish that a production caller
can safely emit or trim PCM before the verified event. Required buffering and
vendor input/output ordering are still unqualified.

This is a sequential-link timing observer, not a complete Ogg/Opus validator:

- Concurrent logical serials and unknown mapping families return UNSUPPORTED.
  For unknown mappings, RFC 8486 does not permit assuming the normal table or
  packet layout. The first implementation does not synthesize an alternative.
- Sequence gaps, missing packet prefixes and unknown completed-audio granules
  return UNALIGNED. Resynchronization, seeking and concealment are separate work.
- Compressed frame extents, all self-delimited stream bodies, comment contents,
  output gain, sample-rate conversion and historical serial uniqueness across
  unbounded chains are not validated here. Decoder validation remains required.
- No exhaustive mapping matrix, differential container corpus, target ABI/stack
  measurement, production integration, actual PCM alignment or physical audio
  qualification is claimed by this checkpoint.

## Reproduce or verify

Run the native suite with an unused ignored capture directory. On Windows the
runner invokes the installed WSL GCC and libopus; it downloads nothing.

```text
python -B tests/run-ogg-opus-timeline-host.py --output .build/ogg-opus-timeline-host-new
```

Verify the saved checkpoint without executing a compiler, decoder, emulator or
any archived code:

```text
python -B tests/results/ogg-opus-timeline-20261101/verify.py
```

`captures.zip` deduplicates identical saved bytes under `blobs/<sha256>`;
`manifest.json` binds every logical path, hash and byte count. Both successful
native executables stay local in ignored captures; only their exact identities,
sizes, roles and local retention provenance are published. The verifier checks
published reports/logs/source bindings and executable omission identities; it
does not claim to inspect omitted executable bytes. Real fixture bytes are
retained as data, not replaced with shortened streams. No archived code is run.

The installed compiler executable SHA-256 is
`1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26`.
The installed libopus executable-library SHA-256 is
`63ddaf057d71c53090607e0467eb308640c3b39b0f189e5b937e9c397be2f676`,
rechecked unchanged after the run. These are local tool identities, not bundled
tool binaries or a claim that the system library itself was sanitizer-built.

Implementation review follows the original
[Ogg page specification](https://www.rfc-editor.org/rfc/rfc3533.html#section-6),
[Ogg Opus packet organization and timeline rules](https://www.rfc-editor.org/rfc/rfc7845.html#section-3),
[Opus TOC framing](https://www.rfc-editor.org/rfc/rfc6716.html#section-3),
[mapping-family updates](https://www.rfc-editor.org/rfc/rfc8486.html#section-5)
and the creator's
[public packet-duration API](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html).
