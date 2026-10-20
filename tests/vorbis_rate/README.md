# Public raw Vorbis rate regression protocol

Run with host Python from any working directory:

```text
python -B tests/vorbis_rate/test_rate_protocol.py -v
```

The 19 methods check the exact canonical 68-packet fixture and strict complete
protocols for the signed baseline, unsigned acceptance, optional 64 kHz cap and
two independent restored-guard controls. Negative cases cover public header-error
witnesses, metadata, consumption, PCM sizes, canaries, ordering/counts, core binding,
close results, exact failure location and actual process terminal facts.
These synthetic tests run no codec, SDK, emulator or device.

The [separate SDK/Xtensa evidence](../results/cyd-vorbis-uint32-rate-20261020/README.md)
records actual public decoding of all 16 checked rates against a fresh original
vendor handle at 192000 Hz. The rates include all nine advertised rates, 1,
63999, 64000, 192000, INT32_MAX, 0x80000000 and UINT32_MAX. Rate zero still rejects.
The two casts preserve the pinned signed vendor ABI field and interpret only its
rate bit pattern as unsigned. The optional cap also uses the unsigned comparison.

This isolates raw parsing/metadata/PCM. The radio output hardware's supported
rates, C3/RV32 behavior and complete Vorbis conformance require separate tests.
