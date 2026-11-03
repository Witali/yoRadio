# Ordinary FLAC task diagnostic

This NEW diagnostic retains the complete original130-fixture encoded/oracle
container and unchanged T0/T1/T2 lifecycle/PCM assertions from
../cyd_flac_task_qemu. It compiles current committed whole production
audio/state/health/registration TUs and shared FLAC on pinned SDK6.0.2/classic
ESP32. The [recorded qualification](../../results/cyd-flac-ordinary-task-20261103/README.md)
passes the three original lifecycle cases and382 complete positive iterations
over15033371 SDK timer microseconds. Its finite scope and output seams are
documented with the results.

The extra positive phase repeats the complete original
flac-24bit-mid-verbatim-block8192 through public Play/EOF/cleanup. It ends after
the first complete iteration reaching15000000 SDK timer microseconds, with a
90000000-microsecond whole-phase deadline fixed before entry. It adds no sleep,
yield or idle feed; the original lifecycle wait loops still wait one tick.
Every iteration byte-compares complete PCM and records actual SHA256, owner
counts, decoder calls, heap/stack snapshots and real idle subscriptions.

Original task profiles stay stream/core0/priority3/6144B, decoder/core1/priority5/
16384B and output/core1/priority6/4096B. Production watchdog/heap policy is TWDT5s/
no-panic, both idle owners, interrupt300ms including CPU1, quiet heap and optional
diagnostics off. The reader rejects real watchdog warnings without requiring
panic/reset. Historical static-RX custom-FLAC/PDM receipt supplies exact
watchdog/heap provenance; current committed Kconfig supplies Ogg/AAC selectors.

Real SDK calls own HTTP client allocation/cleanup, tasks, queues/rings and codec
heap. HTTP open/header/read and immediate public output/LED calls remain explicit
seams. Public gain/layout setters assert legacy mono/stereo and zero gain in
configure/layout/gain/write order. Native physical output/DMA, Wi-Fi/TFT and
analog output do not execute. Request-TX release is off because the synthetic
transport never enters SDK response state. No native OOM, deliberate queue
backpressure or target semantic-fault controls are added.

Each fresh launch requires current committed source inputs and the documented
storage/configuration prerequisites. The
controller is tests/run-cyd-flac-ordinary-task-qemu.py --output .build/NEW, with
explicit installed SDK/QEMU/ROM paths as necessary. --ordinary-host-report and
--legacy-host-report bind fresh unchanged HOST results and all their current
source hashes. Committed Git blob checks reject changed production inputs;
actual compiler dependencies, sources/config/tools/images are frozen and
rechecked through terminal execution. All original captures remain untouched.

The dedicated4MiB test image must not be flashed as firmware. SDK/QEMU software
observations do not establish full-radio memory margins, physical timing,
throughput, universal starvation absence or sound quality. Focused Python reader
controls model logs only; they do not execute codecs or target semantic faults.
