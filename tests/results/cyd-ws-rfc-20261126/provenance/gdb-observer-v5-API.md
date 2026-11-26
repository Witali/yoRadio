# Private observer v5 peer-window pressure basis

Use `gdb-observer-v5.py`. This is a prospective, independently reviewed proof
basis; previous actual WS01 lacks the new fields and remains INCOMPLETE. No
older file/result is changed. Public Collector/Binding/common event APIs,
source/ELF/config/site pins, two hardware sites, startup/command/stop/peer bounds,
timeout state transitions and process ownership are unchanged. No live process,
guest, socket, compiler or Git action was performed during v5 preparation.

## Source and mathematical condition

Pinned ESP-IDF6.0.2 lwIP `src/core/tcp_out.c`, SHA256
`f31f0eef0c9aba4402ebff73b6d99a560b1d7ec219b4e0e5791996c41a832308`,
sets `wnd=min(snd_wnd,cwnd)` at1266 and at1309 blocks an unsent segment if
`ntohl(head.seqno)-lastack+head.len > wnd`. A positive receiver window can be
too small for the queued whole segment. A later persist split, ACK or window
update can still permit progress. This proves instantaneous head blockage, not
permanent unsendability or a timeout. It does not require `unacked==0`; that
extra condition only describes the separate persist-timer setup. `snd_wnd` is
already the effective byte window, so PCAP scaling must not be applied again.

The original zero-window branch remains. The additional positive-window branch
requires actual write EAGAIN, zero send-buffer capacity, retained queue with a
nonzero unsent head/header and positive data length, `0<snd_wnd<=cwnd`, and:

```
seq_host = ntohl(actual_raw_header_u32)  # pinned little-endian target
distance = (seq_host - lastack) & 0xffffffff
end = distance + head.len
distance < 2**31 and end < 2**31 and end > snd_wnd
```

Equality fits and is rejected. The conservative half-space bounds exclude stale
or ambiguous sequence arithmetic, including overflow of the source u32 sum.
The cwnd relation excludes a congestion-only limit. Every owner/head/header
field is a scalar read under the same all-stop, with repeated PCB/unsent/lastack
binding checks. An all-stop can catch the stack mid-update; inconsistent or
unreadable state remains incomplete. No queue traversal, payload/TLS-context
read, inferior call, packet/window change or guest write is introduced.

## Event addition

All existing fields remain, with `pressure_basis` equal to `zero-peer-window`
or `positive-peer-window-unsent-head-blocked`. Both retain the five old
`guest_queue` fields. Only the positive basis requires these additional fields:

```
guest_queue.cwnd, guest_queue.lastack
guest_queue.unsent_head = {
  pointer, tcphdr_pointer, len, seqno_raw,
  seqno_host, seqno_conversion: 'ntohl-u32-from-little-endian-target',
  seq_distance, sequence_end
}
```

The head pointer must exactly equal `guest_queue.unsent`. Raw seqno is the actual
numeric header scalar; host seqno/distance/end are explicitly derived. The
head may contain older TCP data and must not be portrayed as identical to the
current WebSocket frame. Current-frame binding still uses actual fd/PCB/client
storedD. `guest_queue_sample_site=actual-would-block-branch` records the queue
snapshot scope; pressure observed_us is the subsequent actual target retry
clock. Historical internal `write_ready` means WAIT-FOR-WRITE direction, not a
claim that select reported writable. `would_block_write=true` describes the
observed EAGAIN/write-direction branch.

New peer validation must independently retain/check the additional basis fields,
not silently discard them. An actual same-frame original deadline, real target
timer/prepared remainder/select-zero or clock-expiry, exact caller -3 and
source-bound finish/abort remain mandatory for timeout. Final independent wire
evidence and lifecycle/resource gates remain root-owned. Close, reset, flood
size or host elapsed time alone never substitutes for that proof.

## Pure verification

All55 v4 tests plus14 focused cases pass:69 PASS in0.093 seconds. New cases
cover positive-small-window/complete same-frame timeout, equal/full window,
congestion-only and available-buffer negatives, null/missing head/header,
zero length, stale/half-space sequences, valid and invalid wrap, malformed
fields, nonempty unacked, actual scalar helper/snapshot decoding and owner
mismatch. Tests bind the pinned tcp_out source hash and scalar comparison.
No live qualification is claimed; root alone releases actual execution.
