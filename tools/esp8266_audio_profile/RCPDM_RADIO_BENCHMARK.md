# Desktop RCPDM benchmark using real radio PCM

This is an offline **modulator** experiment, not an ESP8266 firmware or decoder
benchmark. It does not contact the board, change Wi-Fi, or use a serial port.
The production `rc_pdm.h` is the control, with the frozen pre-optimization
implementation as an additional exactness oracle.

## Reproduce

Requires Node.js, FFmpeg/ffprobe and a C++17 compiler (MSVC on Windows, `c++`
elsewhere). The binary file format requires a little-endian host.

```powershell
# Network capture: five sources, about 12 seconds each. Use a fresh directory.
node tools/esp8266_audio_profile/capture_rcpdm_radio.js radio_output/my-rcpdm-capture
# Offline: decode was saved during capture; no network access is needed here.
node tools/esp8266_audio_profile/run_rcpdm_radio.js radio_output/my-rcpdm-capture radio_output/my-rcpdm-capture/run-1
# Independent regression, generated input only; no live station required.
node --test tests/esp8266-rcpdm-radio.test.js
```

The capture manifest records source URLs, times, FFmpeg version, probe output,
warnings and SHA-256 of both the compressed clip and decoded PCM. Actual audio
is kept under the already ignored `radio_output/`: broadcast snippets are not
licensed for redistribution and are not committed to Git. Keep this directory
to repeat the **same** experiment. Capturing again records different content.
Measurements and hashes, but not broadcast audio, may be archived in docs.

## Audio path and exactness

FFmpeg decodes MP3/AAC to signed 16-bit PCM at the native rate and channel count.
The desktop program reproduces the firmware's Q15 volume (254/128/64), neutral
balance, integer stereo average toward zero, and zero-order hold resampling to
48 kHz. Normalization is disabled. Decode/gain/resampling are outside timing.
This does not claim to exercise the Helix decoder, enabled normalization,
physical RC-filter response or analog output quality.

One output word contains 32 chronological bits, MSB first. `.rcpdm32le` stores
each numeric word little-endian, like a DMA word on the target. It is **not**
a bytewise MSB-first transport dump; unpack words before viewing individual
bits. `.mono48.s16le` contains the exact mono input to the modulator.

Each candidate must match every original word and RC state after every sample;
uninstrumented bulk output is also compared. A mismatch fails the process.
Identical bits mean zero **additional** distortion, not distortion-free analog
audio. Difference SNR is infinite when streams are identical; no absolute SNR
or THD for a real RC filter is inferred.

## Candidates and counters

- `fixed2/4/8`: conservative `abs(T-S) >= N*STEP-HALF` guard at each opportunity.
- `state2/4/8`: tighter state-dependent sufficient bound, at each opportunity.
- `entry-fixed4/entry-state4`: check only at the start of a PCM sample, retaining
  a first-step flag in the generic loop.
- `split-fixed4/split-state2/4/8`: check once, then branch to the unchanged
  production loop on a miss. The flag is removed from the bit loop.

All preserve each rounded RC update. For the state-dependent bound, define
`down=S-(S>>4)` and `limit=max(T-HALF,0)`. A high run is safe if
`limit>down && limit-down>(N-1)*(STEP-(S>>4))`. A low run is safe if
`down>=limit && down-limit>=(N-1)*(S>>4)`. Subsequent increments/decrements
toward a rail cannot grow. `down(S)` is monotone and 1-Lipschitz, so these bound
the last decision in the run. Ordered subtraction prevents unsigned overflow.

`groups` counts accepted groups; `highGroups` is the subset of ones.
`wordsWithGroup` counts PCM samples with at least one accepted group.
`coveredBitsPercent = 100 * groupSize * groups / (32 * samples)` is the fraction
of emitted bits, **not** the fraction of samples or successful checks.
The run histogram counts natural maximal same-bit runs, split at word
boundaries; natural runs need not pass a sufficient guard.

Seven timed rounds rotate candidate order. All outputs are preallocated; the
timed loop has no counters, I/O, allocation, decoder or resampler. A full
untimed pass warms each candidate. Record median/min/max and individual rounds;
repeat without concurrent tests or builds. Ratios are host-specific and do not
predict Xtensa LX106 timing, IRQ load, or I2S DMA performance.
