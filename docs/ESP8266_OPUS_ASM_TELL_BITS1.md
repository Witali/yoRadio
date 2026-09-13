# Opus ASM: tell-inline + чтение одного entropy-бита

2026-09-13. Отдельный эксперимент `bands-tell-bits1-asm`, default не изменён.
Контроль — сохранённый лучший `bands-tell-inline-asm`, не исходный GCC-ASM.

## Изменение и точность

Три вызова `ec_dec_bits(ec, 1)` в `quant_band`/`quant_all_bands` заменены
специализированным GAS-макросом. Если в end_window уже есть бит, нужны только
младший бит, постоянный сдвиг и обновление трёх полей. Исчезают вычисление
маски и переменные сдвиги через SAR. Если окно пустое, вызывается прежняя
GCC-функция с неизменными аргументами/состоянием. Пополнение пакета, нулевые
биты при его исчерпании и остальные вызовы не меняются.

ABI, поля, регистры и ограничения описаны в `bits1_fast.inc.s`.
Контекст читается/пишется только выровненными 32-битными инструкциями.
В первом месте a3 получает N из a12 после проверки N==1; в двух других
a3 явно равен 1. Encoder-пути не изменены. Stack/arena/таблицы не добавлены.
Четыре исходных tell-inline места и C fallback сохранены.

- [x] Reproducible overlay, проверка protected C/GCC hashes и прочих object-секций.
- [x] 100 000 интерпретаций реального макроса: результат, состояние, ABI, cold path.
- [x] Host ASAN/UBSAN: точный PCM 12/24/64/128/192, mixed/PLC/reset/OOM/guards.
- [ ] Linked ELF: статическая RAM, стек, адреса, фактические инструкции.
- [ ] 10 свежих контролей + 10 кандидатов + 10 повторных контролей; все попытки.
- [ ] Решение по результатам и возвращение обычной прошивки через OTA.

Host-модель проверяет математику, а не скорость LX106. Ускорение не заявлено
до физических замеров. Рост/смещение flash-кода может изменить кэш и linker
relaxation; выигрыш нельзя выводить только из количества команд.

## Воспроизведение

```powershell
node tools/esp8266_opus_asm/tell_bits1.cjs <xtensa-lx106-elf-gcc.exe>
node --test tests/esp8266-opus-tell-bits1-asm.test.js tests/esp8266-opus-tell-inline-asm.test.js
node tools/esp8266_opus_asm/check_bands.cjs tell-bits1
```

Сборка через `build_i2s_pdm_production.ps1`, Diagnostic/EnableOpus,
OpusBackend=bands-tell-bits1-asm, OpusWordAsm/OpusIcdfFlashWord/OpusFirFlashWord,
NoSpiffsCache/Pdm32Iram/Pdm32Batch/OpusBenchmark и прежние fixtures.
Только OTA; GPIO3/UART, разметка и SPIFFS не изменяются.
