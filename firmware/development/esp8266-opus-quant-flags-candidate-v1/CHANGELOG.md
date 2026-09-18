# 2026-09-18: quant flags candidate

Experimental raw benchmark:18 private flag L32I reads replaced by same-width
MOVI at their original addresses. No RAM/stack/app-size growth, no arithmetic
or branch changes.24 exact host PCM/state/sanitizer scenarios pass.
CPU160/QIO40,903216 bytes. Fresh10A/10B/10A2 completed: CPU192
77.869750/77.851083/77.856958%. First speed gate FAIL, repeated PASS;
not adopted as baseline. All30 PCM exact; RAM/stack unchanged.33 local
regressions pass; full raw evidence and ordinary-radio OTA restore saved.
Native OTA only. Not an ordinary playback image or a production default.
See `docs/ESP8266_OPUS_QUANT_FLAGS.md` and saved annotated `patches.s`.
