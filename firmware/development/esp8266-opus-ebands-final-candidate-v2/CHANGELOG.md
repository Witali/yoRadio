# 2026-09-17 — eBands-final v2

- Три exact signed16 pair-load по 0x40248a05/0x40248a21/0x40248a6c.
- 108 B helper-кода в доказанно decoder-dead областях; третий split 16+20 B.
- 126 изменённых байт, нулевой рост образа, RAM, IRAM и stack frame.
- 397248 числовых случаев, symbolic ABI/bit proof, 24 exact PCM host-сценария.
- v2 исправляет общий изменяемый объект в метаданных генератора; ASM тот же.
- C fallback и production defaults не меняются.
- 30 физических A/B/A2, CPU19277.880896%; оба high-bitrate критерия PASS.
- 25 различных локальных регрессий PASS; все попытки и максимумы сохранены.
- Обычное радио восстановлено OTA, HTTP/WS и сохранность настроек проверены.
