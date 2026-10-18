# Аудит WebSocket RFC 6455: CYD и C3

Дата проверки: 2026-10-18. Полное соответствие RFC **не подтверждено**.
Этот документ фиксирует исходные SDK и покрытие project overlay; интеграция
семантики сообщений и проверки всего сервера выполняются отдельно.

Нормативный источник: [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455.html).
Приведённая ниже матрица разделяет обязательные требования, рекомендации и
разрешённые варианты. Она относится к серверной стороне WebUI; собственный
клиент радиопотока использует другие протоколы.

## Проверенные исходники

Локальные SDK прочитаны без изменения:

| Назначение | Корень SDK | Основные места |
| --- | --- | --- |
| CYD | `C:/Work/yoRadio/.idf/v6.0.2` | `components/esp_http_server/src/httpd_ws.c:102`, `:269`, `:463`; `httpd_parse.c:89`, `:377`, `:728`, `:796`; `httpd_uri.c:337` |
| C3 | `C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6` | `components/esp_http_server/src/httpd_ws.c:130`, `:377`, `:429`, `:694`; `httpd_parse.c:419`, `:762`; `Kconfig:53` |
| Общий HTTP parser | Каждый соответствующий SDK | `components/http_parser/http_parser.c`, установка `parser->upgrade` из `F_UPGRADE` и `F_CONNECTION_UPGRADE` |

Проверяемые SHA256 двух C-файлов и public/private заголовков сохранены в
[apply.py](../idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455/apply.py).
Генератор прекращает работу при любом несовпадении. Сведения о сгенерированных
файлах записываются в `native-httpd-rfc6455/manifest.json` каталога сборки.

## Матрица требований и наблюдений

Обозначение «overlay» означает наличие реализации и ограниченных host-проверок;
оно не означает успешный полный сетевой прогон. Для SDK 6.1 нужен
`CONFIG_HTTPD_WS_STRICTER_RFC6455=y`: сам SDK по умолчанию оставляет его выключенным.

| RFC | Уровень и требование | CYD SDK 6.0.2 без overlay | C3 SDK 6.1 strict без overlay | Overlay / оставшаяся работа |
| --- | --- | --- | --- | --- |
| 4.2.1 | MUST: GET, HTTP ≥1.1 | URI GET; parser допускает HTTP/1.0 | Отдельный HTTP/1.1 gate | GET и HTTP/1.1 gate до потери request-line; whole parser wire cases прошли |
| 4.2.1 | MUST: Host, Upgrade, Connection | Host не проверяется; Upgrade сравнивается целиком | Host непустой; Upgrade сравнивается целиком | Host уникальный, authority проверяет SDK URL parser; Upgrade/Connection имеют проверяемый list grammar |
| 4.2.1, 11.3 | MUST: key/version, одиночность | Key только читается; версия `13` | Base64 nonce 16 проверяется; дубликаты не считаются | Уникальные Host/key/version; OWS/LWS; nonce 16; version syntax 0..255 без leading zeros; 426 с `Sec-WebSocket-Version: 13` для другой корректной версии |
| 4.2.2 | MUST: корректный Accept | SHA-1 + Base64 | SHA-1 + Base64 | Нормализованное значение key; exact-send проверка. Host SHA seam проверяет вход и digest RFC-примера, сам SHA SDK не тестирует |
| HTTP framing | Сохранение Content-Length bounds | Narrowing к int при проверке sentinel | Есть uint32 bound | C3 guard сохранён, CYD получил тот же bound; пустое присутствующее поле в обоих SDK теперь даёт 400 |
| 4.2.1, 4.3 | MUST: синтаксис subprotocol | `strtok_r`, фиксированные 50 байт | То же | Проверяется весь offer list, включая повторные headers, case-sensitive уникальность, token syntax; выбор остаётся `NULL` |
| 9.1 | MUST: синтаксис extensions | Синтаксис предложений не проверяется | То же | Проверяются extension tokens/params, quoted-string unescaping в token, repeated headers и folded LWS; malformed offers дают HTTP 400 |
| 4.2.2, 9 | MAY: отказаться от расширений | Расширения не выбираются | То же | Предложения проверяются, расширения не согласовываются; ответ не содержит `Sec-WebSocket-Extensions` |
| 4.2.2 | MAY: выбрать ноль subprotocol | Возможно `NULL` | То же | Допустимо после проверки предложения; нельзя выдавать несогласованное имя |
| 5.1–5.3 | MUST: MASK по направлению | Клиент без маски отклоняется без protocol Close | Strict посылает 1002 | CYD 1002; серверные кадры без маски |
| 5.2 | MUST: RSV/opcode | Проверок нет | Strict whitelist/RSV | Добавлены CYD проверки до приложения |
| 5.2 | MUST: минимальная длина, MSB=0 | Нет; возможна потеря старших бит на 32-bit target | Strict проверки | CYD проверки до приведения к size_t; слишком большой размер 1009 |
| 5.2 | MUST: минимальный исходящий размер | Для 65535 выбирается 64-bit encoding | Граница исправлена | CYD `<= UINT16_MAX`; host проверяет 125/126/65535/65536 |
| 5.5 | MUST: FIN и ≤125 у control | FIN не проверяется, граница parser допускает 126 | Strict проверки | Добавлены CYD проверки |
| 5.4 | MUST: fragments, последовательность | SDK отдаёт отдельные кадры; прежний WebUI отвергает `!final` | То же ограничение WebUI | Требуется общий semantic core и интеграция, включая control между fragments |
| 5.5.2–3 | MUST/MAY: Pong и unsolicited Pong | SDK автоответ Ping; Pong передаёт handler | То же | Для общего core нужен `handle_ws_control_frames=true`, bounded control buffer, соответствующий payload |
| 5.6, 8.1 | MUST: UTF-8 | SDK не проверяет текст | SDK strict тоже не проверяет | Semantic core: входной UTF-8 между fragments; отдельно проверить исходящие station/title JSON |
| 5.5.1, 7.4 | MUST: Close payload/status | Автоматический пустой Close без проверки payload | То же | Semantic core: длина 0 или ≥2, код, UTF-8 reason; integration gate ещё нужен |
| 5.5.1 | SHOULD: отражать Close status | SDK ответ теряет status/reason | То же | Общий core должен формировать ответ после проверки |
| 5.5.1 | MUST: прекратить data после Close | Отдельного send gate нет | Strict блокирует non-Close | CYD send gate добавлен; сервис должен допустить принадлежащий ему Close до освобождения session |
| 5.5.1, 7.1.1 | MUST: завершение TCP | Cleanup ставит callback с `sock_db*` в очередь | То же | Cleanup не ставит callback; `req_delete` возвращает ошибку в текущий owning loop для удаления той же session |
| 7.1.7 | SHOULD/MAY: Close при ошибке | Обычно только обрыв | Strict 1002/1009 | CYD protocol Close; не продолжать разбор после ошибки; transport failure ограничен deadline |
| 10.4, 7.4.1 | MAY: лимиты, 1009 | Лимит приложения 96 байт | Прежний лимит 255 байт | Лимиты допустимы; применять к полному сообщению, включая fragments, и документировать выбранные значения |
| 10.6 | MUST/SHOULD: TLS support/use | Исходный WebUI использует plain WS | То же | WSS реализуется и квалифицируется отдельно, см. [TLS plan](WEBSOCKET_TLS_PLAN.md); TLS клиента радиостанций это требование не закрывает |

Для строк с общей семантикой сообщения окончательным доказательством являются
сами интегрированные C3/CYD handlers и их результаты. Этот audit не подменяет
их будущими намерениями.

## Архитектура overlay

[enable.cmake](../idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455/enable.cmake)
вызывается после регистрации main component. Он получает `esp_http_server`
target и заменяет только `httpd_ws.c` и `httpd_parse.c` сгенерированными копиями
в каталоге сборки. Остальные SDK файлы и исходные notices Apache-2.0 сохраняются.
Для компиляции используются private заголовки **того же** SDK target. Копии
структур, private offsets, RISC-V assembler или перенос C3 task affinity не нужны.

На 6.0.2 перенесены проверки frame headers из более нового варианта с сохранением
старого API целого кадра. На 6.1 остаются его strict checks, добавлены общие
handshake проверки и безопасное завершение session. Неизвестный SDK нельзя
автоматически считать совместимым: сначала требуется проверить diff и обновить
четыре source/header hashes отдельным изменением.

Обычные public pre/post-handshake callbacks есть в обоих SDK. Они подходят для
проверки прикладной политики и установки transport overrides. Первоначальная
HTTP version в `httpd_req_t` не представлена. `httpd_get_raw_req_data()` существует,
но к моменту pre-handshake request-line уже отброшена, а CRLF в headers заменены
NUL. Его реализация копирует ровно переданный `buf_len`, не ограничивая его
размером scratch. Поэтому вместо восстановления недокументированного raw формата
overlay выполняет version gate непосредственно в matching parser.

Новая проверка mandatory headers использует настоящие `req_hdrs_count`,
`scratch_cur_size` и ограниченный поиск NUL в этом matching private API.
Постоянные lookup buffers: Host 256, version 4, key 25 и nonce 16 байт; heap
в helper не выделяется. Authority Host разбирает matching SDK URL parser;
временный URL buffer 264 байта. C3 больше не выделяет raw-header-sized version/key
buffers: нормализованный key используется один раз. Сохраняется SDK calloc для
61-байтного SHA input и его исходные error cleanup paths.

Синтаксис optional offers проверяется целиком в исходном header storage.
Уникальность subprotocol сравнивается между всеми предложенными значениями,
включая повторные строки, без request-sized массива токенов. Алгоритм ограничен
настроенным HTTP header limit; повторные сравнения имеют квадратичную верхнюю
границу по этому лимиту. Extension-specific параметры не применяются, поскольку
ни одно расширение не выбирается. Валидный длинный offer не обрезается до
старого 50-байтного буфера при проверке синтаксиса.

Whole parser тест воспроизвёл ещё один дефект обоих SDK: `cb_header_value`
суммировал callback lengths, в которые не входил folded CRLF. Следующая установка
NUL затирала последние два байта значения. Overlay сохраняет физический span
между callback pointers. Валидный folded extension parameter и обычный folded
HTTP header теперь сохраняются при любом проверенном receive split.

Новые whole-parser случаи подтвердили ошибку пустого `Content-Length:` на обоих
SDK: parser устанавливает `F_CONTENTLENGTH`, но оставляет `content_length`
равным sentinel отсутствующего поля. HTTPD мог принять upgrade. Overlay отличает
эти состояния и возвращает 400. Кроме того, existing C3 `> UINT32_MAX` body bound
сохранён; CYD получил такой же guard до narrowing. Проверены отрицательные,
malformed и повторные lengths, отказ 413 для `4294967296`, сохранение значений
`0`, `1`, `2147483648`, `4294967295` у обычного HTTP handler без выделения
памяти под объявленный body.

Ошибка cleanup воспроизводится без сети: исходный `httpd_req_cleanup` ставит
callback с указателем на session в очередь, затем owning loop может удалить
этот слот по `ESP_FAIL`. После повторного использования слота настоящий SDK
`httpd_sess_close` видит новые `lru_counter` и `handle` и удаляет новую session.
Overlay не ставит этот callback. Ошибочный кадр уже возвращает `ESP_FAIL`;
обычный Close получает тот же результат из `httpd_req_delete` после cleanup.

## Выполненные проверки и границы доказательства

Команда из корня worktree, Python Windows запускает GCC в WSL:

```powershell
python idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455/test_host.py `
  --sdk C:/Work/yoRadio/.idf/v6.0.2 --output .build/rfc6455-http-length-cyd-fixed
python idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455/test_host.py `
  --sdk C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6 --output .build/rfc6455-http-length-c3-fixed
```

Для каждого SDK прошли 623 ASan/UBSan checks реальных сгенерированных SDK
handshake/recv/send/get-frame-type/cleanup/delete функций. Вариант с target
`SIZE_MAX=UINT32_MAX` добавляет проверку отказа для `0x100000000` до приведения
длины: 624 checks. Этот вариант моделирует только size cap, а не 32-bit ABI.

Далее прошли **14 332 receive split checks** через настоящий SDK `http_parser.c`
и весь сгенерированный `httpd_parse` pipeline: callbacks, URL parsing,
`read_block`, `parse_block`, pause/unpause. Исполняются реальные SDK
`recv_pending`, `recv_with_opt`, `unrecv`. Проверяются GET/version, mandatory
headers, OWS/folding, optional offers, граница 1024-байтных headers, обычный
HTTP/1.0 вне upgrade, Content-Length границы и первый masked Ping, пришедший
вместе с upgrade.

Четыре отрицательных контроля компилируют исходные SDK parser/WS функции:
выявлены принятие malformed extension, duplicate protocol offer, порча folded
value и принятие пустого Content-Length.
Отдельный настоящий SDK close callback/trigger test воспроизводит удаление
повторно использованного session slot на исходнике; overlay сохраняет новую
session. Exact source/generated hashes и результаты хранятся в `report.json`
каталогов двух приведённых команд.

Host harness использует модель полей HTTPD structs и seam byte stream. Это
не проверка target ABI. Base64 C взят из соответствующего SDK; его constant-time
primitive в host seam заменён обычным диапазонным выражением. SHA seam проверяет
точный hash input RFC-примера и возвращает его известный digest. HTTP parser
работает на настоящих входных байтах; socket receive и dispatch единственного
`/ws` route остаются seams. Настоящие sockets, TCP timing, target ABI/stacks,
SDK crypto SHA operation и TLS этим прогоном не проверяются.

## Следующая квалификация

1. Скомпилировать оба actual HTTPD targets со сгенерированными файлами и matching
   private headers. Проверить compile commands и manifests, чтобы старые C-файлы
   не остались одновременно в target.
2. Интегрировать общий semantic core в оба handlers с включённой передачей
   control frames. Покрыть fragments, UTF-8, Close и входные лимиты. Сохранить
   существующие привязки audio tasks CYD к ядрам.
3. Повторить подтверждённую host HTTP handshake matrix на реальном HTTPD server:
   сетевые receive boundaries, lifetime callbacks и поведение ошибок должны
   совпасть с исполняемым SDK parser и корректным HTTP response.
4. Создать host/target echo test endpoint, который вызывает **тот же** production
   protocol path, и прогнать независимый
   [Autobahn Testsuite](https://github.com/crossbario/autobahn-testsuite).
   Прикладной `/ws` дополнительно проверить с его message limits и командами;
   echo-only pass не доказывает корректность команд или жизненного цикла WebUI.
5. Проверить short I/O, partial handshakes/frames, Pong между fragments,
   одновременный Close, STOP/teardown, повторное использование fd/session и
   продолжение playback при медленном клиенте. Для WSS добавить TLS handshake,
   heap/stack измерения и управление сертификатом.
6. Сохранить внешние отчёты вместе с версиями инструментов и source hashes.
   Каждое исключение соотнести с конкретным разрешённым лимитом или отсутствующим
   согласованным расширением; обязательный тест нельзя скрыть как optional.

Read-only inventory зависимостей: в Windows SDK Python 6.0.2/6.1 установлен
`websockets`, но нет `autobahn`, `twisted`, `wsproto`, `pytest`. В основном bundled
Python этих модулей нет. WSL `/usr/bin/python3` имеет Twisted 24.3.0 и GCC,
но `autobahn`, `wstest`, `pip3`, Docker и `websockets` не найдены. Установка
пакетов и внешний conformance run в рамках этого audit не выполнялись.
