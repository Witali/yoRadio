# R06 positive-window pressure: independent design review

Scope: read-only review of retained results, pinned source and official RFCs.
No firmware, fixture code, Git, SDK execution, guest, socket or debugger action.

## Conclusion and retained outcomes

**A zero receive window is not necessary.** A positive window can be smaller
than the queued segment that this pinned lwIP implementation is willing to emit.
The proposed additional basis is justified if its actual head/range evidence is
captured and validated. It does not justify retroactively passing WS01.

`.build/cpbuf24/rfc-r06-withheld-ws-01/pressure.json` remains **INCOMPLETE**:
actual fd57, EAGAIN11, wait-for-write direction, snd_buf0, queue4, unsent
`0x3ffbd410`, unacked0 and snd_wnd286. D=19705181us, retry clock18708390us;
the derived reference start is18705181us and the remainder996791us. Role/fd/PCB
binding exists, but accepted pressure/timeout events are absent. No actual
head length/sequence/cwnd proof or forwarded same-frame timeout completes the
chain. Sender reports ConnectionResetError; orderly EOF and Close were not
observed. Local cleanup followed. The root checkpoint
`.build/cws-rfc26/root-checkpoint-20261126-2045.json` preserves that scope.

Drained WS03 is a genuine separate **controlPASS**:524/524 commands, terminal
PCAP accounting354441 unique server TCP bytes, healthy peer and all owned
cleanup/join checks pass. It does not by itself prove withheld pressure/deadline.

## Source and standards basis

The pinned SDK does the following:

- [tcp_out.c:1266](C:/Work/yoRadio/.idf/v6.0.2/components/lwip/lwip/src/core/tcp_out.c:1266)
  takes the minimum of snd_wnd and cwnd.
- [tcp_out.c:1268](C:/Work/yoRadio/.idf/v6.0.2/components/lwip/lwip/src/core/tcp_out.c:1268)
  selects the actual unsent head.
- [tcp_out.c:1309](C:/Work/yoRadio/.idf/v6.0.2/components/lwip/lwip/src/core/tcp_out.c:1309)
  compares its sequence distance plus data length with that effective window.
  If it does not fit, output stops at1325. Lines1310–1319 explicitly cover a
  remaining window that can be nonzero and later persist-time segment splitting.
- [tcp_out.c:1336](C:/Work/yoRadio/.idf/v6.0.2/components/lwip/lwip/src/core/tcp_out.c:1336)
  admits queued segments only while the same range fits.

TCP windows describe acceptable sequence ranges. Sender SWS avoidance can
defer small transmissions; the usable window also accounts for outstanding
data. Therefore neither the TCP model nor this implementation makes exact zero
a prerequisite for waiting. [RFC9293 §3.8.6](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.8.6),
[§3.8.6.2.1](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.8.6.2.1).

TCP normal FIN closure and reset abort are distinct outcomes that applications
must distinguish. [RFC9293 §3.6](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.6).
WebSocket Close starts a closing handshake; it is not TCP EOF. Clean closure
requires the closing handshake and transport closure. A failed connection may
omit a Close when the peer is unlikely to receive it, but this does not make
an arbitrary reset a send-timeout witness. [RFC6455 §7.1.1–7.1.4](https://www.rfc-editor.org/rfc/rfc6455.html#section-7.1.1),
[§7.1.7](https://www.rfc-editor.org/rfc/rfc6455.html#section-7.1.7).

The one-second deadline is the project's existing frame policy, not a timeout
dictated by WebSocket. [CYD send helper:116–152](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/websocket_service.c:116)
keeps one D across partial writes and uses the original remainder in select.
Failure reaches [fail_client:201](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/websocket_service.c:201);
[transport shutdown:316](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/components/native_web_transport/native_web_transport.c:316)
retains the existing failed-session path. These source paths, not a host timer,
must establish the failure cause.

## Prospective positive-window criterion

Keep the current zero-window basis. Add a separately labeled
`positive-peer-window-unsent-head-blocked` basis with **all** these facts:

1. Same run/input/source/ELF, actual slow fd/PCB/client ownership and current
   nonzero stored frame D. Native send actually returns EAGAIN/EWOULDBLOCK,
   with wait-for-write direction, snd_buf0 and retained guest TX queue. The
   boolean `writable=true` selects which readiness to await; it does **not**
   mean select has reported the socket writable.
2. One coherent all-stop scalar snapshot: actual cwnd, snd_wnd, lastack,
   snd_queuelen, unsent/unacked; actual unsent head pointer equals unsent;
   nonzero TCP-header pointer and positive data len. No queue traversal,
   payload/TLS-context reading, packet edits or guest writes are required.
3. Recompute, rather than trust supplied derived fields:

   ```text
   seq = ntohl(actual queued TCP header seqno)
   offset = (seq - lastack) modulo 2^32
   head_end = offset + actual head data len
   W = min(snd_wnd, cwnd)

   require 0 <= offset < 2^31 and 0 < len and head_end < 2^31
   require 0 < snd_wnd <= cwnd
   require head_end > snd_wnd       # STRICT; equality fits
   ```

   On this little-endian target, raw/header seqno conversion must be explicit
   and independently checked. Reject ambiguous serial distances, overflow or
   inconsistent fields. PCB snd_wnd already denotes effective bytes; do not
   apply the PCAP window scale a second time.
4. Record unacked; do not generally require it null. Null unacked additionally
   matches the persist-setup condition at1316, as in WS01. With flight present,
   the sequence-distance term already includes it. Requiring snd_wnd<=cwnd
   excludes a congestion-only explanation for the selected predicate.
5. Bind the active frame by owner/fd/PCB/D, not by claiming a queued TCP segment
   is one WS frame. The head can contain previously buffered data. It may also
   change after honest splitting/progress; do not fabricate a stable head or
   assume the positive window can never reopen.

This proves an actual, peer-window-limited queued-head obstruction **at that
snapshot**. It does not alone prove duration, deadline expiry, physical latency
or a broken standard implementation. The withheld-read boundary and matched
drained control support the slow-reader attribution; retain exact tuple/ACK
capture and healthy-peer/resource evidence as independent gates.

## Completion and reset handling

Keep the source-owned same-frame chain unchanged: pressure; actual pre-select
target T with positive D-T; exact original timeval; select0 and source caller
result-3, or a separately proven actual target-clock-expired branch; existing
target ticks/quantization and bounded debugger receipts. D must not be replaced
by a fresh budget for another chunk/frame. A verified successful logical-frame
completion retires this attempted timeout; a later frame's failure cannot be
borrowed. If the caller clears D before its failure branch, preserve the
already-validated causal token rather than pretending that clear proves success.

On a sender-side ConnectionResetError, record **remote_reset_observed**, stop
stimulus and join its owner. Do not set orderly EOF, Close1000, deadline observed
or local-cleanup success as a substitute. Keep the independent guest collector
alive within the original watchdog to finish or reject the causal chain; avoid
closing the slow transport merely to manufacture terminal evidence.

An attributed guest abort after a real same-frame timeout may establish bounded
**abnormal termination** if its failure/caller path and selected-flow server RST
are independently bound and cleanup/healthy-peer/resource gates hold. Report
that result separately from clean EOF/WS Close. A reset alone, including one
first seen during a failed client send, stays INCOMPLETE for timeout causation.
If a new fixture supports this outcome, it needs explicit new oracle tests and
must preserve the frozen/old failure; no catch-and-PASS shortcut is justified.

## Required negative/positive tests before a new attempt

| Input or sequence | Required verdict |
| --- | --- |
| head_end<window or head_end==window | Reject positive blocked-head basis. |
| cwnd<snd_wnd | Reject this peer-window basis, even if congestion blocks output. |
| Positive wnd286 alone with snd_buf0/EAGAIN/queue4 | Insufficient; do not pass WS01 retrospectively. |
| Null/mismatched head, null header, len0, stale fd/PCB/D | Reject snapshot/binding. |
| Wrong byte order, offset>=2^31, arithmetic overflow, wrong derived end | Reject scalar proof. |
| Valid wrap: lastack0xfffffff0, seq0x10, len512, wnd286, cwnd1000 | offset32/end544; accept pressure basis only. |
| Correct pressure, then successful same logical frame | No timeout PASS; retire old D. |
| Correct pressure, timeout on another frame/fd or altered timeval | Reject timeout chain. |
| Real select0 but missing source caller-3/abort attribution | Incomplete causal gate. |
| Remote reset without guest-timeout proof | Abnormal transport observation only. |
| Close frame without transport end, local close, TLS close alert alone | Never rename to orderly TCP EOF/deadline. |
| Source-bound timeout+abort+matching captured RST | Candidate abnormal-termination gate, never clean-close PASS. |
| No PCAP final completeness, healthy progress, no-allocation proof or joined owners | No overall R06 PASS. |
| Zero-window existing case | Retain its prior validated schema and limits. |

No changes are proposed to firmware, TCP/TLS/task budgets, frame/case deadlines,
input/output caps, test payload meaning or packet headers. Only a correctly
observed additional cause can replace the overly narrow exact-zero trigger.

## Narrow candidate-code cross-check

Read-only inspection of `gdb-observer-v5.py`, SHA-256
`6a9e8d1eca04840dedac2d7fdd975cba72ff7c7c45fce29bed04390d4d2b689e`:
`queue_pressure()` at56–94 matches the reviewed strict fit, peer-window/cwnd and
serial-arithmetic conditions; `_positive_unsent_head()` at509–520 checks PCB,
head owner and lastack before scalar header reads. No concrete mismatch was
found in those two functions. This is design/source review, not execution of
its tests or acceptance of a live result. Acceptance remains prospective and
conditional on the independent event/binding/timeout/termination gates above.
