# JPEG upload privacy gate

`codec/jpeg_privacy.c` replaces the baseline-specific metadata scanner in the
actual `photo_upload_finish` path. It is independent of the JPEG decoder,
ESP-IDF, networking and LCD. Fixed-size JFIF headers without thumbnails and
canonical Adobe APP14 color-transform headers are allowed. Other APP markers,
comments, thumbnails, noncanonical Adobe payloads and data after EOI are rejected.
Both headers and markers between scans are inspected; FF00, restart/TEM, fill
bytes and DNL continuation are handled without interpreting entropy samples.

The result distinguishes private metadata, thumbnails, invalid/truncated JPEG,
trailing bytes, read failure and cooperative stop. It reports marker/offset and
preserves the callback error, without copying private input strings into errors.
SOF process/precision/dimensions and scan count are observations, not decoder
capability claims. Codec support, entropy correctness, size and memory limits
remain the decoder's responsibility. Passing this metadata gate alone cannot
publish an image; the actual upload path still requires its successful decode.

The parser allocates no heap and uses a 256-byte input buffer. The owner must
serialize source updates and supply verified reads plus a deadline/cancellation
check. The existing synchronous upload owns `media_mutex`; its replacement by
the guarded asynchronous media worker is still pending. The cache identity now
binds this privacy policy so an older policy cannot silently authorize a cache.
The browser's metadata removal, cropping and resizing remain in place.

Checks are separated from image decoding:

- Native grammar controls exercise 45 APP/COM positions, all 353 truncations of
  the multi-scan fixture, both physical read faults and 343 cooperative stops.
  A stuffed byte crosses offset255/256. These synthetic streams test metadata
  grammar; they are not presented as valid entropy-coded images.
- The gate accepts all 63 valid JPEGs already decoded by the independent codec
  oracle, including usual gray/RGB/CMYK/YCCK, progressive, arithmetic and lossless
  variants. Four late APP/COM injections and appended data are refused.
- Seven unsafe variants compile successfully and fail behavioral assertions:
  early SOS return, accepted EXIF, trailing bytes, thumbnails, Adobe flags,
  ignored stop and ignored source I/O error. Compiler failure is not success.
- Existing upload/HTTP/native checks and the ESP32-C2 production build run with
  the new gate. This does not switch TJpgd to libjpeg or prove asynchronous UI,
  target runtime, full network/LCD or hardware acceptance.

```powershell
pwsh -File Small_TV/src/tests/jpeg_privacy/run.ps1 -OutputDirectory NEW_UNIT
python -B Small_TV/src/tests/jpeg_privacy/contract.py --build NEW_UNIT --oracle QUALIFIED_CODEC_ORACLE --output NEW_REAL
python -B Small_TV/src/tests/jpeg_privacy/mutation_contract.py --output NEW_MUTANTS
```

2026-10-20 build: app `733c006a…de1c9a`, ELF `c1f1d94b…1d2ffa`,
source `4c8c3878…c453ce`; 1171136 app bytes, 364864 free partition bytes.
RV32 object: 1224 code bytes, 180 readonly bytes, no data/bss; largest compiler
frame 368 bytes. The final ELF's `photo_upload_finish` calls the privacy gate
before the existing decode validator. No new VM was used in this checkpoint.
Evidence: [`jpeg-privacy-validation-20261020.json`](../../qemu/parity/jpeg-privacy-validation-20261020.json).
