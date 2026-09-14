# Experimental exact small division — 2026-09-14

Best tell-inline ASM plus three rng/ft call sites using a leaf LX106 helper.
Four unsigned 16x16 products form exact high32; corrected reciprocal division,
same Xiph table, original __udivsi3 fallback. No bitrate cap or approximate PCM.

CPU160/QIO40, diagnostic raw RAM benchmark; no audio output/function profiler.
App 903856 bytes (+640); helper114 bytes, table516 bytes. No static RAM/stack
growth. See manifest.json for app/recipe hashes and exact build options.
20 regressions pass; host exact PCM through510kbps and PLC/reset/OOM.
Linked helper/table and three call sites verified. Physical A/B/A completed:
10 A /10 B /10 A2, CPU192 medians 88.132 /93.804 /88.197%.
Candidate takes 6.36-6.44% more time; not selected. All PCM hashes match.
All attempts retained, including B/run5 observation timeout, 1044B min DRAM,
107.177% CPU192. Static RAM/scratch unchanged; stack free minimum1660B.
The <=70% goal remains unmet. Restored the original ordinary radio by OTA;
status/WS/playlist checked, initial stopped state preserved, no UART/SPIFFS writes.
This is not the production default or live audio qualification.

See docs/ESP8266_OPUS_ASM_SMALL_DIV.md and preflight.json.
