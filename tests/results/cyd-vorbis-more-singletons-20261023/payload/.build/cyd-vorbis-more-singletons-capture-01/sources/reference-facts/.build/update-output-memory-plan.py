from pathlib import Path

path=Path('docs/ESP32_CYD_C3_TRANSFER_PLAN.md')
raw=path.read_bytes()
newline=b'\r\n' if b'\r\n' in raw else b'\n'
body=raw.decode('utf-8').replace('\r\n','\n')
for stage in ('05','06','09','10'):
    old='| CYD-C3-'+stage+' | В работе |'
    assert body.count(old)==1,stage
    body=body.replace(old,'| CYD-C3-'+stage+' | Программная часть выполнена |',1)
old='| CYD-C3-13 | Открыт | TLS/heap/IRAM/stack политика после измерений CYD. Full-record TLS, раннее освобождение старого codec, сохранение сетевого headroom. |'
new='| CYD-C3-13 | В работе | [Освобождение GET TX-буфера](CYD_MEMORY_TRANSFER_DESIGN.md) подключено через проверяемый build-local overlay SDK6.0.2. Host SDK17/8, actual open_stream62/6, CMake9 и whole Xtensa compile проходят. Число 4096 — configured capacity, не измеренная экономия heap. Idle-pool reclaim, TLS reserve/MPI, IRAM/stack и физические измерения CYD остаются. |'
assert body.count(old)==1
body=body.replace(old,new,1)
old='Backend DMA telemetry и физические измерения отдельно.'
new='[Backend telemetry](CYD_OUTPUT_TELEMETRY_DESIGN.md) подключена ко всем трём выходам и HTTP: SMP-счётчики16/7, backend22/8 и bounded JSON2000/2304 проходят; quiet без timer calls, целевые IRAM/DRAM helper objects проверены. Физические CPU/heap/stack/IRQ/DMA измерения отдельно.'
assert body.count(old)==1
body=body.replace(old,new,1)
old='actual CYD task lifecycle, OOM/target controls, watchdog/ресурсы и физический vendor/custom A/B остаются.'
new='[Actual CYD task QEMU](../tests/results/cyd-flac-task-qemu-20261020/README.md) проходит три public-API случая: ordered EOF/exact PCM, Stop/reopen и three-owner maintenance/resume; пять реальных decoder/client cleanup, исходные cores/priorities/stacks. OOM/backpressure/target semantic controls, production watchdog/ресурсы и физический vendor/custom A/B остаются.'
assert body.count(old)==1
body=body.replace(old,new,1)
anchor='## Карта функций и мест в коде\n'
section='''## Что осталось по переносу

- **Этап 13, память:** lifetime-safe reclaim входного пула, TLS reserve/MPI и
  подбор heap/IRAM/стеков по CYD. Освобождение HTTP GET TX уже реализовано;
  физический выигрыш ещё не измерен.
- **Этап 14, AAC/Vorbis:** аудит и адаптация Xtensa ABI, compact owners/repair,
  OOM и сравнение PCM. Ранее остановленный автоматической проверкой пункт
  AAC private owner-view остаётся отложенным; ограничение не обходилось.
- **Этап 12, FLAC:** дополнительные target OOM/backpressure/semantic controls
  после прошедших трёх actual-task QEMU случаев; физический vendor/custom A/B.
- **Этапы 00/05/15, аппаратура:** единая проверка сети HTTP/HTTPS, WebUI/OTA,
  DMA/IRQ, CPU/heap/stack, watchdog и длительного воспроизведения каждого выхода.

Дисплей, распиновка, USB/reset и другие специфичные функции C3 исключены.
Stream остаётся на core0, decode/output на core1 с прежними приоритетами и
стеками. Программная телеметрия завершена; аппаратные измерения ещё впереди.

'''
assert body.count(anchor)==1 and '## Что осталось по переносу' not in body
body=body.replace(anchor,section+anchor,1)
body+='''
- 2026-10-20, CYD-C3-05/12/13: подключены счётчики трёх output backend и
  completion-queue drop PDM, bounded HTTP snapshot и освобождение завершённого
  GET TX-буфера через hash-guarded IDF6.0.2 overlay. Host/ASan/UBSan и независимое
  ревью проходят; полный Clang53 сохраняет 86 warnings/0errors. Actual full-TU
  FLAC QEMU проходит три случая с реальными SDK owners и прежней affinity;
  OOM/backpressure и физическая квалификация остаются открыты.
'''
path.write_bytes(body.encode('utf-8').replace(b'\n',newline))

path=Path('docs/CYD_FLAC_TRANSFER_DESIGN.md')
raw=path.read_bytes();newline=b'\r\n' if b'\r\n' in raw else b'\n'
body=raw.decode('utf-8').replace('\r\n','\n')
start=body.index('6. **Actual CYD task target gate open:**')
end=body.index('7. **Physical qualification open:**',start)
body=body[:start]+'''6. **First actual CYD task target checkpoint complete:**
   [frozen SDK/QEMU evidence](../tests/results/cyd-flac-task-qemu-20261020/README.md)
   executes unchanged complete `audio_service.c` through public startup/play/
   stop/maintenance APIs with all three real SDK owners and original profiles.
   Three cases pass ordered EOF/PCM identity, Stop/reopen and maintenance/resume;
   five actual decoder and HTTP-client instances are cleaned up. Transport and
   output hardware are explicit seams, and request-TX release is disabled because
   that transport does not enter SDK response state. No private phase/ACK writes
   simulate cleanup. Backpressure/errors, scoped OOM and deliberate target
   semantic controls remain open, as do production watchdog/resource margins.
'''+body[end:]
path.write_bytes(body.encode('utf-8').replace(b'\n',newline))
