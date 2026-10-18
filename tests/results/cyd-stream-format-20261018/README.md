# CYD stream format and bitrate state

The deferred format/bitrate work was restored at the user's request. CYD now
publishes decoder PCM layout, precise fractional kHz, codec and a bitrate source
in the existing status API. The public AAC API establishes PCM layout, so its
description explicitly says `AAC PCM`; it does not claim nominal HE/PS layout.
Custom legacy callbacks refresh layout on every callback instead of retaining
the first rate/channel count. ICY hints never outrank decoder or measured data.
Actual measured-rate collection is a subsequent part of the same plan item.

Output failure is latched under the generation/state mutex, keeping a late
decoder callback from restoring playback. Decoder errors still drain already
queued PCM in FIFO order. Invalid decoder layout and returned output length
are reported before PCM publication. These are scripted API seams, not claims
about a failure observed on a physical board or inside a vendor decoder.

- [Six lifecycle variants](lifecycle/report.json) pass, including layout changes,
  exact 44.1/11.025 kHz formatting, metadata/result failures, concurrent failure
  latch and ICY/decoder/measured source priority.
- [HTTP/status](http/report.json) passes 49 stream scenarios and maximum-size
  JSON fields, optional ICY hints, redirect replacement and pending-state checks.
- Startup passes for both [CYD](startup-cyd/report.json) and
  [C3](startup-c3/report.json), including 34 media corpus cases per target.
  CYD preserves connecting state and bitrate hints until decoder PCM; C3 keeps
  its existing provisional publication. The CYD fixture now explicitly asserts
  zero provisional state updates instead of expecting a stopped-state callback.

The campaigns execute actual production functions with host SDK/RTOS seams and
ASan/UBSan. Source snapshots and hashes are preserved. Pinned SDK builds and
physical audio acceptance remain separate gates.
