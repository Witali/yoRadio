# Restore input headroom after underflow

Diagnostic PCM-queue path only,2026-09-17. No additional allocation/buffer.
The existing start prefill is reused after all of these conditions:
playing, decoder needs more input, recv reached EAGAIN, transport has not
ended, and the DMA underrun counter changed since the last decoded packet.
Ordinary packet/page boundaries and temporary EAGAIN with enough PCM do
not pause. Counter wrap is handled by inequality, not signed subtraction.

Keep the same TCP connection, codec history, Ogg/ICY parsing state and PCM
ownership. The output task drains its existing PCM; hardware emits neutral
PDM if needed. Refill the compressed queue until full or the existing1s
deadline, respecting stop/station cancellation and EOF. Report BUFFERING,
then Playing only after another packet has actually decoded. Do not reset
DMA counters or omit that pause from any continuity measurement.

This cannot repair a network outage; it tests whether restoring read-ahead
prevents repeated short gaps after a single outage. Physical validation is
required before calling it a playback fix. Other firmware paths unchanged.
