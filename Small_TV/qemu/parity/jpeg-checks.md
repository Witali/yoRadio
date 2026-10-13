# Executed JPEG decoder comparisons

`../../src/tests/jpeg_oracle.py` executes the factory RV32 input/output callbacks,
TJpgDec preparation, Huffman/IDCT/color conversion and ST7789 blitter, then the
corresponding routines in the actual compiled C ELF. SDK flash, allocation,
mutex operations and the LCD byte transport are the adapted boundaries.
JPEG algorithms and output callbacks run from the verified executable bytes.

The image gate covers all 107 public JPEGs: four status images, 98 animation
frames and five photos. Each comparison includes all 57,600 RGB565 pixels,
including the untouched background. Sanitized animation headers determine the
native frame offsets: removing APP/COM metadata changes successive offsets.
Public files and archived partition bytes must match. Factory reads retain the
original bytes; no metadata or settings strings are written to the report.

## Confirmed differences

The previous application `5e12da8c5b20740316f17da954b7ce8bc250e06b04e2f1e4f1095ccf484acc44`
matched all photos and animation frames, but its four status images differed by
3, 33, 3 and 3 pixels. [Negative evidence](jpeg-before.json) retains the actual
factory/native ELF identities and the comparisons. The wind example is saved as
[factory output](jpeg-wind-before-factory.png) and
[previous C output](jpeg-wind-before-native.png).

Factory `0x42011624..0x420116c6` clips IDCT components through a byte lookup table
before YCbCr conversion. `JD_FASTDECODE=1` retains signed component overshoot;
`JD_FASTDECODE=0` selects the matching byte-clipped path in our unchanged decoder
source. This is a reconstruction correction, documented at
`jpeg_decode_unlocked` and `tjpgdcnf.h`.

The literal input callback `0x4200c33e` ignores the flash error return, advances
the cursor and claims all requested bytes. A direct RV32 callback test observes
this behavior after a synthetic SDK error. The native stream rejects the error,
but the previous renderer left partial stripes. Three recorded MCU-stage errors
left 1,411, 57,598 and 57,551 pixels differing from the required cleared rectangle.

`jpeg_decode_unlocked` now clears the known image rectangle after a failed
decompression. Preparation errors and allocation failures preserve the previous
screen. Discard-only validation never draws or clears. This is an intentional
factory correction; error output is checked against an independently constructed
rectangle and patterned guard pixels, rather than literal factory error pixels.

## Error and placement checks

The additional 35 error/validation cases include first/last preparation reads,
first/middle/last MCU reads, successful retries, failed allocation, dimension
mismatch, validation with/without read errors and two truncated stream lengths.
The harness observes actual `jd_decomp` entry to distinguish preparation from
decompression. An early prototype mistakenly expected a clear during preparation;
that ambiguous negative case is excluded from published failure evidence.

Seven placement checks cover the production animation position, a second
translated position, negative coordinates, right/bottom clipping, a completely
offscreen image and clipped error cleanup. Clipped expected pixels are placed
independently from a complete image produced by the actual factory decoder.
Outside pixels must retain their nonzero patterned background. Workspace
ownership and native flash length bounds are checked throughout.

[Current results](jpeg-validation.json) record exact application/source/ELF
hashes. `run-all.ps1` includes this gate; publication requires the complete
107-image set. The per-call instruction deadline is increased for large photos
without claiming a hardware decode speed. These tests do not establish arbitrary
uploaded JPEG compatibility, physical SPI behavior, task concurrency or throughput.
