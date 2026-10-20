# C3 public raw Vorbis unsigned-rate regression

Run the nineteen pure protocol methods with host Python:

```text
python -B tests/c3_vorbis_rate/test_rate_protocol.py -v
```

The native C3 protocol requires actual coordinator/decoder core0 throughout,
including priming and the final packet. It checks the exact canonical68-packet
fixture, all16 rates, metadata, consumption, PCM sizes, canaries, close results,
three complete modes, two independently restored guards and actual terminal facts.
Synthetic tests execute no codec, compiler, SDK, emulator or device.

The [separate C3 SDK/RISC-V record](../results/c3-vorbis-uint32-rate-20261020/README.md)
retains the actual baseline, acceptance, optional-cap and two restored-guard
campaigns. C3 uses its own SDK6.1/RV32 archives,160MHz/unicore profile and bootloader
offset0. CYD/Xtensa results cannot substitute for those independent gates.

Raw header acceptance does not extend radio output hardware rates or establish
complete Vorbis format/conformance, Ogg, resource or physical qualification.
