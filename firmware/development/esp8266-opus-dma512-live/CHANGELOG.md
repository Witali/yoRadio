# Diagnostic live Opus DMA512 control

2026-09-11, source b77b61c, app885520B, CPU160/QIO40. C rotation, word/ICDF/FIR
helpers, PDM32 batch/IRAM, SDK RX diagnostic. GPIO3, two512-word DMA buffers.
Input1024B, scratch6144B. PCM publication OFF. No pure-codec benchmark.
Matched DMA768 differs only by DMA capacity. Target sections/ISR archived in
target-evidence.json. DRAM BSS18520B; IRAM text22848B, ISR387B.
Not a release; continuity and memory safety still require physical testing.

OTA confirmed after the768/3s series. Physical qualification:0/10, all raw
attempts retained. Startup showed playing in5/9 available status responses.
First full window:28.219s elapsed,26.960s PCM,1046 new DMA underruns. Later
errors include Decoder Init Error and HTTP response timeouts. Lifetime heap
minimum eventually3124B, not a per-window value. Not continuous/qualified.
