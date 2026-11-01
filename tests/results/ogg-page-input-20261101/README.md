# Verified-page ownership and raw PCM clipping: host checkpoint

The new `ogg_page_input.h` owns one complete encoded page and exposes it only
after the timeline observer verifies its CRC and metadata. Its allocation grows
to the actual header/lacing/payload extent, bounded by **65307 bytes**. The caller
keeps the page pending until an explicit generation/token acknowledgement;
logical EOS must be fully drained/closed before that acknowledgement.

`opus_pcm_trim.h` derives byte spans from verified pre-skip/end bounds in raw
48 kHz frames per channel. It changes no samples and allocates no PCM. It rejects
unaligned formats, overflow, unexpected decoder totals and end bounds arriving
after their samples have already been emitted. It does not derive metadata or
establish the raw decoder's alignment by itself.

Neither helper is selected in production by this checkpoint. A public vendor
wrapper and full pipeline qualification remain in progress. The extra encoded
page heap, actual decoder ordering, independent PCM alignment and full-app
resources need target proof before integration is complete.

Two original GCC 13.3 host campaigns pass with ASan, UBSan, leak detection and
`-Werror`; their sources, commands, logs and terminal statuses are preserved.
Campaign 01 has 263 page cases. Campaign 02 adds multi-link Opus/bypass/Opus input
and OOM abandonment, giving **276 page cases, 204 PCM clipping cases and 12
recovered allocation refusals**. Every actual allocation ordinal is also tested
with immediate abandonment/reset, with no live allocation remaining.

Both complete 20/120 ms fixtures pass whole/4096/257/one-byte page ownership,
exact original page-byte comparison and immediate poisoning of consumed caller
storage. Tests cover delayed/stale/forged ACKs, same-generation reset, every
compact-stream truncation/reset position, CRC-invalid page rejection and the
maximum page extent. PCM geometry covers 1/2/8/255 channels, 8/16/24/32 bits,
pre-skip 0/1/312/65535, empty playable output, chunk partitions, late end bounds,
generation/format errors and checked 64-bit limits. These are ownership/span
tests, not a claim that Espressif synthesizes all those layouts.

The unchanged timeline suite also executes: 525 cases, 159 semantic negatives,
403 reset positions, ten real-fixture schedules and 219 public libopus duration
comparisons. Current nil-page repair is qualified separately in
[its differential checkpoint](../ogg-opus-nil-page-20261101/README.md).

```text
python -B tests/run-ogg-page-input-host.py --output .build/ogg-page-input-new
python -B tests/results/ogg-page-input-20261101/verify.py
```

The verifier executes no archived program. `captures.zip` deduplicates exact
original text/source/fixture bytes; `manifest.json` binds logical files to their
hashes/sizes. Both host executables remain local under ignored captures with
explicit original identities and omission provenance. Omitted bytes are not
read by this data-only verifier.

The design follows [Xiph's page-integrity-before-packet framing](https://xiph.org/ogg/doc/framing.html)
and [RFC 7845 pre-skip/end-trim units](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2).
