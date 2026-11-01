# Documented public Opus handle composition

The pinned ESP32/LX6 public raw Opus APIs decoded all elementary streams of the
same complete creator-valid family1 fixtures that the stock Ogg path refused.
Six fresh cases passed:3/6/8 channels, each through the documented self-delimited
mode for nonfinal streams and an independent common-framing control. Both modes
produced byte-identical native PCM for every stream and complete channel mapping.

| Encoded channels | Concurrent handles (coupled) | Complete mapped PCM bytes per mode | Observed maximum difference from creator PCM | RMS error, PCM16 LSB |
|---|---|---:|---:|---:|
| 3 | 2 (1) | 63360 | 1 LSB | 0.427289 |
| 6 | 4 (2) | 126720 | 1 LSB | 0.418858 |
| 8 | 5 (3) | 168960 | 2 LSB | 0.448271 |

All22 public handles opened and closed with actual return0. All242 decodes
consumed the exact selected input and produced eleven20ms frames per stream,
10560 samples per channel, at48kHz/16bit. Caller-owned documented configuration
arrays remained alive until close. No private layout, serialized state, codec
wrapper, archive modification, forced status or allocation-failure injection was
used. No production source was changed.

Before SDK execution, an independent framing implementation extracted original
RFC6716 AppendixB segments and removed only their extra length fields for the
control mode. Creator libopus1.4 public single-stream handles reproduced every
original creator multistream float sample exactly after the declared mapping,
and the entire mapped PCM matched the previous creator reference. Thirty-two
independent expected-byte/malformed framing controls passed under host GCC
ASan/UBSan/leak checks. The native self-delimited/common equality is an additional
observed framing witness. The differences in the table are complete saved
observations; no new numerical tolerance or formal codec conformance is claimed.

Actual SDK6.0.2 build and QEMU children completed0 on the first raw-composition
campaign. Real compiler records bind4 selected translation units and146
dependencies. No production Ogg/audio-service/output source was consumed. Worker:
core1, priority3, stack16384. Heap was283704 before and after every case and the
complete campaign, retained0; minimum150936 with five concurrent handles.
Stack-free was3252. Heap integrity remained intact. These resources describe the
diagnostic, not combined radio/TLS/display production load.

This establishes a public reuse path for these three complete default mappings.
Production packet reconstruction, general family1 mappings (including unused,
duplicate and silent channels), correct speaker mixing, trim/gain integration,
broader packet modes and full application resources remain separate gates.
The completed stock-Ogg NOT_SUPPORT record is unchanged. Production's current
first-two-channel output behavior is not treated as a correct surround downmix.

Run the data-only evidence verifier:

```powershell
python -B tests/results/cyd-opus-multistream-public-20261101/verify.py
```

It checks source/process/compiler bindings, all genuine public events, complete
input/frame/layout/close counts, native mode identities and seven contradictory
controls. It runs no native program and reads no omitted payload. Numeric PCM
differences are preserved measurements; the data-only verifier does not recompute
them without PCM. The full original UART log contains PCM and remains local with
an exact byte/hash identity. `qemu.events.log` removes only complete `MS_PCM`
lines and preserves every other original byte, with explicit derivation counts.
Executables, images, encoded transports and PCM remain local. The run controllers
take the exact historical creator-qualified capture as input; the evidence
verifier needs no local capture payload.

Relevant creator contracts:
[RFC6716 section3](https://www.rfc-editor.org/rfc/rfc6716.html#section-3),
[AppendixB](https://www.rfc-editor.org/rfc/rfc6716.html#appendix-B), and
[Opus public multistream API](https://opus-codec.org/docs/opus_api-1.5/group__opus__multistream.html).
