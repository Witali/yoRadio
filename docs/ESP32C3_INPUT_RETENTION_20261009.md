# ESP32-C3 input queue retention and contiguous heap recovery

The queue now retains its earliest resident packet buffers when an ordinary
Stop, EOF or station change reduces its limit. Busy excess buffers retire on
consumer return. Actual TLS allocation pressure can still reclaim idle
buffers above the minimum count. The optional FLAC expansion remains
disabled by default; this correction does not qualify it for production.

This follows the [matched capacity comparison](ESP32C3_SWITCH_CAPACITY_CONTROL_20261009.md).
That comparison found contiguous-heap loss with additional FLAC input slots,
without a comparable loss of total free memory. Its original failures,
including the unresolved WebUI timeout, remain unchanged.

## Finding and implementation

The existing heap-owner probe watched one initially free region. In the
expanded queue, idle snapshots found persistent allocations of **2,060
requested bytes** from task `radio_strea` (the recorded, truncated task
name). That matches the stream task's 2,048-byte encoded packet plus header.
One allocation persisted through EOF, another codec, the TLS test and a
minute with no HTTP polling. The trace covers this region, not every heap
allocation or a full caller stack.

Code review and a deterministic regression reproduced the mechanism:

1. The original four buffers become idle while the four added buffers still
   contain queued data or producer/consumer leases.
2. Ordinary shrink frees any idle buffer until its count reaches the limit.
   The old code can therefore free original buffers and retain added ones.
3. Added allocations can divide the formerly contiguous free region even
   after playback ends. The resident count is correct, but addresses drift.

`adaptive_input_set_limit()` and `adaptive_input_return()` now rank resident
pointers by slot order and retain the first `limit` buffers. They count
existing pointers, rather than assuming the first slots remain populated:
emergency reclamation can leave holes. The FLAC-enabled connection preparation
uses this shrink policy instead of a second unconditional reclaim loop.
The actual pressure allocator and its retry remain enabled. Busy packets
are never reclaimed; FIFO data and the minimum resident count are preserved.

The common return path exits the rank check when the count is already at
the limit. Additional work is bounded by the existing 16-slot queue and
occurs during excess-buffer retirement. No new buffer, state field, PCM
copy, codec arithmetic or sample-rate restriction was introduced.

## Build and host checks

Matched owner images use ESP-IDF 6.1 revision `9a97f6c54ec638111ce55cd36581b3c192f15207`,
full compact AAC/SBR/PS, QIO 80 MHz, a 17,058-byte TLS RX reserve, and the
same laboratory CA with normal public roots retained. They use experimental
nominal 48 kHz fractional PDM output. This is a diagnostic comparison;
fractional output remains default-off pending listening.

The fixed and original expanded images have identical active SDK settings.
Exactly three firmware source files differ: `adaptive_input.c`, its header,
and `tls_input_reserve.c`. The inactive CLZ experiment is not compiled.
Linked audits verify full AAC, HTTP and TLS allocator routes. GCC inlines
the rank helper; both caller disassemblies are retained. The first audit's
incorrect expectation of a standalone helper symbol is recorded separately
from the successful completed audit.

| Fixed image versus original expanded diagnostic | Change |
| --- | ---: |
| Ordinary DRAM sections | 0 B |
| IRAM sections | 0 B |
| RTC sections | 0 B |
| Flash code | +516 B |
| Flash constants | +8 B |
| Application binary | +528 B |
| Compared AAC/FLAC code and constant sections | 128 identical sections in 18 objects |

The existing owner diagnostic itself uses 3,128 RTC bytes. Its timing and
logging effects mean these images are not production CPU benchmarks.

The new host regression fails against the original queue, then passes
against the fix under AddressSanitizer and UndefinedBehaviorSanitizer.
It covers idle baseline buffers with added READING, READY and WRITING
buffers, connection preparation before those leases finish, and holes from
real pressure reclaim. Existing checks also pass:

- 30,000 concurrent queue packets, allocation failures and publication races.
- Five TLS reserve configurations, 8,000 concurrent allocations each, intact
  reserve contents and the enabled four-slot FLAC case.
- 42 enabled-growth and 37 disabled-growth stream lifecycle scenarios.
- 88 prefill cases across eight configurations.

Commands are in [the testing guide](ESP32C3_TESTING.md#experimental-flac-input-capacity-after-decoder-initialization).
Host results check ownership and behavior with platform doubles; physical
observations below provide separate evidence.

## Initial owner-probe observations

Each fresh boot runs three FLAC 48 kHz stereo -> HE-AAC 48 kHz stereo ->
HE-AACv2 44.1 kHz stereo cycles, four HTTPS EOF cases (FLAC/HEv2, AUTO/explicit),
a 75-second HEv2 TLS stream with 1 KiB -> 16 KiB plaintext records, and a
60-second stopped period without WebUI polling. Serial capture is continuous.
All owner snapshots are complete, with no lost, dropped or unknown records.

| Original image | Report entries passed | Initial raw free span | Final largest raw free span | Live allocations in watched region at end |
| --- | ---: | ---: | ---: | ---: |
| Expanded, extra slots 4 | 13/15 | 104,424 B | 94,164 B | 1 |
| Control, extra slots 0 | 14/15 | 100,076 B | 100,076 B | 0 |

The expanded image fails cross-stage recovery: its API largest-block value
loses 8,192 bytes against the first switch-cycle baseline and stays reduced
after the quiet minute. Its persistent allocation ID 1333 is observed in
24 snapshots over approximately 237 seconds, requested size 2,060 bytes,
heap block size 2,176 bytes. This is not an 8 KiB payload leak: the API's
size classes and the allocation's position affect available contiguous size.
The control leaves the entire watched region free.

Both original runs also fail their final runtime gate with Mbed TLS
`-29312` (`MBEDTLS_ERR_SSL_CONN_EOF`, `-0x7280` in the pinned SDK). Each error
is recorded immediately after the record test returns, outside its complete
75-second playback interval. The first harness closes its TLS server right
after sending Stop; that can race the stream task's pending read. The
corrected harness keeps the server open through settled idle, as the shared
TLS-record runner already does. The original runtime failures are retained;
neither is silently exempted from acceptance.

## Matched comparison with corrected TLS-server lifetime

Both images then run the same corrected server-lifetime scenario, after
fresh app-only OTA boots:

| Image | Original report | Initial raw free span | Final largest raw free span | Final live owners | Complete-capture runtime gate |
| --- | ---: | ---: | ---: | ---: | --- |
| Original expanded queue | 15/15 | 104,556 B | 95,576 B | 2 | PASS |
| Retention fix, first run | 15/15 | 99,204 B | 99,204 B | 0 | FAIL: incomplete final serial line |

The original queue again leaves two 2,060-byte stream-task allocations in
the region after the quiet minute. Its regular recovery gate passes because
the first switch checkpoint is already smaller than startup and the later
4 KiB decrease is within the existing tolerance. The raw initial-region
comparison still exposes **8,980 bytes** of lost contiguous capacity. A
successful stage gate must not hide that observation.

The fixed image's completed snapshots restore the entire watched region.
However, its first log closes during a serial line, **after** the original
runtime gate. Independent replay rejects complete-capture runtime and DMA
telemetry acceptance. The original 15/15 report is retained alongside this
stricter failure; it is not presented as a fully accepted capture.

The serial reader now allows a bounded 0.5-second grace period to finish
the pending line, using single-byte reads so it stops at the newline. The
existing port read timeout also bounds each read. Missing newlines, I/O
errors and overlong lines still produce a failure marker. Eight capture
tests, six DMA-parser tests and two owner-log tests pass. The repeated run
also checks runtime **after** closing capture, so a terminal truncation can
no longer escape its final report.

For the first corrected pair, observed HEv2 TLS CPU averages are **59.30%**
and **62.29%** respectively. Minimum total free heap is 23,152 / 23,000 B;
minimum largest block is **13,312 / 8,704 B**. There are no observed DMA
counter increments in either record-playback window, but the fixed run's
whole-capture qualification is rejected as described above. These are not
measurements of analog continuity or a speed improvement. Different
fresh-boot allocation layouts remain a confounder, and the retention policy
does not guarantee a larger free block during playback.

## Repeat with complete capture: memory recovered, WebUI timeout remains

The same fixed application was repeated with the corrected reader and
post-close gate. **15/16 report entries pass.** The serial capture and
post-close runtime gate pass, all nine switch observations and four EOF
cases pass, and the watched region returns from **107,828 B to 107,828 B**
fully free, with zero live owners after the quiet minute.

The TLS record-growth case nevertheless fails. Its status observation ends
at **39.922 seconds of the requested 75**, following a 5.016-second TCP
connection timeout. The subsequent Stop request also fails to connect for
5.015 seconds. The next idle-stage Stop succeeds. These are two failed
connections, each recorded at both connect and enclosing-request levels;
the exception chain is not evidence of four failures.

No final record-acceptance snapshot is captured. Replay keeps that test
failed and marks its interrupted performance result incomplete. Partial
observations show 62.77% weighted CPU, minimum free heap 23,004 B and largest
block 13,312 B, with no observed DMA counter increments. Those partial
figures do not qualify a complete TLS run or prove uninterrupted sound.
No allocation/decoder/TLS fault, panic or unexpected reset is recorded in
the complete filtered serial capture.

This reproduces a WebUI connection failure despite successful settled heap
recovery. The queue fix does not resolve that separate symptom, and its
cause is not established. Next investigation should correlate TCP connection
attempts with listener/socket state, network buffers and Wi-Fi events, using
the same bounded queue and TLS reserve controls.

## Restoration

After each comparison, the controller restores `idf61-qio80-8c1f2d2d`,
application SHA-256
`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
The final restoration verifies its ELF identity, unchanged Wi-Fi, playlist
and settings, and three AAC 44.1 kHz stereo playing observations. It uses
the prior integer output clock. Diagnostic images remain saved under
`firmware/development/`; none is declared production-qualified.

## Evidence and remaining qualification

[Frozen data and offline replay](../tests/results/esp32c3-switch-owner-20261009/README.md)
retain both harness versions, raw observations, the failing host regression,
successful host checks, build audits and the source overlay. Shared prior
sources are checked through a pinned archive index. Private settings and
TLS private keys are excluded.

The queue correction does not establish gap-free public-radio playback or
analog sound quality. Heavy FLAC continuity, repeated switching with the
candidate's production settings, negative OTA tests and the prior WebUI
timeout still require qualification before enabling extra input slots.
CPU has no pass/fail threshold, following the preference to prioritize audio
continuity. The user cannot listen now; exact-clock analog qualification is
deferred.
