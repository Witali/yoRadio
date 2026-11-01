# Anchored documented public handle owner

The new unselected family1 owner prepares header syntax before touching active
state, deduplicates at most8 needed stream IDs, and keeps each public
esp_opus_dec_cfg_t at its stable owner address through actual close. Live owner
movement is refused. Partial construction closes previous real handles; a close
refusal keeps ownership cleanup-pending and blocks replacement of its cfg data.

Every packet's complete all-N framing/duration is validated before synthesis,
including unused streams. One reusable public PCM scratch uses the documented
buffer-resize protocol, preserving actual consumed counts and cached-empty-input
retry. Its maximum stereo120ms capacity is23040 bytes. begin/write callbacks
stage per-stream PCM; finish follows complete needed-stream synthesis. This
owner performs no trim, gain, speaker mix, page ACK or queue publication itself.
The caller must retain/emit mapped channel planes with appropriate ownership.

HOST ASan/UBSan/leak tests passed13 real creator-backed positive cases and
2,679,360 exact gathered PCM samples against independent creator multistream
synthesis. They include all three full20ms fixtures, C1–8 nondefault maps, and the
full original92-packet120ms stream with both unconsumed and consumed-all/cached
buffer-resize models. Pre-skip312, input-rate48000 and header-gain1536 metadata
remain unchanged; raw PCM is neither trimmed nor gain-adjusted here.

Twenty-two HOST contract controls cover each selected open/decode refusal
ordinal, staged-sink cancellation, both scratch realloc ordinals, cached decoded
output cleanup, busy/moved owners, pending-close refusal/retry, malformed unused
duration, packet policy and transactional invalid arguments. Scripted public
statuses are explicitly test doubles; prior real handles use actual creator
creation/synthesis/destruction, and cfg lifetime is checked through close. These
controls do not claim genuine creator/native allocation failure or native ESP OOM
qualification. Complete production integration and radio resources remain open.

Constructor capture01 preserves a missing public esp_audio_dec_reg.h compile
dependency. Capture02 adds that public header and is the qualified HOST result;
the owner C behavior was unchanged. No vendor/SDK tree or production file was
modified, and no private state, archive patch or codec-state serialization is used.

```powershell
python -B tests/verify-opus-family1-host-checkpoint.py --checkpoint decoder
```

The data-only verifier executes no archived/native code and reads no omitted
executable, encoded audio or PCM payload.
