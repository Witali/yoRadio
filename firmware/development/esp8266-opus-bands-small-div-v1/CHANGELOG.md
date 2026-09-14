# Experimental exact small division — 2026-09-14

Best tell-inline ASM plus three rng/ft call sites using a leaf LX106 helper.
Four unsigned 16x16 products form exact high32; corrected reciprocal division,
same Xiph table, original __udivsi3 fallback. No bitrate cap or approximate PCM.

CPU160/QIO40, diagnostic raw RAM benchmark; no audio output/function profiler.
App 903856 bytes (+640); helper114 bytes, table516 bytes. No static RAM/stack
growth. See manifest.json for app/recipe hashes and exact build options.
20 regressions pass; host exact PCM through510kbps and PLC/reset/OOM.
Linked helper/table and three call sites verified. Physical speed pending.
This is not the production default or live audio qualification.

See docs/ESP8266_OPUS_ASM_SMALL_DIV.md and preflight.json.
