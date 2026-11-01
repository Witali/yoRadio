# Full stock Opus PCM capture for independent position checks

This separate diagnostic captures complete public Ogg-decoder output for the
unchanged 20 ms and 120 ms fixtures. Each fresh decoder uses 24576 output bytes,
genuine data-bearing EOS and a complete empty-input drain. All input/metadata,
whole raw PCM and fixture-derived window identities must reproduce the earlier
stock-vendor checkpoints before the host accepts captured bytes.

No parser replacement, private ABI, synthesis repair, trim filter or production
change is used. Labeled sequential hex records are observations of the unchanged
PCM. Full PCM and hex logs stay local under ignored `.build`; publication uses
identities and independent comparison metrics only. The real SDK, dual-core LX6,
heap integrity, stack protections and both idle watchdogs remain enabled.

```text
python -B tests/run-cyd-opus-position-qemu.py --output .build/<fresh-capture>
```

These diagnostic images are not production firmware and must not be flashed.
