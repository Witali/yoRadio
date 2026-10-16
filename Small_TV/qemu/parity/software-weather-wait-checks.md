# Удаление программного ожидания погоды

Пользователь попросил убирать ненужные программные задержки. `clock_task`
ранее выполнял `vTaskDelay(100 ms)` и пропускал отрисовку, пока
`weather_request_active()` сообщал pending/running. Ожидание повторялось до
завершения HTTP, включая его десятисекундный тайм-аут. Оно повторяло блокировку
заводского main вокруг `0x42010864`, хотя в нашей модульной программе HTTP уже
выполняется отдельной задачей.

Этот guard удалён. Погодная задача публикует целый snapshot под mutex, поэтому
активные часы, прокрутка и фото-fade могут продолжать работать до её ответа.
Изменение отмечено `REQUESTED_CHANGE`: это намеренное удаление лишнего ожидания
по запросу пользователя. Обычный 100-ms task yield, периоды таймера, ожидание
завершения записи photo slot и последовательность запуска ST7789 сохраняются.

## Проверки

- Новые platform cases проверяют целые кадры classic/simple/dial при ожидающем
  weather request и все шесть fade actions. На прежнем guard classic case
  воспроизводит устаревший кадр; после изменения проходят все 37 сценариев,
  всего 1,182,490 checks. Это production C с детерминированными SDK adapters.
- Постоянный `tests/weather_wait_qemu.py` удерживает ответ настоящего внешнего
  HTTP-сервиса. В QEMU через аппаратные breakpoints наблюдаются реальные
  simple-renderer entry/return, естественная смена минуты и RGB-кадр. RUNNING
  mask читается из actual ELF DWARF, гостевые RAM/регистры/код не записываются.
- Прежний app `9e4f856a` допускает следующий кадр после завершения/тайм-аута
  погодного запроса: измеренное оставшееся ожидание 6.735 guest s, request state
  уже 0. Кандидат рисует новую минуту за .932 guest s при RUNNING=1 и ещё
  удержанном ответе. Это ожидание ближайшего штатного colon/timer event,
  отдельная искусственная пауза перед рендером не добавляется.
- Приложение/ELF, observer/test/helper bytes и QEMU hashes проверены. Обе ВМ
  закрыты. Первые prototype attempts с неверным RUNNING mask не являются
  доказательством дефекта; постоянный before/after использует compiled enum.

Кандидат: app `a2b6129b`, source `246397dd`, ELF `00ef2763`, 1,176,144 bytes;
в app-разделе свободно 359,856. Сборка сохранена в
`firmware/development/small-tv-esp32c2-reconstructed/`. Точные инструкции —
`native-weather-wait.asm` с manifest. Отдельные результаты:
`weather-wait-before.json`, `weather-wait-candidate.json` и
`weather-wait-platform-candidate.json`.

Пример для worktree с общими установленными зависимостями:

```powershell
& C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe `
  Small_TV/src/tests/weather_wait_qemu.py --dependency-root C:/Work/yoRadio `
  --qemu-root C:/Work/QEMU-ESP32/.worktree/small-tv-wifi-link `
  --output .build/weather-wait-test
```

Реальный QEMU-сценарий охватывает simple theme. Другие темы/fade покрыты здесь
platform cases, а полный актуальный набор ещё требуется. Постоянный test пока
запускается отдельно; следующие шаги — включить его в общий gate и обновить
старое ожидание frozen scroll в `field_qemu.py` под запрошенную отзывчивость.
Старые общие published reports относятся к прежнему app и не подтверждают этот
candidate. Startup wait и другие программные паузы остаются отдельным аудитом.
