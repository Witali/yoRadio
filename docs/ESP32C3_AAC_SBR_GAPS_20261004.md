# ESP32-C3: extended SBR-gap regression

**Status: the recorded PC18 candidate fails the 3-LSB precision gate.**
Memory/lifecycle and format checks pass in QEMU. This work changes test coverage,
not production defaults or the firmware installed on the physical board.

Follow-up: [PC19 high-QMF history](ESP32C3_AAC_PC19_20261004.md) passes this
corpus at 2 LSB maximum, with 144 extra allocated bytes. The rejected PC18
evidence below remains unchanged; production qualification is still open.

## What is tested

The earlier [retention test](ESP32C3_AAC_SBR_RETENTION_20261004.md) concatenated
independent LC and HEv2 fixtures. The new
[fixtures](../tests/fixtures/aac_sbr_gap/README.md) remove only parser-identified
SBR FIL elements from actual HE-AAC frames. Every AAC core bit and every trailing
fill element is preserved; only the SBR element, ADTS length and final padding
change. Unsupported syntax fails closed rather than being edited by byte search.

Each case plays its original frames, all corresponding frames without SBR, then
the original frames again. The same decoder stays open throughout. The sequence
contains 11–15 consecutive frames without extension data. The input is split into
1-, 7-, 193- and 31-byte chunks to exercise header/payload boundaries.

Two independent decoders receive different output-buffer poison patterns before
every call. PCM must match completely and guards must remain intact. After the
captured sequence, both decode another missing-SBR phase; one is reset, the other
is recreated, and their next original-file PCM must match byte-for-byte. Finally,
a decoder is destroyed with nine buffered bytes of an incomplete frame.

## Reference implementation and mono output policy

Pristine FAAD float and fixed builds pass all four sequences, retaining full
32/44.1/48 kHz output and the established SBR/PS state. Source files and executable
hashes are pinned. Their frame and private SBR-state traces are retained.
This establishes reference behavior, not complete MPEG conformance or bit-exact
PCM equality between FAAD and the native SDK.

The first native test expected mono PCM for mono HE input. Both compact and
full-precision images rejected that assertion. The native controller explicitly
duplicates non-PS mono SBR into stereo when output channels are unspecified.
The corrected test **proves** this policy against the unchanged native
controller, with byte-identical PCM, and checks every L/R sample pair. Both
original failed logs and their source/ELF hashes remain in `first-failure/`.
The file is still a mono HE-AAC source; duplicated output is not evidence of PS.

This exposes a separate reporting issue: `native_aac_decoder_label()` currently
infers HE-AACv2 from mono ADTS plus stereo upsampled PCM. That inference also
matches duplicated HE mono. The next metadata fix must read actual SBR/PS state,
preserve the distinction between encoded and PCM channels, and test PS transitions.
No metadata fix is claimed by this change.

## Exact compact/full-precision PCM result

Both images use the same experimental late-SBR/retention controller. The
reference retains native 32-bit sample histories plus existing lossless owner
compaction. The candidate uses 18-bit high-QMF history, four persistent smoothing
rows, scoped low-QMF scratch and the asymmetric owner. All returned signed-16 PCM
samples are compared, including startup and loop boundaries, with no alignment,
resampling, gain matching or skipped samples.

| Source | Native PCM | Compared channel samples | Max error: initial / missing SBR / resumed | Samples over 3 LSB |
| --- | --- | ---: | --- | ---: |
| HE-AAC stereo 44.1 kHz | 44.1 kHz stereo | 172,032 | 1 / **5** / 0 LSB | **41** |
| HE-AAC stereo 48 kHz | 48 kHz stereo | 184,320 | 0 / 0 / 0 LSB | 0 |
| HE-AACv2 stereo 44.1 kHz | 44.1 kHz stereo | 184,320 | 1 / 2 / 1 LSB | 0 |
| HE-AAC mono 32 kHz | 32 kHz, identical L/R | 135,168 | 0 / 2 / 0 LSB | 0 |
| **Total** | | **675,840** | **5 LSB maximum** | **41** |

2,254 samples differ; RMS error is 0.0863904 LSB. All violations occur in the
44.1 kHz HE stereo missing-SBR phase, from its third frame onward. The resumed
phase in that case is exact. The precision comparator exits **2**, and the saved
result explicitly has `precision_pass: false` and `production_qualified: false`.
The existing 3-LSB limit is unchanged.

The preceding 189,440-sample synthetic transition reproduces its earlier PCM
hashes and maximum 2-LSB error exactly. Its narrower pass does not override this
new rejection. The ordinary six-stream controller comparison also remains exact
over 887,808 samples.

## Memory and lifecycle evidence

- 971,369 pointer checks and 63,796 checked copies pass.
- 466 tracked allocations have 466 matching frees; 12 reset boundary checks pass.
- Four reset-versus-fresh comparisons and four partial-frame closes pass.
- Existing allocation-failure injection, concurrent decoder isolation, negative
  pointer/buffer checks and heap poisoning still pass.
- The measured decoder stack margin remains 2,844 bytes on the unchanged 16 KiB
  stack. Instrumented PCM capture is unsuitable for CPU-performance claims.
- SBR owner: 32,744 bytes requested / 32,756 allocated for the compact candidate;
  49,708 requested / 51,188 allocated for the full-precision history reference.
  These are QEMU owner measurements, not total radio RAM or a new saving.

## Reproduction and interpretation

Both existing QEMU build directories include the new corpus when
`YORADIO_QEMU_AAC_LATE_SBR_TEST` is enabled. Capture additionally requires
`YORADIO_QEMU_AAC_LATE_SBR_CAPTURE`. The saved configs are in
[the evidence directory](../tests/results/esp32c3-aac-sbr-gaps-20261004/).

Run `run_aac_late_sbr_capture.py` for compact and full-precision builds as in the
preceding retention document, using separate output directories. Then run:

```powershell
python tools/codec_benchmark/compare_aac_sbr_gap_pcm.py --reference-log .build/aac-sbr-gaps/reference/qemu.log --candidate-log .build/aac-sbr-gaps/candidate/qemu.log --output .build/aac-sbr-gaps/pcm
python tests/test-aac-sbr-gaps.py
```

The **first command is the precision gate and currently fails with exit 2**.
The second verifies fixture provenance, exact reproduction of the saved rejected
result, parser boundaries and rejection of incomplete or altered captures. Its
eight passing tests do not turn the rejected precision result into a pass.
The prior retention, late-SBR and pointer test suites also pass (23 tests).

Evidence includes raw native PCM and logs in gzip, per-frame errors, full error
histograms, FAAD state/format traces, configs, source snapshots, native patch
audits and checksums. No credentials or private radio URLs are recorded.

## Next work before deployment

1. Isolate the lossy high-QMF history contribution, then evaluate an extra
   mantissa bit or another bounded precision improvement. Keep the 3-LSB gate
   and measure actual owner size; do not assume a wider format costs zero RAM.
2. Fix mono/PS reporting using the decoder's actual extension state.
3. Add malformed/truncated extension and late-activation allocation-failure
   coverage. Current partial-close coverage is not malformed-SBR qualification.
4. After those gates pass, repeat physical CPU/heap, HTTP/HTTPS, station switching,
   OTA and the complete supported-codec matrix. The full playback goal remains open.
