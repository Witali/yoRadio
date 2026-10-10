# Laboratory firmware only

This image includes an additional short-lived local test CA. Do not use it as
production firmware. Regenerate the CA and rebuild for later TLS record tests;
certificate verification must remain enabled. Private keys are not included.

Full-sized-record memory checks failed. See the
[physical test report](../../../docs/ESP32C3_TLS_RECORD_MEMORY_20261007.md)
and the exact manifest and sdkconfig beside this image.
