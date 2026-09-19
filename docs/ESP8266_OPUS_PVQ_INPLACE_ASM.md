# Opus ASM: PVQ напрямую в X, без iy[], B=1

2026-09-19. Независимый эксперимент над принятой `ebands-final` цепочкой.
N4 lookup и short-leaf сюда не входят. Production default пока не изменён.

## Изменение

При `B==1 && 0<K<=32767` импульсы записываются непосредственно в int16 X,
затем нормализуются на месте. Каждый элемент читается до перезаписи. Маска
collapse равна 1, в том числе при gain=0. Для других B/K — прежний путь.
Никакого ограничения битрейта не добавлено.

Генератор клонирует **принятые linked-инструкции**, не перекомпилирует весь C
и не теряет предыдущие оптимизации поиска. Меняются пять stores импульсов,
stride и итоговое смещение X; адресация U-таблиц остаётся 32-битной.
В normalise меняются только ширина load и stride. Inline rotation сохранена.
На fast path убраны mark/alloc/restore; оставшиеся callees не используют арену.
Никаких halfword accesses в word-only IRAM: X уже был int16 DRAM-массивом.

Clone/literals занимают 1676 из 1788 B доказанно недостижимого для декодера
encoder-кода `alg_quant`. Отдельный guard помещён в другой проверенный dead
участок. В исходном alg_unquant заменена только первая 3-байтная инструкция
переходом; fallback выполняет перемещённый пролог и исходное продолжение.
Адреса всех остальных функций и размеры секций не меняются. Положение самих
двух клонированных функций меняется: влияние instruction cache включает A/B/A.

Frame alg_unquant/decode_pulses остаётся 112/48 B. Дополнительного wrapper
frame нет. Пиковые byte/word arena на корпусе прежние: максимум формирует
synthesis, а не iy[]. Уменьшать общую арену по этому результату нельзя.

## Проверки перед платой

- [x] 653 linked-инструкции сопоставлены с точными разрешёнными изменениями.
- [x] 80 граничных B/K: guard, fallback, регистры, отсутствие нового stack frame.
- [x] 83951 вектор через интерпретатор реальных LX106-инструкций: точные
  импульсы, энергия, entropy-call arguments, callee-saved и границы writes.
- [x] 2625 normalisation случаев: signed int16, gain=0, граничные значения.
  Вызов rsqrt моделируется одинаковым результатом и clobbers; это не замена
  полного PCM-теста и не измерение процессорного времени.
- [x] 24 полных host PCM/state/ASan/UBSan сценария, включая 320/510 кбит/с,
  120 ms, 48 packed frames, reset/PLC/OOM/mixed. PCM побитово совпал.
- [x] 14 новых и связанных регрессий, включая отрицательные mutation tests.
- [ ] 10A/10B/10A2, проверка PCM на самой плате, RAM/stack и выбросов.
- [ ] После положительного raw speed gate — отдельно ordinary I2S/WebUI.

Прямой host cwrsi проверяет также K=32767 как границу представления int16.
Это не допустимый индекс конечной U-таблицы public decode_pulses; ISA-тест
этого API использует только представленные в таблице N/K. Guard отдельно
проверен на 32767/32768. Нельзя выдавать недопустимый индекс за valid packet.

## Воспроизведение

```text
node tools/esp8266_opus_asm/check_algorithm_candidates.cjs inplace-b1
node tools/esp8266_opus_asm/pvq_inplace_b1.cjs
node --test tests/esp8266-opus-inplace-asm.test.js tests/esp8266-opus-algorithm-candidates.test.js
node tools/esp8266_opus_asm/pvq_inplace_b1.cjs --publish
node tools/esp8266_opus_asm/pvq_inplace_b1.cjs --verify
```

`--publish` повторно проверяет всю родительскую цепочку до сохранения app.bin
в `firmware/development/esp8266-opus-pvq-inplace-b1-{control,candidate}-v1/`.
Это raw-профиль CPU160/runtime QIO40, без вывода и function/stage profiling.
Загрузка только OTA. Для каждой из трёх серий `run_raw_series.ps1`: 10 попыток,
15s polling, явный fixtures manifest `esp8266-opus-board-through192`.
Итоговый `report_pvq_inplace_b1.cjs` требует завершения всех 30 попыток,
проверяет PCM/RAM, архивирует все результаты и не исключает выбросы.
