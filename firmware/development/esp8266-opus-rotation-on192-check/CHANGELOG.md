# LX106 rotation ASM: только проверка сборки, 2026-09-10

Исходникиf37def7, app902400B. Диагностический raw profile12/24/64/128/192,
CPU160/QIO40, rotationASM ON, decoder-onlyCELT OFF, FIR/ICDF/wordON.
Бинарник и полные хеши сохранены. На плату **не загружался**.

Полная сборка/линковка успешна. Локально512 векторов C/model совпали;
это не физическое исполнение assembly. Нужны physical golden PCM и10+10
raw A/B с парным macro-off, затем flash→PDM и непрерывное радио.
Не использовать как production по умолчанию. На плате восстановлено обычное
radio без этого эксперимента. [Контракт](../../../docs/ESP8266_OPUS_ROTATION_ASM.md).
