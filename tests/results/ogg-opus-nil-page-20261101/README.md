# Nil-page continuation: public libogg differential checkpoint

The bounded Ogg/Opus timeline observer now preserves an unfinished packet across
a nil page regardless of that page's continuation bit. A page with zero segments
has no first packet segment for the bit to describe. Sequence and CRC checks
still apply to every page. Pages containing segments retain the original strict
continuation check. No decoder, production integration or playback trim is added.

The actual baseline run proves the previous problem: the public installed
libogg reconstructs every expected packet byte without a hole, while the old
observer rejects 60 valid-input split schedules. Five additional mismatches
classify a corrupted nil page as unaligned before reaching its CRC. The focused
fix checks the continuation bit only when the page has at least one segment.

The reference follows the creator's public `ogg_sync_pageout`,
`ogg_stream_pagein` and `ogg_stream_packetout` APIs. CRC-invalid pages pass
through the real sync/CRC checker; packet comparison checks every reconstructed
payload byte. No private structure member is inspected or changed. The public
libogg header declarations already vendored in this repository are used with
the installed ABI-compatible library; their complete source and BSD license are
preserved. The historical custom Vorbis implementation is not run or modified.

| Actual coverage | Result |
| --- | --- |
| Valid nil-page layouts | 24: before an open packet, between its 255-byte continued pieces, and after completion; continuation bit 0/1; one/two nil pages; zero-length terminating lace or seven-byte tail |
| Split schedules | Whole, one byte, 27, 257 and seeded partitions; all 120 valid schedules agree with libogg after the fix |
| Negative controls | Sequence gap and corrupted CRC, each with both nil-page continuation bits; all 20 schedules reject and libogg records loss of the incomplete packet |
| Memory/lifetime | GCC `-Werror`, ASan, UBSan and leak detection pass; consumed input is poisoned immediately; observer state remains 512 bytes on the host |
| Full previous regression | The unchanged original timeline suite passes 525 cases, 159 semantic negatives, 403 reset positions, ten full real-fixture schedules and 219 libopus duration comparisons against the fixed observer |

These are container/metadata tests. Synthetic audio packets have a timing TOC
but are not passed to an audio decoder. libogg is a framing reference, not a
complete validator of every Opus mapping rule. Both system libraries remain
unchanged local binaries; they are not claimed to be sanitizer-built. Actual
versions, exact executable-library hashes, compiler identities and all commands
are in the preserved original reports.

## Original run history

1. `baseline01`: all native commands run; the native test exits 1 with 65
   measured mismatches. Its report stays NONPASS and its old observer snapshot
   stays unchanged.
2. `reader-failure02`: native test exits 0 and all 140 schedules pass after the
   header fix. The outer Python controller then raises a duplicate-keyword
   `TypeError` while printing its summary. Its original `state=nonpass` and
   exception remain, alongside a contradictory `passed=true` written before
   the exception. This inconsistent failed-reader record is explicitly checked
   as historical data and is not accepted as the passing checkpoint.
3. `authoritative03`: only the controller's summary-print expression changes;
   fresh native compilation and all commands/tests finish with exit 0.
4. `regression04`: the unchanged previous timeline host runner/harness executes
   with the fixed observer and passes the complete original suite.
5. `authoritative05`: failure handling now also clears the outer `passed` flag
   on any exception. Fresh compilation and all native commands/tests pass.
   This is the final canonical passing nil-page campaign.

Original logs, reports, source snapshots and failed outcomes are not rewritten.
`captures.zip` stores identical bytes once under `blobs/<sha256>` and
`manifest.json` maps each logical file to its exact bytes. All five host ELF
executables remain local in ignored captures; only their exact hash, size,
role and local-retention provenance are included. The data-only verifier never
executes archived code and does not claim to read omitted executable bytes.

```text
python -B tests/results/ogg-opus-nil-page-20261101/verify.py
python -B tests/results/ogg-opus-nil-page-20261101/verify.py --require-current
python -B tests/run-ogg-opus-nil-page-host.py --output .build/ogg-opus-nil-page-host-new
```

The default verifier checks historical frozen evidence so later legitimate
source evolution does not invalidate the original observation. The optional
flag additionally requires today's canonical sources to match campaign05.

Primary references: [RFC 3533 nil pages](https://www.rfc-editor.org/rfc/rfc3533.html#section-4),
[RFC 7845 packet continuation](https://www.rfc-editor.org/rfc/rfc7845.html#section-3),
[Xiph framing and zero-lace continuation](https://xiph.org/ogg/doc/framing.html),
and [libogg page/packet implementation](https://github.com/xiph/ogg/blob/master/src/framing.c).
