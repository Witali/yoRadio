# Physical ICDF flash-word A/B — 2026-09-09

Source8534cd7,909168-byte diagnostic app. Same effective profile as the
paired OFF build; only ICDF flash-word ON. Application OTA app0→app1 passed.
Two runs, all five PCM fingerprints exact in every run. Host ASan/UBSan
actual flash-word path and independent22-case PCM/scratch checks are also
retained in tools/esp8266_opus_profile/icdf-word-results.json.

| Mode | CPU OFF | CPU ON | Decode time reduction |
|---|---:|---:|---:|
| SILK mono12 |59.183%|58.199%|1.66%|
| Hybrid mono24 |93.085%|91.847%|1.33%|
| CELT stereo64 |75.993%|74.349%|2.16%|
| CELT stereo128 |94.317%|90.030%|4.54%|
| CELT stereo510 |152.575%|150.908%|1.09%|

These are two-run mean raw task budgets on ESP8266, not host timings and
not complete-pipeline CPU use. Each run/mode decodes120 packets producing
115200 mono samples at48kHz. Charged interrupts and small measurement
overhead remain included. Wall-time outliers remain in original reports.

State6582 bytes, scratch peaks1808/2904/5488 and word arena14112/15600
bytes did not increase. Target ICDF stack frame increases16→32 bytes,
but observed audio task lifetime watermark stayed1788/5120 in both profiles.
Binary growth48 bytes. No new static/heap buffers are introduced by ICDF.

This reproducible small improvement is retained as an opt-in switch;
it does not make510kbps realtime or establish uninterrupted full radio.
Use -EnableOpus -OpusWordAsm -OpusIcdfFlashWord for the measured path.
PDM batch has not been physically measured here and remains OFF.
