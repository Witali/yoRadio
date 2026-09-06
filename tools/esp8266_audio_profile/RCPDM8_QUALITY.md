# Desktop RCPDM8 quality experiment

This is **RCPDM8**, not the ordinary PDM8 firmware profile initially inferred
from the request. Those temporary firmware edits were undone. All candidates
live in a host-only harness; production and the connected device are unchanged.

## Run

Requires Node.js, a C++17 compiler (MSVC on Windows), Python 3 and NumPy.
Uses saved mono PCM from the preceding real-radio benchmark, with SHA-256
validation. The radio files must still exist locally; no new broadcasts are
downloaded by this script.

```powershell
python tools/esp8266_audio_profile/measure_rcpdm8_quality.py
node --test tests/esp8266-rcpdm8-quality.test.js
python tests/rcpdm8_quality_model_test.py
```

Use `--capture` / `--output` to choose directories. Default output is the
ignored `radio_output/rcpdm8-quality/`: packed bits, metadata, synthetic PCM,
2-second listening WAVs, and a compiled desktop executable. Radio excerpts
are not added to Git. Synthetic test signals are generated deterministically.

## Variants

At 48-kHz mono PCM, eight bits/sample means 384 kbit/s; 32 means 1.536 Mbit/s.
The input remains signed 16-bit PCM, and state is carried across samples.

| Name | Algorithm | Bits/sample | Alpha |
| --- | --- | ---: | --- |
| pdm8 | Ordinary first-order accumulator PDM | 8 | n/a |
| pdm32 | Actual extracted firmware packer | 32 | n/a |
| rc8-a16 | RCPDM8, original coefficient | 8 | 1/16 |
| rc8-a4 | RCPDM8, larger step at lower clock | 8 | 1/4 |
| rc8-matched | RCPDM8, matched to a 10-us RC at 384 kHz | 8 | 15025/65536 |
| rc32 | Actual production RCPDM32 header | 32 | 1/16 |

`rc8-matched` uses 64-bit Q16 products, only as a quality control; it is not
claimed to be a fast implementation for LX106. Shift variants use 32-bit
arithmetic. Both are checked against independent two-candidate references.
Four calls to rc8-a16 on the same held input, concatenated, must equal rc32
exactly. Thus a 1.536-MHz stream with four new 8-bit groups per original
sample still needs 32 decisions. Merely repeating each bit four times is the
same waveform as a 384-kHz stream, not a higher-quality modulator.

## Measurement model

All waveforms are represented on a **common** 1.536-MHz grid. A PDM8/RCPDM8
bit is held for four grid intervals, not recomputed or interpolated. All
32-bit files contain little-endian numeric words, chronological MSB first;
8-bit files contain one chronological MSB-first byte per sample.

One-second periodic Hann windows, no overlap, at least 250ms omitted at each
clip edge. The analysis band is 20 Hz–20 kHz. The continuous-time zero-order
hold aperture is included. Identical physical transfer functions are used
for every algorithm, without aligning gain or phase to improve the scores:

- `rc10us`: `H(s)=1/(1+s*10us)`, for example 1k/10nF, high-impedance load.
- `rc40us`: `H(s)=1/(1+s*40us)`, a narrower comparison filter.
- `ladder10us`: two **unbuffered** equal 1k/10nF RC sections,
  `H(s)=1/(1+3*s*10us+(s*10us)^2)`, high-impedance output load.

This is a stationary/windowed **spectral** filter model, not a transient SPICE
simulation or a recording of the actual GPIO, amplifier and RC components.
The +0.16% physical I2S divider error, component tolerance, GPIO edge noise,
DMA gaps, UART loading, loudspeaker and codec errors are not simulated.

Two radio-error metrics are saved deliberately:

- `snr_to_input_db`: output vs the original held PCM; includes RC gain/phase.
- `snr_to_ideal_rc_db`: output vs ideal PCM through the same RC; isolates
  deviation from that DAC+filter reference, but can penalize RCPDM's attempted
  RC compensation. Do **not** use this metric alone to rank total fidelity.

Tone SINAD separates the fundamental (central bin plus the Hann neighbours)
from all other in-band energy. THD and fundamental gain are saved separately.
No dither or noise is added. A vanished tone has `tone_detected=false` and
null SINAD; ratios of FFT roundoff must not be reported as meaningful quality.
An exact constant `0xaa`/`0x55` (or its 32-bit counterpart) is also detected.

WAV previews use one 10-us RC plus an ideal 20-kHz low-pass, a common gain of
0.7 and a 10ms edge fade. No per-file normalization; clipping is a fatal error.
FFT boundary effects mean these are preview simulations, not hardware captures.
