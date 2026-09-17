# Diagnostic accepted ASM + PCM queue + standard TCP — 2026-09-17

All18 accepted hot ASM stages, C leased-PCM packet dispatcher.
Same PCM pool, DMA256, stacks and memory guards as `pcmqueue-20260917`.
Restores the normal SDK TCP out-of-order queue; the low-RAM OOSEQ-OFF trial
did not establish reliable live reception. No board-default change.
I2S PDM32 GPIO3, CPU160/QIO40, Opus input1024B/scratch6144B/reserve4096B.
No raw benchmark or tone generator. App889648B; SHA256:
`ff5650f1d4762e764df4b8b6253f1caf21e3e1e58aadfd71a28c17ce4483b120`.

Six offline image/provenance tests pass, including all accepted instruction
graphs and exact loaded sections. Board results are retained separately;
a successful OTA or Playing status alone is not continuous-output proof.
