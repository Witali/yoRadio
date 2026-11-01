# Standalone public family1 adapter qualification

`prepare.py` creates a fresh data-only fixture bundle from the complete pinned
creator-qualified 3/6/8-channel packets and all 92 original 120 ms stereo
packets. It preserves every coded packet body. The finite inventory adds
selected C1–8 mappings with duplicate, silent and unused decoded channels;
decoded channel count need not equal logical channel count.

The independent Python writer owns identification/comment headers, lacing,
page sequence, granules and CRC. Whole and continued/nil-page variants carry
the same original audio. The comments include declared UTF-8 and an arbitrary
binary tail. A separately prepared elementary-offset table retains the exact
original Appendix B framing for the direct public-native reference.

The new standalone target runs twelve direct-reference cases and twenty-two
adapter schedules. The reference translation unit uses documented public
ESP raw-handle calls, the prepared framing table and its own channel gather and
preskip/end calculations. Its compiler dependencies must exclude production
framing/mapping/trim/page helpers. Byte-exact full logical PCM SHA256 equality
against that reference is a same-vendor integration gate. Creator numeric
observations remain in their separate evidence; this gate adds no tolerance
or formal codec-conformance claim.

The sink validates gain metadata and captures unscaled trimmed PCM. Combining
header gain, user volume and speaker mixing remains the production output
owner's separately qualified responsibility. The standalone target checks
borrowed scratch/immutable-zero lifetime, actual complete input and per-stream
frames, real public statuses/closes, page retirement and observed heap/stack.
Both encoded and PCM owners survive at worker lifetime if a real close refuses.
There is no native allocation fault injection or hardware/network access.

The worker runs on core 1, priority 5, with 16384 bytes, independently of the
full application's stream and output tasks. Target type sizes and that worker's
cumulative stack high-water mark are observations, not a full-radio resource
qualification. A genuine resource or decoder refusal keeps the required gate
open; it is not relabelled a permitted unsupported format.

Use `tests/run-cyd-opus-family1-playback-qemu.py --preflight-only` before the
coordinated SDK launch. The new syntax-only checker reuses an earlier campaign
only as a read-only flags/include recipe and redirects every output and temporary
path to a fresh capture. Initial native and syntax failures remain immutable.
