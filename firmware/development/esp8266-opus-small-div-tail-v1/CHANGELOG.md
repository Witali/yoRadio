# Experimental late-flash exact division — 2026-09-14

CPU160/QIO40, 16KiB cache, bands-small-div-tail-asm, raw RAM benchmark.
Unchanged exact114B LX106 helper and516B reciprocal table relocated to late
.irom1.text. Three rng/ft sites; original val/ext and C/GCC fallback preserved.
App903872 B (+656 vs fresh tell-inline control), no static RAM/stack growth.
Hot functions retain their sizes but shift4 B: not perfect layout isolation.

27 targeted regressions and host PCM/ASan/UBSan through510kbps pass.
All30 physical A/B/A2 attempts retained and PCM exact; no observation errors.
CPU192 medians88.144 /103.633 /88.119%, 17.57–17.61% slower. Rejected/OFF.
CPU128 medians77.384 /86.881 /77.354%. Minimum sampled DRAM8168B across
series, minimum free stack1660B; maxima/all lower rates in comparison.json.

Full suite log:183 tests,168 pass,7 fail,8 skip. One stale diagnostic API
harness subsequently fixed and passes separately. Six evidence/setup
failures remain listed in docs/ESP8266_OPUS_ASM_SMALL_DIV_TAIL.md; no claim
of a green full suite. The target<=70% and live I2S qualification remain unmet.

Final targeted suite including archive integrity and repaired API harness:
29 passed,0 failed,0 skipped; final-targeted-regression.log retained.

Ordinary live512-idle3s firmware restored OTA to0x10000, stopped as initially.
Actual WS status/current and HTTP playlist verified; no UART/SPIFFS writes.
App/manifests,30 raw runs, build/test logs, linked proof and restore reports
are retained here. Control image: ../esp8266-opus-tail-control-v1/.
