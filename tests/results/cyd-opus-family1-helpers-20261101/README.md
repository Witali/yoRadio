# Family1 plans, framing and borrowed channel views

Unselected pure headers now preserve valid family1 syntax with C1–8, N1–255,
M≤N, N+M≤255, arbitrary valid indexes, duplicates,255 silence and unused decoded
channels. N+M need not equal C. The plan retains at most8 distinct needed stream
IDs, with stereo for coupled IDs and mono otherwise. All elementary framing and
durations are checked before any selected packet view is published, including
unused streams. No allocation, synthesis, trim, gain or downmix occurs here.

HOST GCC ASan/UBSan/leak checks passed9,498,670 assertions:16,511 valid N/M
pairs,132,088 selected C×N×M header patterns and exhaustive individual decoded
index checks. These counts do not enumerate every multi-channel map combination.
Eleven real creator differential cases cover the three default fixtures and
C1–8 nondefault maps with duplicate, unused and all-silent channels. Every creator
float and bounded gathered PCM sample matches. Separate valid PLC cases cover
N255/M0 and N128/M127 with decoded count255. Zero-coded-frame cases are labelled
PLC boundaries; they do not substitute for the active-signal map cases.

Borrowed channel views preserve aliases and exact silence. Bounded gather emits
logical C speakers in Vorbis order without stereo reduction or clipping. Packed
LE data may be unaligned; the eventual output owner must load aligned host-endian
samples for the normalizer/mixer. Caller-owned input and PCM leases must remain
unchanged for the lifetime of their views.

The61440-byte family0/1 audio-packet policy is distinct from malformed framing.
Compatible header extension bytes are accepted. Actual decoder/public ownership,
page reconstruction, output integration and native resource coverage are separate
checkpoints. No complete standard-playback qualification is claimed.

Verify the saved data without running native code:

```powershell
python -B tests/verify-opus-family1-host-checkpoint.py --checkpoint helpers
```

Original source/tool/process identities are preserved. Executable and encoded
payload bytes remain local with exact identities; the verifier does not read them.
