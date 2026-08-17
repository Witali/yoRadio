# Сборщик потоков для yoRadio

Скрипт `radio_stream_collector.py` получает прямые аудиопотоки с публичных страниц:

- Radio Record;
- 101.ru;
- Zaycev.FM;
- Relax FM;
- Radio Caprice (RADCAP).

Он извлекает URL из HTML, JSON и JavaScript, применяет шаблоны каналов Radio Record, 101.ru и Zaycev.FM, при необходимости дополняет результат через Radio Browser и проверяет каждый поток коротким потоковым GET-запросом.

## Установка

На Windows из каталога сборщика:

```powershell
.\setup.ps1
& ..\..\.build\radio-stream-collector-venv\Scripts\python.exe .\radio_stream_collector.py --verify -v
```

На Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-radio-streams.txt
```

## Основной запуск

```bash
python radio_stream_collector.py --verify -v
```

Результаты появятся в каталоге `radio_output`:

- `playlist.csv` — готовый табличный плейлист yoRadio;
- `playlist.m3u` — проверка в VLC;
- `streams.json` — полный структурированный результат;
- `streams_report.csv` — таблица проверки, включая ошибки.

## Отдельные сайты

```bash
python radio_stream_collector.py --sites record,zaycev --verify -v
python radio_stream_collector.py --sites 101 --max-101-channels 100 --verify -v
python radio_stream_collector.py --sites relax,caprice --verify -v
```

## Экономичный вариант для ESP32

```bash
python radio_stream_collector.py --quality low --verify -v
```

Для 101.ru сначала проверяется AAC 64 кбит/с; для Zaycev.FM и Radio Record варианты качества также перебираются от меньшего к большему.

## Только данные сайтов, без Radio Browser

```bash
python radio_stream_collector.py --no-radio-browser --verify -v
```

## Ускоренная проверка

```bash
python radio_stream_collector.py \
  --concurrency 20 \
  --timeout 8 \
  --probe-bytes 16384 \
  --verify -v
```

Слишком высокая параллельность может создавать лишнюю нагрузку на сайты. Значение 8–20 обычно разумно.

## Выгрузить и непроверенные ссылки

По умолчанию в `playlist.csv` и `playlist.m3u` попадают только работающие потоки. Полный отчёт всё равно содержит неудачные попытки. Чтобы включить их в плейлисты:

```bash
python radio_stream_collector.py --include-unverified
```

## Самопроверка без Интернета

```bash
python radio_stream_collector.py --self-test
```

## Формат yoRadio

`playlist.csv` не является обычным CSV с запятыми. Каждая строка имеет вид:

```text
Название<TAB>URL<TAB>0
```

Последнее поле — поправка громкости `ovol`.

## Ограничения

Сайты могут менять HTML, JavaScript, внутренние API и адреса серверов. Поэтому сборщик сочетает несколько методов и всегда проверяет конечный URL. Скрипт не обходит CAPTCHA, авторизацию, географические ограничения и DRM.
