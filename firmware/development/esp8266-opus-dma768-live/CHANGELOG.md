# Diagnostic live Opus DMA768 candidate

2026-09-11, source b77b61c, app885536B. Matches DMA512 except two768-word
DMA buffers:2048B additional static DRAM, total buffer capacity32ms at48kHz.
DRAM BSS20568B; IRAM text22848B, ISR387B. ISR hash differs due to capacity/
addresses; equal size is not proof of identical timing. App is16B larger.
C rotation and unchanged exact PDM32; GPIO3. Guarded decoder reserve retained.
User approved768-word experiment. Production default remains512 pending tests.
Initial OTA prerequisite status query timed out before upload; retained ota.json.
Subsequent old-firmware failure snapshot records receive timeout116 and decoder
reserve rejection (stage10, free3672<4096), not proof of a leak. Network recovered
without serial reset; application-only OTA attempted as ota-retry1.json.

OTA retry confirmed successful. Physical qualification:0/10; failed starts,
unavailable status responses and all traces retained. Observed lifetime heap
minimum3080B. No valid continuous20s interval; do not promote this DMA increase.
Independent PC arrival probe is retained as network context, not ESP evidence.
