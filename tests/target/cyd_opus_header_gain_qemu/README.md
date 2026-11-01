# Public OpusHead output-gain observation

Three complete Ogg inputs differ only in signed header gain (zero/+6/-6 dB)
and its first-page CRC. Six independent stock public decoder handles compare
whole input and 257-byte feeds, genuine data-bearing EOS and full draining.
Every decoded PCM byte contributes to SHA-256, complete signal energy, absolute
sum, nonzero count, peak and saturation counts. No application gain is applied.

This is a diagnostic worker on core 1 / priority 3 / stack 16384 using the
unchanged LX6 Espressif libraries on SDK 6.0.2. It does not modify production
sources, private codec layouts, binary archives or task control state. Both idle
watchdogs, stack canaries and heap poisoning remain enabled. No board/network
is used. Images have test partitions and must not be flashed as radio firmware.

```text
python -B tests/run-cyd-opus-header-gain-qemu.py --output .build/cyd-opus-header-gain-new
```

A successful observation campaign is distinct from header-gain support. If all
three nonzero outputs are identical, the report records ignored gain. Otherwise
an independent raw libopus plus normative-gain reference is required to assess
the observed gain. This is not universal format or numerical conformance.
