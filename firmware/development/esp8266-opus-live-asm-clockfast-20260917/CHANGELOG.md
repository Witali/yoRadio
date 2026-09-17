# Exact I2S clock compensation — 2026-09-17

Source24243cc0,889712 bytes, all18 accepted ASM stages rebased and proved.
CPU160/QIO40, I2S PDM32 GPIO3, app-task PCM2x960, DMA128/input2048,
scratch6144/reserve4096, LED OFF, RX14, TCP536/window2440/OOSEQ ON.
Adds8 static bytes for48k->48076.923 rational linear interpolation.
No new task or PCM buffer. This is ordinary radio with diagnostics,
not a synthetic playback benchmark. OTA PASS.

All14 host direct-output configurations passed (five DMA sizes with/without
clock compensation and four other output modes). Independent64-bit timing
oracle agrees with every PDM word. Exact division tested for all40893841
possible magnitudes. Target object contains no __divsi3/__divdi3/__muldi3.
All21 saved-image identity tests passed, no skips.

**Live result:NOT qualified.** Kultur24 window1 crossed a TCP idle timeout
and reconnect (3149 underruns,22.143s PCM/28.005s). Window2 was stable but
had263 underruns,27.749s PCM/28.018s. DLF24 then had643 underruns and
27.240s PCM/28.017s. Queue error stayed0; active heap snapshots6312..7320B.
Read/input-wait intervals account for many misses. Wall profile times
include preemption/queue blocking and must not be reported as CPU load.

Compensation corrects the mathematical nominal-clock mismatch but these
trials do not show a playback improvement. It remains OFF by default.
No acoustic verification. The earlier unflashed `clock` image used compiler
division and was superseded before physical testing.

Private recorded DLF24 host check:873 packets/52.38s, scratch2904B,
word arena15600B, no decode-time allocations or guard errors. Only report
hashes/statistics are retained; no station recording is published here.
