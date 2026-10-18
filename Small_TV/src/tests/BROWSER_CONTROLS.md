# Настройки в настоящем desktop/mobile браузере

`browser_controls_qemu.py` запускает собственную writable QEMU и
`browser_controls_flow.mjs` в установленном headless Chrome. Ответы и страницы
приходят от настоящего ESP-IDF HTTP server; JavaScript исполняется браузером.
Внешние origin блокируются, данные города/ключа синтетические.

Проверяются viewport1280×900 и390×844, `/settings`, его alias `/`, `/advanced`
и `/photo`. Выбор всех4тем,5GIF и3форматов даты выполняет реальный POST.
Три переключателя последовательно меняют оба значения, сохраняя другие флаги;
неподдерживаемый browser time sync остаётся disabled. Ползунки проверяют дневные
0/100/37%, ночные2/99%, интервалы фото3/60s; палитра сравнивается с независимым
RGB565 ожиданием. Для скрытых CSS checkbox используется настоящий клик по label;
для color/range — реальные DOM input/change handlers, без подмены fetch.

Ночной режим, start18/23 и stop12/5 проверяются в отдельном редакторе. NTP со
спецсимволами должен пережить submit и перезагрузку страницы без нарушения HTML,
затем восстанавливается pool.ntp.org. Поле API key после reload остаётся пустым;
сам синтетический ключ проверяется только в raw record. Город вводится с краевыми
пробелами и сохраняется как Fixture/CN. Поле города предназначено для ввода,
не является отображением текущего города; тест не требует нового поведения UI.
Пять photo switches проверяются масками0/1/17/31 после готовности всех превью.
Кадрирование/upload проверяют отдельные `browser_photo_*` tests.

После каждого reload DOM сравнивается с отдельными публичными GET API. В конце
проверяется соответствие полного набора известному заводскому raw ABI. Cold stop
разрешён только когда настоящий1-byte dirty symbol matching ELF равен0 до и после
чтения raw, а все ожидаемые строки/числа уже записаны. Затем новый процесс QEMU
и новый Chrome повторяют все чтения без POST. Все области flash, кроме NVS и
raw settings sector, включая фото, должны совпасть с началом. Каждый процесс
имеет ровно один ROM boot и не содержит panic; ELF связан с app header.

Аргументы: `--qemu-root`, `--dependency-root`, `--node`, `--playwright-modules`
(папка node_modules), `--browser-executable`, новый `--output`. Используются
существующие локальные зависимости; этот тест ничего не устанавливает. Например:

```powershell
python -X utf8 -B Small_TV/src/tests/browser_controls_qemu.py `
  --qemu-root C:/Work/QEMU-ESP32/.worktree/hostfwd-backlog `
  --dependency-root C:/Work/yoRadio `
  --node C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe `
  --playwright-modules C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules `
  --browser-executable 'C:/Program Files/Google/Chrome/Application/chrome.exe' `
  --output C:/Work/yoRadio/.build/browser-controls-new
```

Для зафиксированного результата использован отдельный47-file frozen QEMU
snapshot из `codex/small-tv-jpeg-headers`; его точные пути и SHA содержатся в
отчёте. Сборка F1ADA8B4/ELF91E26EB2/QEMUD64 прошла281 UI checks и5 storage/source
checks:236 в mutate,45 в cold,96 UI POST. Chrome155.0.8059.80;25наблюдаемых
входов не изменились; console warnings/errors и page exceptions отсутствуют.
См. `../../qemu/parity/browser-controls-validation-20261018.json`.

Это самостоятельная часть H03/H04. Сетевые RF/WPA/captive-portal, успешная
Internet-погода, физическое отключение питания посреди записи, LCD pixels/PWM,
software restart и H10 этим тестом не принимаются. Full/H10 F1 продолжают
исполняться на собственных frozen inputs; новый тест в них задним числом не добавлен.
