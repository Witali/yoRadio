# Playback checkpoint — 2026-09-18

Later follow-up: see ESP8266_LOCAL_RADIO_2026-09-18.md. A LAN-only station
reproduced underruns and scratch-allocation failures. No firmware change;
the board was left stopped after that experiment, not playing Kultur.

Stopped at the user's explicit save-and-shutdown request, without pushing.
Branch:codex/esp8266-opus-asm, worktree:.worktree/esp8266-opus-asm.

## Actual result

Normal uninterrupted Opus radio playback has NOT been achieved. All accepted
18 ASM optimizations are included in the physical ordinary-radio trials
(diagnostics enabled; not a decoder benchmark). No zero-underrun real-station
window has qualified. No acoustic recording/listening evidence is available.

Kultur low-rate24kb/s with read-ahead recovery and two PCM slots:
independent25s board windows without HTTP sampling had8 and9 underruns.
Adding rational clock compensation gave22 underruns/25.001s; not a fix.
Preserve these failures. Wall timing is not CPU utilization.

## Saved work

- Rebuffering preserves decoder/TCP/Ogg state after confirmed starvation.
- Autonomous continuity measurement uses48 static bytes and no extra task.
- Rebuffer/quiet/quietclock binaries, manifests, ASM proofs, OTA and live
  results are saved under firmware/development/esp8266-opus-live-asm-*-20260917.
- Third PCM slot is opt-in, default remains two. Eight ASan/UBSan queue tests
  passed. This new slot option has NOT been target-built or board-tested.
- Commits859d1936 and49141325 retain measurements and the slot implementation.

## Board left running

192.168.100.6, OTA slot0x110000, quietclock image890272B. Temporary Kultur24
URL selected through diagnostic API; playlist and Wi-Fi files unchanged.
I2S PDM32 onGPIO3/RX, CPU160/QIO40, two960-sample PCM slots, DMA128,
input2048, scratch6144, reserve4096, LED disabled. All18 ASM stages retained.
No serial reset or UART commands were used. Continue deploying over OTA.

## Next steps (not executed)

1. Compile the third-slot experiment with input1024, DMA128, unchanged4096B
   reserve and existing app consumer. Test ownership/heap and all18 ASM proofs.
2. Compare autonomous windows, then playback while using WebUI; retain every
   failed start/reconnect. Do not accept a single lucky window as reliability.
3. If successful, repeat station starts/switches and only then qualify an
   ordinary production profile. Do not promote the present trials by default.

Build intermediates remain local and untracked. Three unrelated user files
flash_clock_diag.c/.h and web_flash_clock_diag.inc were preserved unstaged.
No further testing, pushing or shutdown should be inferred from this file;
resume only in response to a new user request.
