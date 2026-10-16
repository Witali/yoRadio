# Synthetic JPEG fixtures

These images contain a deterministic arithmetic pattern, without personal
content or private metadata. They cover RGB 4:4:4/4:2:2/4:2:0, restart intervals,
grayscale and dimensions ending inside an MCU. Their manifest pins exact bytes.

The test reads the checked-in JPEGs directly; Pillow is needed only to reproduce
them, using the recorded Pillow 12.3.0/libjpeg-turbo encoder:

```powershell
python Small_TV/src/tools/generate_jpeg_test_fixtures.py
```

`jpeg_inputs_oracle.py` runs real factory/native instructions with these inputs
at the SDK flash-read boundary. Every pixel, including outside-image guards,
is compared. Header/entropy/restart mutations check rejection and error cleanup.
Upload policy, HTTP and FreeRTOS concurrency remain separate tests.
