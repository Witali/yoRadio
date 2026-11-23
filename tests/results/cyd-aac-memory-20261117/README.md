# AAC startup memory and current task regression

The complete TLS HE-AAC fixture exposed a resource failure hidden by the
isolated public decoder check. The library fails a 55,128-byte allocation,
prints `Disable AAC-Plus for memory not enough` and continues at the 24 kHz
core rate. The full-rate controller rejects this result. The normal
AAC-LC control completes all 529,408 stereo frames with the
[exact direct-public reference](../cyd-aac-tls-reference-20261117/README.md)
and serves the exact WebUI asset after EOF.

Two bounded production changes reduce the AAC startup workspace:

- Public AAC starts with 8,192 PCM bytes, enough for the measured 2,048-frame
  stereo PCM16 output. The existing public `needed_size` growth path remains.
- Before publishing the first AAC payload, the producer lowers the leased
  input pool to its existing four-slot minimum. Idle excess slots are freed;
  busy slots keep their data and retire through the established API. The next
  generation restores the configured target as before.

The original stream/decode/output cores, priorities and stack sizes are
retained. No private decoder ABI, reset hook or codec arithmetic is changed.

## Complete current task regression

The current SDK/QEMU task campaign passes all 48 cases: six LC/HE/HEv2
fixtures, input splits, EOF, Stop/reopen, maintenance/resume and four genuine
continuous format observations. Complete PCM hashes and metadata retain
their original contracts. All 60 decoder handles and 60 HTTP clients close.
The compiler witness binds 17 actual translation units and 459 dependencies.
All bound inputs still match at completion. The observed heap minimum is
95,028 bytes; this isolated fixture uses synthetic transport/output and
20-second/1,000 ms watchdog diagnostics, rather than radio/TLS/TFT margins.

The first current run reached the real decoder but stopped on the old
test-only requirement for at least 12,288 initial bytes. It remains NONPASS.
The final fixture asserts exactly the selected 8,192 bytes. The complete
PCM oracle, owner checks and deadlines are retained. A separate data-only
witness rejects 41 contradictory transcript copies, including a wrong
initial capacity. The immutable November 1 archive still verifies its
original 48 cases, 60/60 cleanup and 40 original controls with the historical
12,288-byte contract. No archived code is executed.

The current PDM Clang profile completes all 53 project units, including both
HTTPD overlay units, with 100 warnings and zero errors. Every warning's
file/check/message/multiplicity matches the previous reviewed catalog.
This is one current profile; the previous six-profile production matrix
remains a separate checkpoint.

## Full-application resource controls remain nonpassing

| HE-AAC profile | Observation |
| --- | --- |
| Static TLS, 12 KiB PCM, eight input slots | SBR allocation fails; core-rate playback is rejected. |
| Dynamic TLS, original buffers | Same 55,128-byte refusal and core-rate output. |
| Static TLS with allocation probe | Before refusal: 62,884 free bytes, largest block 51,200. |
| Static TLS, 8 KiB PCM | SBR allocation succeeds; PDM later fails a 1,024-byte DMA allocation. |
| Static TLS, 8 KiB PCM, four slots | Full 48 kHz PCM reaches PDM, then OpenETH/WebUI runs out of usable blocks. |
| Dynamic TLS with both changes | Full-rate PCM begins; the stream ends with a read error after 96,256 frames. |
| Static TLS with both changes and TCP 8640/8 | SBR and PDM start, then OpenETH pressure and IDLE1 watchdog occur. The stack resolves to the simple-decoder parser and its free path. |

The matched allocation observations show the 55,128-byte request succeeding
with a largest block of 55,296 after reducing PCM, and 63,488 after both
changes. These are concurrent heap snapshots, not guaranteed savings or
atomic reservations. The diagnostics return genuine allocator results and
do not inject failures.

All full-application controls retain a five-second task watchdog,
300 ms interrupt watchdog and full 16,384/4,096-byte TLS record settings.
Original failures, UART, flash snapshots and reports remain local and
unchanged. No candidate is presented as successful full HE-AAC playback.
Normal production firmware has not been re-exported for this intermediate
change. Physical Wi-Fi and audio remain untested.

The next public-API check is complete ADTS frame input, to measure whether
the decoder can avoid a second input-assembly owner. Its resource benefit
and complete PCM identity are still unproven. Compact/private AAC remains
deferred. [All observed outcomes and identities](observed.json)

Follow-up, November 23: the [14-case public API comparison](../cyd-aac-public-input-memory-20261123/README.md)
now verifies complete-frame input, ordinary parsed output growth and matched
fragmented input. Complete PCM is preserved, but the matched HE frame-mode
saving is only 636 bytes. No production frame assembly was introduced and
the full-application HE resource gate remains NONPASS.
