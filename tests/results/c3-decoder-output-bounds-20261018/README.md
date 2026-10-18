# Reject an oversized decoder output declaration before PCM copy

The [negative control](negative.log) injects a success result declaring 4,100 PCM
bytes for a 4,096-byte output buffer. The actual C3 `send_pcm` reads beyond the
array; ASan reports stack-buffer-overflow in `memcpy`. Codec writes are not part
of this injection: this tests the application's handling of returned metadata,
not an observed codec/library error or a crash on the physical board.

The decoder loop now rejects `frame.decoded_size > output_size` before advancing
input or copying PCM, records a process fault and closes through its existing
failed-generation path. The host wrapper compiles that actual guard and the
actual frame-publication branch with real state and `send_pcm`, retaining the
producer condition rather than copying a validation model into the test.

The [positive run](test.log) passes the oversized case with no PCM publication,
one diagnostic and terminal error state, plus all seven original format/AAC
groups. The C host programs use ASan/UBSan; the suite's separate actual Helix C++
adapter command remains an ordinary host codec test. Kernel/driver timing and
physical audio are outside this host result.
