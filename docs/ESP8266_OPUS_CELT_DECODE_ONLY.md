# ESP8266: CELT bands decoder-only A/B

2026-09-10. Эксперимент A4 из плана ускорения. Флаг
`-OpusCeltDecodeOnly` / `YORADIO_OPUS_CELT_DECODE_ONLY`, по умолчанию OFF.
Это специализация существующего fixed-point алгоритма, не другой декодер.

## Изменение и контракт

`quant_all_bands()` всегда вызывается декодером с encode=0. Пять внутренних
путей bands раньше читали encode из context, включая рекурсивную функцию.
Флаг делает это значение константой на этапе компиляции без LTO. Вызов с
encode!=0 отклоняется через ec.error до обращения к mode/bands/scratch.
Общий upstream-путь сохраняется при выключенном флаге и без bounded.
Entropy, stereo, rounding, PLC и качество не упрощаются.

## Проверки до физического A/B

- 27 PCM-сценариев exact: пять режимов/битрейтов, смешанные SILK mono/stereo,
  Hybrid/CELT/PLC/reset, десять фазовых фикстур 2.5/5/10/20ms, одиннадцать
  составных пакетов до120ms. Проверены OOM/reinit, отмена callback и изменение
  содержимого выдаваемого PCM. Полного покрытия всех FEC/DTX/malformed нет.
- Scratch не вырос: в смешанном пути5968B DRAM /15600B word arena.
  Временный PCM остаётся1920B. Host ABI не равен ABI LX106.
- ASan/UBSan проверяет ранний отказ encoder-вызова и пять полных PCM-фикстур
  с инструментированным bands.c. Это не sanitizer-проверка всего декодера.
- XtensaGCC8.4: macro-off инструкции и relocation targets совпадают с прежними
  после нормализации только числовых ID локальных символов GCC. Это не
  сравнение ELF целиком. В macro-on из bands исчезли encoder-вызовы; alg_quant
  больше не присутствует в linked ELF.
- Flash text −5892B, rodata −4B; DRAM data/BSS, IRAM text/BSS без изменений.
  Stack frames **не все уменьшились**: quant_partition112→144B,
  quant_all_bands384→400B, quant_band128→112B; появился отдельный
  compute_theta80B. Итоговый high-water stack проверяется на плате.

```powershell
node tools/esp8266_opus_profile/run_celt_decode_regressions.cjs
node --test tests/esp8266-opus-celt-decode-only.test.js tests/esp8266-opus-raw-comparison.test.js
node tools/esp8266_opus_profile/audit_celt_decode.cjs
```

[PCM](../tools/esp8266_opus_profile/celt-decode-results.json),
[assembler/RAM/stack](../tools/esp8266_opus_profile/celt-decode-target-results.json).

## Решение

До повторного A/B на физической плате ускорение не подтверждено. Требуются
не менее десяти попыток OFF/ON, одинаковые CPU160/QIO40, FIR/ICDF/word flags,
poll interval и raw corpus. Сохраняются ошибки/OOM/медленные выбросы.
Raw CPU не доказывает отсутствие пропусков I2S или сетевого радио.
