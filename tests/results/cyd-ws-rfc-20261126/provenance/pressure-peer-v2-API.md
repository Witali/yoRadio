# Private pressure peer v2 termination contract

Preparation and scripted verification only. No new actual endpoint, guest, GDB,
SDK or Git action was performed. Original a698 peer/client/tests and historical
attempts remain unchanged; the old sender-reset attempt is still ineligible.

## Binding and source events

The six fields of Binding are unchanged. Root calls
`observer.bind(binding, guest_tuple=slow_guest_tuple)` once, using the exact
tuple from the same Collector role map and bind_slow call. The tuple has exactly
local_ip, remote_ip, local_port, remote_port. snapshot() includes a copied tuple.

Pressure accepts the reviewed collector v5 schema, including the required
`guest_queue_sample_site='actual-would-block-branch'`:

- zero-peer-window: snd_wnd=0 and the original five queue fields.
- positive-peer-window-unsent-head-blocked: those fields plus cwnd, lastack,
  unsent_head. The pointer/header, positive length, explicit target-little-endian
  ntohl conversion, modulo distance/end and `0 < snd_wnd <= cwnd`, snd_buf=0,
  end>snd_wnd relationships are independently validated. Nonzero unacked is
  allowed. All selected nested queue metadata is copied.

Both timeout bases require integer caller_result=-3. All original actual clock,
select0/original remainder/tick, same-frame/stored-deadline and debugger bounds
remain. A guest-timeout is accepted as the pinned source collector's post-
finish(graceful=False,closing=True)/shutdown(graceful=False) event; it does not
invent an entry clock or use packet time as guest time.

## Exact final wire event addition

Live wire events never carry terminal proof. The final root wire-accounting
event adds `selected_slow_terminal`, one exact entry returned by frozen PCAPv2
selected_terminal_coverage, selected by role/fd/PCB/full tuple. Exact top keys:

`role, guest_fd, pcb, guest_tuple, terminal_basis, server, peer,
captured_ranges_contiguous, missing_bytes_inferred`.

Each side has exactly `payload_bytes, fin_offset, sequence_end, fin_acked,
max_ack, rsts`. Types/ranges, sequence_end=payload+FIN, FIN-at-payload-end,
cross-side ACK bounds, contiguous=True and inferred=False are checked. FIN basis
requires both FIN/ACK and zero RST; reset basis requires actual recorded RST.
Owner and full tuple must match Root's binding. Submitted and returned nested
proofs are deep-copied under Observer.lock; snapshot mutation cannot alter them.

Root still owns final capture completeness after stopping QEMU, dump-write-error
absence and both selected flow terminal checks. This peer never authenticates a
controller or reconstructs capture proof itself. No packet payload is exported.

## Distinct terminations and final policy

SocketGate.recv alone converts an actual remote ConnectionResetError into
ReceiveReset while not locally closed. Session records transport_reset and
termination_kind='remote-reset', without setting transport_eof, clean_tls_eof
or any WebSocket Close flag. Sender resets and automatic Pong-send resets are
ordinary errors. Local cleanup cannot manufacture a receive-reset candidate.

Only the withheld slow reader can consume ReceiveReset as a pending candidate.
It starts after a real same-frame pressure/timeout/caller-abort token, sender
join, zero withheld reads, no sender error or partial command, and no local close.
At observation, it rechecks that immutable token and ownership. The main loop
can then run healthy progress/normal Close. Before final wire proof it remains
INCOMPLETE. Receive-reset qualification additionally requires matching captured
server.rsts>0; peer-only/local-cleanup RST is insufficient.

An actual ordinary EOF stays orderly-eof. An established TLS SSLEOFError remains
PeerEOF(clean_tls=False), tls-ragged-eof, never reset or clean TLS closure. Either
EOF path can prove withheld bounded termination only after that same real abort
token and matching final actual server FIN or server RST. Generic TLS errors,
verification failures, missing witnesses and local EOF never qualify.

Controls never use abnormal termination: resume Pong, a completely sent exact
default Close 1000 payload, exactly received matching Close 1000 payload, ordinary
remote EOF (clean TLS EOF for WSS), and both-FIN/ACK/no-RST proof are required.

Additional report fields:

- slow_remote_reset, slow_termination_kind, slow_secure, slow_clean_tls_eof;
- slow_normal_close_sent and slow_normal_close_received;
- slow_reader_timeout_token and slow_termination_token;
- local_closed_at_termination=False for witnessed withheld termination.

`timeout_token(observer.snapshot())` returns the binding, tuple and exact
frame/start/deadline/timeout-basis/caller-result identity. It accepts no missing
witness. It is a bounded source-evidence token, not a new timing observation.

Existing watchdog_fired and observation_exhausted must both be explicitly False
for any final PASS. A late final proof cannot promote an expired fixture.

The original 30-second watchdog, 27-second I/O cutoff, three-second cleanup,
command/byte/8 MiB envelope, strict TLS verifier/cipher and SSL single-owner
handoff remain unchanged. Root owns versioned runner integration and live release.
