# Experimental PC16 PS delay storage

Full-rate AAC/SBR/PS with 16+16 mantissas and eight exponent nibbles per word.
Includes the experimental smaller PS owner, early scratch allocation, compact
service stacks, bounded Wi-Fi buffers and HTTP CPU diagnostics. No deep sleep.

Not production-qualified: the retained raw-PCM corpus reaches 3 LSB, and QEMU
instruction overhead is 32–43% on active PS. Compact payload does not further
shrink the fixed SBR owner. See `docs/ESP32C3_AAC_PC16_WRITES_20261001.md` and
`manifest.json`. This image predates the decoded-value cache experiment.
