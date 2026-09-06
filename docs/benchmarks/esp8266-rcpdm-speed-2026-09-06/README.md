# RCPDM32 speed optimization — physical measurements, 2026-09-06

Full explanation and acceptance decisions:
[ESP8266_RCPDM_SPEED_OPTIMIZATION.md](../../ESP8266_RCPDM_SPEED_OPTIMIZATION.md).

- `matrix/`: one physical run of each independent scalar candidate.
- `final-ab/`: two runs each of original, threshold-only and the first
  (rejected) generic batch. Kept to explain the GCC register-pressure regression.
- `specialized-ab/`: two runs each of threshold-only and the accepted batch.
- `host-specialized.log`: 16 output/RC/direct-DMA tests passed.
- `summary.json`: parsed raw measurements, rejecting invalid timers/mismatches.

All runs: Wemos D1 mini COM8, CPU160/QIO40, generated stereo 48-kHz PCM,
volume64/normalization OFF in RAM only, two 512-word DMA buffers, no Wi-Fi
or decoder. Atomic diagnostic timestamp reads; 2 s warmup + 10 s measurement.
No bit/state mismatches, no underruns/partial handoffs/FIFO empty.

| Variant | Scalar pack, us/48000 words | Producer excluding DMA wait, us/audio second |
| --- | ---: | ---: |
| original | 119216 | 158586 |
| limit / production-no-batch | 112275 | 149798 |
| unroll4 / unroll8 | 108560 | 150841 |
| unroll32 | 108710 | 150930 |
| mask8 | 114233 | 157273 |
| branchless8 | 126454 | 166421 |
| generic batch (production) | 112275 | 160155 |
| specialized batch (accepted) | 112273 | 124764 |

The complete producer result, not just the isolated scalar kernel, decides
acceptance. This is not total CPU utilization or an analog SNR/THD measurement.
The batch fast path is only for 48-kHz input with zero resampler remainder;
other rates retain the scalar resampler and benefit from the hoisted threshold.

To reproduce scalar candidates and accepted production (requires the repository
ESP8266 SDK/tool installation; verify board/COM port and reduce amplifier volume):

```powershell
./tools/esp8266_audio_profile/build_rcpdm_speed.ps1
./tools/esp8266_audio_profile/run_rcpdm_speed.ps1
./tools/esp8266_audio_profile/build_rcpdm_speed.ps1 -Variants production -DisableBatch
./tools/esp8266_audio_profile/build_rcpdm_speed.ps1 -Variants production
./tools/esp8266_audio_profile/run_rcpdm_speed.ps1 -Variants production-no-batch,production -Repeats 2
./tools/esp8266_audio_profile/build_rcpdm_speed.ps1 -Variants production -Radio
node tools/esp8266_audio_profile/summarize_rcpdm_speed.js docs/benchmarks/esp8266-rcpdm-speed-2026-09-06/matrix docs/benchmarks/esp8266-rcpdm-speed-2026-09-06/final-ab docs/benchmarks/esp8266-rcpdm-speed-2026-09-06/specialized-ab
```

The current production implementation is the final specialized batch, not
the rejected generic batch formerly built under the `production` artifact name.
Use archived binaries and their hashes for the exact historical matrix.
The frozen scalar candidates stay in `tests/native/rcpdm_variants.h`.

The ordinary PDM32 radio was restored at the end (SHA256
`E10B739E9BDDEA684E657DAA77274C397FAE323FD908A6D78CAB07E07C0AB874`).
UART confirmed CPU160, PDM32, station1/volume254, SPIFFS93623/233681 B,
and DHCP address 192.168.100.6. WebUI/live radio sound was not retested here.
