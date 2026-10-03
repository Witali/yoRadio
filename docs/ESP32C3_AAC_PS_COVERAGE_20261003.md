# Groove Salad 16: PS coverage verified against reference decoders

## Result

The retained `groovesalad16.aac` recording is **32 kHz mono HE-AAC without active
PS**. No missing PS processing was found in our compact decoder for this file.
This confirms the earlier [FAAD scaling observation](FAAD2_HISTORY_SCALING_20261001.md),
and resolves the question raised by the pointer audit. It does not classify
future broadcasts from the same station URL.

| Decoder / observation | Result for the same 469 ADTS frames |
| --- | --- |
| FAAD fixed-point, unchanged control | 32,000 Hz, one channel, zero PS frames |
| FAAD floating-point, unchanged control | 32,000 Hz, one channel, zero PS frames |
| FFprobe 8.1.1 | Reports HE-AACv2, 32,000 Hz, two channels |
| FFmpeg 8.1.1 signed-16 output | 1,921,024 channel samples; left and right identical at every sample |
| Native compact decoder, full pointer-audit run | Zero additional PS dispatches; complex SBR active |
| Native GDB trace, first 32 frames | SBR synchronized at frame 5; 28 extension-parser calls; zero PS-data reads |

FAAD emits 958,464 mono samples, excluding its initial delayed frame. The
FFmpeg/native sample counts include startup output. No cross-decoder PCM-error
claim follows from these different output lengths.

The pinned [FFmpeg decoder source](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/aac/aacdec.c#L1968-L1975)
provisionally enables PS and assigns the HE-AACv2 profile when implicit SBR is
found while PS is unknown and the output has one channel. That profile label
therefore does not prove that a PS extension was decoded. Here the independent
FAAD results and identical FFmpeg channels support the mono interpretation.

## Evidence and reproduction

[Result and commands](../tests/results/esp32c3-aac-ps-coverage-20261003/result.json)
retain the input, FAAD binary, FFmpeg binary/PCM and source hashes. The two FAAD
executables come from the pinned, source-verified comparison workflow linked
above. The saved GDB script uses the exact pointer-audit ELF and a disposable
QEMU flash image; it stops tracing after 32 capture frames and leaves the rest
of the full audit running. It never accesses the physical board.

The [QEMU log](../tests/results/esp32c3-aac-ps-coverage-20261003/qemu.log),
[GDB log](../tests/results/esp32c3-aac-ps-coverage-20261003/gdb.log), and two FAAD
control logs are retained. Audio is not copied into the repository.

## Acceptance consequences

- Keep ABBA and the synthetic HE-AACv2 fixture as active PS coverage gates.
- Keep Groove Salad 16 as a complex-SBR mono case, even if a backend duplicates
  its output channels. Never count it as a PS case from FFprobe metadata alone.
- The firmware's source-profile display still needs actual SBR/PS flags instead
  of inferring PS from a mono ADTS core and stereo PCM. This is distinct from
  the RAM failures on public radio; neither issue is fixed by changing test labels.
