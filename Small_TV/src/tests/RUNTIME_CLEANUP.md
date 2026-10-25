# Повторный cleanup уже закрытой ВМ

Исправлен дополнительный host cleanup defect из
[неуспешного H10](RUNTIME_MAIN_FAILURE.md). Workload закрывал свою ВМ в `finally`,
после чего supervisor повторно обращался к QMP и записывал connection refused
как новую ошибку cleanup. Исходный HTTP-таймаут этим исправлением не объяснён.

## Проверка исходного процесса

`runtime_cleanup.psm1` читает production session PID, executable и `started_utc`.
Последнее поле записано после `Popen`: это верхняя граница времени создания
исходного процесса, а не его точная creation timestamp. Если процесс с данным
PID создан позднее или имеет другой executable, он не является исходной ВМ.
Отсутствующий или завершившийся исходный процесс тоже не требует QMP cleanup.

При совпадении identity удерживается kernel process handle. Если helper вернул
ошибку, а этот исходный процесс уже завершился, дополнительная cleanup error
не создаётся. Фактический nonzero exit code и stdout/stderr helper сохраняются.
Если исходный процесс жив или identity неизвестна, отказ helper остаётся ошибкой.

Не удалось прочитать identity — это отдельная diagnostic error, но штатный helper
всё равно выполняется. Его прежняя проверка имени ВМ/nonce защищает целевой QMP;
ошибка диагностики не должна оставлять ВМ без попытки cleanup. Старые host-only
fixtures без production identity также используют helper. Новых PID-based kill
операций в cleanup нет.

Поля `vm_cleanup_owner_status` и `vm_cleanup_action` объясняют решение. При
пропуске helper его exit code равен null; успешный код вызова не придумывается.
Исходный workload failure остаётся failure при любом исходе cleanup.

## Проверки окончательной версии

- 13 cases с реальными Windows-процессами: уже закрытый исходный процесс;
  живой процесс при отказе helper; завершение внутри неуспешного helper;
  успешный helper; устаревшее время с живым canary; другой executable;
  legacy metadata; некорректные timestamp/PID; продолжение helper после ошибки
  identity, включая его реальное успешное завершение.
- Все 10 прежних supervisor fault cases прошли. Рабочие дети закрыты, сторонний
  canary сохранён, ошибки записи stdout/stderr/state не прерывают cleanup.
- Реальная ВМ app `c91294fc…` / ELF `9e4ec88d…` на QEMU main executable
  `2df90327…`: намеренная host filesystem error завершила supervisor с failure;
  workload, UART guard и ВМ остановлены проверенными kernel handles. Test-level
  принудительный cleanup не потребовался.
- Повторный вызов cleanup для сохранённой, уже закрытой настоящей H10 session
  выбрал `original-already-exited` / `absent`, не создал cleanup errors и сохранил
  `passed=false`. Сам исторический отчёт H10 не менялся.

Устаревшее время в canary fixture моделирует чужой процесс по сохранённому PID;
настоящий kernel PID reuse не вызывался. Первый тестовый запуск обнаружил
Windows sharing race при чтении только что опубликованного fixture JSON.
Добавлены ограниченное ожидание того же файла и cached identity для cleanup;
оставшийся canary первого запуска отдельно закрыт по проверенному nonce.
Это исправление тестового harness, а не перезапуск ВМ из-за observation timeout.

[Сохранённые отчёты](../../qemu/parity/runtime-cleanup-validation-20261025.json):
четыре gzip, 8314 байт, source pins семи файлов. SHA всех фактических test inputs
повторно проверены при архивировании. Они подтверждают описанные host cleanup
сценарии, не заменяют network/display gates, H10 или аппаратную приёмку.

```powershell
python -B -X utf8 Small_TV/src/tests/runtime_cleanup_test.py --output .build/cleanup-check
python -B -X utf8 Small_TV/src/tests/runtime_supervisor_test.py `
  --dependency-root C:/Work/yoRadio --output .build/cleanup-supervisor-check
python -B -X utf8 Small_TV/src/tests/runtime_supervisor_qemu_test.py `
  --yoradio C:/Work/yoRadio/.worktree/small-tv-timer-bounds `
  --dependency-root C:/Work/yoRadio `
  --qemu-root C:/Work/yoRadio/.worktree/small-tv-jpeg-selectors/.build/jpeg-selector-qemu-complete-20261019 `
  --qemu C:/Work/QEMU-ESP32/.worktree/small-tv-ap-clients/build/main-9135-riscv32.exe `
  --output .build/cleanup-qemu-check
```

Каждая команда требует нового output directory. Использовать указанный в рабочих
заметках Python/PowerShell runtime и не заменять pinned executables живых controls.
Следующий этап реализован отдельно:
[bounded failure-state capture](RUNTIME_FAILURE_CAPTURE.md) сохраняет наблюдения
до cleanup. Воспроизведение и причина исходного HTTP-таймаута ещё открыты.
