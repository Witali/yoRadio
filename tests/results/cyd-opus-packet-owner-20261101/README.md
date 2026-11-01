# CRC-verified audio packet ownership

The new unselected audio packet owner starts only after an actual committed
OpusTags completion event. Its61440-byte audio policy therefore does not cap ID
extensions or comments. Contiguous complete audio packets borrow the held verified
page. Continuations copy each required fragment into a bounded owned packet;
that storage can reach61440 bytes and overlap the current page allocation.

HOST ASan/UBSan/leak checks passed65 schedules and18 independent creator libogg
walks, reconstructing202 borrowed and148 copied packets exactly. Cases use the
complete real C3/C8 coded bodies with whole/grouped/split pages,1-byte/257/whole
feeds, nil continuation flags0/1,70000-byte valid comments, N255,61440 acceptance,
61441 policy refusal and corrupted-page rejection before owner exposure.

Every one of nine actual growth-realloc ordinals has two explicit HOST allocator
seam controls: retry from the same held page/cursor, and separate reset/abandon.
Refusal preserves exact prefix bytes, pointer/capacity, cursor/segment and packet
token. Retry reconstructs the exact61440-byte packet without refeeding input or
premature metadata ACK. Every path ends with zero tracked live prefix bytes.
These are deliberate HOST seams, not observed native ESP allocation failures.

The owner does not call opi_ack or assert decoder drain. Consumer tokens release
packet views. Only after the caller's actual metadata ACK may page retirement
be confirmed. EOS alone never proves decoder-close/output completion; the future
integration must establish those conditions before its ACK. Reset cancels views
and frees continuation storage while preserving token monotonicity.

Initial capture01 is preserved as genuine PASS without fault coverage. Interim02
ran all C fault controls successfully but retained a stale false top-level
reporting flag; its contradiction is preserved and excluded from final
qualification. Capture03 corrects the report and is the qualified checkpoint.
All original processes, sources and records remain unchanged. No production
file, old controller, deferred FLAC scope or private codec ABI was changed.

```powershell
python -B tests/verify-opus-family1-host-checkpoint.py --checkpoint packets
```

The data-only verifier reads no omitted executable or encoded payload and makes
no native decoder/OOM or complete-playback claim.
