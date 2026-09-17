# Diagnostic accepted ASM + PCM queue + DMA128 — 2026-09-17

All18 accepted hot ASM stages, C leased-PCM dispatcher, standard TCP OOSEQ.
Two128-word DMA descriptors save1024B versus the DMA256 queue profile.
PCM pool remains two960-sample slots; consumer stack1536B, audio stack5120B,
Opus input1024B, scratch6144B, reserve4096B unchanged. CPU160/QIO40,
I2S PDM32 GPIO3. Default board configuration is unchanged.

App889648B; SHA256:
`d5af3a7ebac578531d0d2eff2d274de7b200f0f55fc349fbd98243d4bf8dc985`.
Seven offline image/provenance checks pass, plus six DMA/PDM/config tests.
Direct-writer tests include DMA128 bit equality and EOF/ownership races.
Smaller DMA requires more frequent service (nominal2.67ms per full block);
live qualification, not allocation alone, determines whether it is useful.

Target GCC stack audit: individual frames64B queue,144B output,16B normalizer
wrapper,64B normalizer,80B DMA. These are NOT summed call-chain/ISR bounds.
The main audio stack and reserve guard have not been reduced.
