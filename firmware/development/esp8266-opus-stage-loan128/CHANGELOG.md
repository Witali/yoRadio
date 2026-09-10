# Opus 128-word publication experiment, 2026-09-10

Source 7666cc8; 884912 bytes. ICDF/WordASM/PDM32 IRAM/batch ON,
Pdm32LoanWords128. The physical buffers remain 2x512 words. CPU160/QIO40,
GPIO3, standard I2S PDM32, mono PCM48k, input1024, scratch6144.
OTA to app1 0x110000 succeeded. No SPIFFS or saved playlist upload.

Exact host PCM/PDM/ownership tests passed. The ISR and RAM sections are
unchanged; flash +48 bytes. Four physical intervals FAILED with TCP/reconnect,
missing HTTP samples, and later post-init reserve failure. These data do not
qualify the shortened publication limit. It stays diagnostic-only; default512.

Final state: saved station284 restored and stopped; temporary servers stopped.
This is not a production release or a claim that Opus continuity is fixed.

[Full method, limitations and next checks](../../../docs/ESP8266_OPUS_LIVE_STAGE_PROFILE.md).
