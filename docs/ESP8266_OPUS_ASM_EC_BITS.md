# Opus ASM: извлечение low bits через high в ec_dec_bits

2026-09-14. Отдельный frozen-layout кандидат поверх принятого PVQ row-loop.
Лучший raw CPU192 около87.3%, текущая цель80% ещё не достигнута.

## Изменение и точность

Сохранённый GCC ASM строит `(1U<<bits)-1` через MOVI−1/SSL/SLL/XOR/AND.
Одновременно для обновления `end_window` вычисляется `high=window>>bits`.
Кандидат использует `low=window^(high<<bits)`. В общем хвосте
0x40298575..0x40298598 это14→13 инструкций,35→33 исполняемых байта.
Остальные2 байта — недостижимое заполнение после RET, не выполняемые NOP.

Полностью прежние байты вне одного35-byte диапазона, адрес функции/литералов,
refill/EOF, порядок обращений к entropy state, стек и RAM. Leaf call0 ABI:
сохранены return/a1/a12..a15, выход a2 и финальный SAR. Только a5/a9 могут
отличаться как caller-saved scratch. В том числе восстановление SAR учтено
в13 инструкциях: экономия не завышена за счёт изменения контракта.

Документированный `entdec.h` допускает bits0..25; побитовая символьная
проверка покрывает0..31, произвольные32 бита window/state. Это не новый
лимит битрейта. Численная проверка готовых linked инструкций покрывает81120
состояний всей функции,32448 refill и20280 EOF; счётчик nbits_total проверен
с wraparound. C fallback и исходный GCC snapshot неизменны.

## Проверки

- [x] Два образа903216 B, RAM/frame без роста, XOR/SHA SDK image корректны.
- [x]32 символьных shift cases и81120 численных full-function cases точны.
- [x]24 host-сценария exact PCM/guards/reset/OOM/PLC, до510кбит/с,
  фазы/2.5–20мс, составные120мс/48 frames. Host — semantic mirror, не Xtensa.
- [x]63 связанных preflight-регрессии PASS/0skip, включая negative mutations
  операций/порядка памяти/SAR и реальные поля памяти host mono/stereo.
- [ ]10 A/10 B/10 A на плате, без function/stage profiler, вход в RAM.
- [ ] Проверить high-bitrate gate, текущий порог80%, все max/RAM/выбросы.
- [ ] Вернуть обычное радио OTA, проверить HTTP/WS/станцию/плейлист.

Артефакты: `firmware/development/esp8266-opus-ec-bits-{control,candidate}-v1`.
Candidate SHA256 `fa2bf5e6afb71b7184454b738e1027664852b03e13959560732b576f029b317a`.
Профиль CPU160/QIO40, no output/function/stage profiling; default не меняется.
Уменьшение числа инструкций само по себе не считается ускорением.

```powershell
node tools/esp8266_opus_asm/ec_bits.cjs
node tools/esp8266_opus_asm/check_bands.cjs ec-bits
node --test tests/esp8266-opus-ec-bits.test.js
```
