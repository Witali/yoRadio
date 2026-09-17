# Diagnostic accepted ASM + PCM queue — 2026-09-17

All18 accepted hot ASM stages; the existing packet dispatcher is compiled from
C to enable per-coded-frame PCM leases. No arithmetic or state-ABI change.
I2S PDM32 GPIO3, CPU160/QIO40; two960-sample PCM slots, two256-word DMA buffers,
1536B consumer stack,5120B audio stack. Input1024B; scratch6144B/reserve4096B.
TCP OOSEQ OFF. App887504B; exact SHA256 and flags are in manifest.json.
No raw benchmark, tone generator or function profiler.

12 host cases match pristine generic32 PCM exactly, including the real24kbps
Hybrid capture. Concurrent ownership/Stop/failure tests pass under ASan/UBSan.
All loaded sections and18 accepted instruction graphs verified in preflight.json.
Not a production default; live qualification must establish continuous output.
